
# pages/page2.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Visualisasi Data", page_icon="📊", layout="wide")
st.title("📊 Visualisasi Data Kekerasan Seksual terhadap Perempuan")

# --- 1) Ambil data: prioritas session, lalu file lokal (root atau pages/) ---
df = None
if "data" in st.session_state:
    df = st.session_state["data"]
else:
    for candidate in ["data_kekerasan_perempuan.csv", "pages/data_kekerasan_perempuan.csv"]:
        if os.path.exists(candidate):
            try:
                df = pd.read_csv(candidate)
                st.info(f"Membaca data dari file lokal: {candidate}")
                st.session_state["data"] = df
                break
            except Exception:
                try:
                    df = pd.read_excel(candidate)
                    st.info(f"Membaca Excel dari: {candidate}")
                    st.session_state["data"] = df
                    break
                except Exception:
                    df = None

# Jika belum ada data, tampilkan uploader minimal
if df is None:
    uploaded = st.file_uploader("", type=["csv","xlsx"], label_visibility="collapsed")
    if uploaded:
        try:
            # simpan sementara ke disk agar bisa dipakai fallback
            try:
                with open(uploaded.name, "wb") as f:
                    f.write(uploaded.getbuffer())
            except Exception:
                pass
            if uploaded.name.lower().endswith(".xlsx"):
                df = pd.read_excel(uploaded)
            else:
                df = pd.read_csv(uploaded)
            st.session_state["data"] = df
            st.success("Data berhasil diupload dan disimpan ke session.")
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
            st.stop()
    else:
        st.warning("Data belum tersedia. Silakan unggah file CSV/Excel (kotak upload di atas).")
        st.stop()

# --- 2) Tampilkan kolom asli supaya jelas ---
st.markdown("**Kolom asli di file:**")
st.write(df.columns.tolist())

# --- 3) Bersihkan data wide menjadi long jika perlu ---
# Heuristik: ada kolom bernama 'cakupan' atau 'provinsi' atau 'Cakupan'
cols_lower = [c.lower() for c in df.columns]
prov_col = None
for candidate in ["cakupan", "provinsi", "prov", "nama provinsi", "region"]:
    if candidate in cols_lower:
        prov_col = df.columns[cols_lower.index(candidate)]
        break

# Jika tidak ada prov_col, coba kolom kedua (bila format sama seperti screenshot: kolom B)
if prov_col is None:
    # ambil kolom non-numeric pertama sebagai provinsi
    non_num = df.select_dtypes(exclude="number").columns.tolist()
    if non_num:
        prov_col = non_num[0]

# Hapus kolom yang bukan jenis: mis. 'No', 'Satuan' dll.
exclude_names = ["no", "satuan", prov_col]
numeric_candidates = []
for c in df.columns:
    if c not in (exclude_names if exclude_names else []):
        # anggap numeric jika dtype numeric atau seluruh nilai bisa dikonversi ke angka
        try:
            pd.to_numeric(df[c].dropna().astype(str).str.replace(",", "").str.strip(), errors="raise")
            numeric_candidates.append(c)
        except Exception:
            # bukan numeric
            pass

# Jika numeric_candidates lebih dari 0 -> kemungkinan wide format
if len(numeric_candidates) >= 1:
    st.info("Terlihat dataset wide: kolom jenis kekerasan terdeteksi. Mengkonversi ke format long...")
    # Buang baris total jika ada (misal 'INDONESIA' atau baris yang memiliki string 'INDONESIA' di prov_col)
    if prov_col in df.columns:
        df = df[~df[prov_col].astype(str).str.strip().str.upper().eq("INDONESIA")]
        # juga hilangkan baris yang hanya berisi 'No' atau header berulang
        df = df[~df[prov_col].astype(str).str.strip().str.lower().isin(["no", ""])]
    # lakukan melt
    id_vars = [prov_col] if prov_col else []
    df_long = df.melt(id_vars=id_vars, value_vars=numeric_candidates,
                      var_name="Jenis", value_name="Jumlah")
    # bersihkan nama kolom
    if prov_col:
        df_long = df_long.rename(columns={prov_col: "Provinsi"})
    else:
        df_long = df_long.rename(columns={id_vars[0]: "Provinsi"} if id_vars else {"variable": "Provinsi"})
    # bersihkan nilai jumlah (hapus koma, spasi)
    df_long["Jumlah"] = pd.to_numeric(df_long["Jumlah"].astype(str).str.replace(",", "").str.strip(), errors="coerce")
    # tambahkan kolom Tahun (default 2024) — beri pilihan kepada user
    tahun_default = 2024
    tahun_input = st.number_input("Tahun untuk data ini (jika semua 2024, biarkan saja)", value=tahun_default, step=1)
    df_long["Tahun"] = int(tahun_input)
    # simpan kembali sebagai df yang dipakai pipeline
    df = df_long.copy()
    st.markdown("Contoh data setelah konversi ke long (5 baris):")
    st.dataframe(df.head())
else:
    st.info("Dataset tampak sudah dalam format long atau tidak ada kolom numerik yang terdeteksi sebagai jenis kekerasan.")
    # pastikan minimal punya kolom Provinsi, Jenis, Jumlah
    # coba rename otomatis jika kolom ada
    possible_prov = prov_col if prov_col in df.columns else None
    if possible_prov and "Provinsi" not in df.columns:
        df = df.rename(columns={possible_prov: "Provinsi"})
    # coba normalisasi kolom jumlah (cari nama 'jumlah' atau 'kasus')
    for candidate in df.columns:
        if any(k in candidate.lower() for k in ["jumlah", "kasus", "total", "nilai"]):
            if candidate != "Jumlah":
                df = df.rename(columns={candidate: "Jumlah"})
            break
    # coba cari kolom jenis
    if "Jenis" not in df.columns:
        # take first non-numeric column that is not prov
        candidates = [c for c in df.columns if c not in (possible_prov, "Jumlah") and df[c].dtype == object]
        if candidates:
            df = df.rename(columns={candidates[0]: "Jenis"})

# Simpan final ke session
st.session_state["data"] = df

# --- 4) Deteksi kolom pipeline dan tampilkan hasil deteksi ---
def find_col(columns, keywords):
    for kw in keywords:
        for c in columns:
            if kw.lower() in c.lower():
                return c
    return None

cols_now = df.columns.tolist()
col_tahun = find_col(cols_now, ["tahun", "year"])
col_prov = find_col(cols_now, ["provinsi", "prov", "cakupan", "province"])
col_jumlah = find_col(cols_now, ["jumlah", "kasus", "total", "count", "nilai"])
col_jenis = find_col(cols_now, ["jenis", "kekerasan", "kategori", "type"])

st.markdown("**Kolom terdeteksi (setelah pra-pemrosesan):**")
st.write({"tahun": col_tahun, "provinsi": col_prov, "jumlah": col_jumlah, "jenis": col_jenis})

# --- 5) Filter UI ---
st.markdown("---")
st.subheader("Filter Data")

prov_options = sorted(df[col_prov].dropna().astype(str).unique().tolist()) if col_prov else []
jenis_options = sorted(df[col_jenis].dropna().astype(str).unique().tolist()) if col_jenis else []

prov_selected = st.multiselect("Pilih provinsi (kosong = semua)", options=prov_options)
jenis_selected = st.multiselect("Pilih jenis kekerasan (kosong = semua)", options=jenis_options)

# Tahun filter
if col_tahun:
    year_min = int(df[col_tahun].min())
    year_max = int(df[col_tahun].max())
    tahun_range = st.slider("Rentang Tahun", min_value=year_min, max_value=year_max, value=(year_min, year_max))
else:
    tahun_range = None

if st.button("Terapkan filter"):
    st.experimental_rerun()

# Terapkan filter
filtered = df.copy()
if prov_selected and col_prov:
    filtered = filtered[filtered[col_prov].astype(str).isin(prov_selected)]
if jenis_selected and col_jenis:
    filtered = filtered[filtered[col_jenis].astype(str).isin(jenis_selected)]
if tahun_range and col_tahun:
    filtered = filtered[(filtered[col_tahun] >= tahun_range[0]) & (filtered[col_tahun] <= tahun_range[1])]

if filtered.empty:
    st.warning("Hasil filter kosong. Coba opsi filter lain.")
    st.stop()

# --- 6) Preview & download ---
st.markdown("---")
st.subheader("Preview Data (hasil filter)")
st.dataframe(filtered, use_container_width=True)
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV hasil filter", data=csv, file_name="data_kekerasan_filtered.csv", mime="text/csv")

# --- 7) Visualisasi sederhana ---
st.markdown("---")
st.subheader("Visualisasi")

chart_type = st.selectbox("Pilih jenis grafik", options=[
    "Bar Chart (Per Provinsi untuk Jenis terpilih)",
    "Stacked Bar (Per Provinsi, semua jenis)",
    "Pie Chart (Distribusi jenis, diseluruh pilihan)"
])

if chart_type == "Bar Chart (Per Provinsi untuk Jenis terpilih)":
    if not col_jenis or not col_prov or not col_jumlah:
        st.error("Butuh kolom Provinsi, Jenis, dan Jumlah untuk membuat grafik ini.")
    else:
        # pilih satu jenis
        jenis_ = st.selectbox("Pilih jenis untuk bar chart", options=jenis_options)
        df_plot = filtered[filtered[col_jenis] == jenis_].groupby(col_prov)[col_jumlah].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10,5))
        ax.bar(df_plot.index.astype(str), df_plot.values)
        ax.set_xlabel("Provinsi")
        ax.set_ylabel("Jumlah Kasus")
        ax.set_title(f"Jumlah kasus jenis '{jenis_}' per Provinsi")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

elif chart_type == "Stacked Bar (Per Provinsi, semua jenis)":
    if not col_prov or not col_jenis or not col_jumlah:
        st.error("Butuh kolom Provinsi, Jenis, dan Jumlah untuk stacked bar.")
    else:
        df_stack = filtered.groupby([col_prov, col_jenis])[col_jumlah].sum().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(12,6))
        df_stack.plot(kind="bar", stacked=True, ax=ax)
        ax.set_xlabel("Provinsi")
        ax.set_ylabel("Jumlah Kasus")
        ax.set_title("Jumlah Kasus per Provinsi menurut Jenis (Stacked)")
        plt.xticks(rotation=45)
        st.pyplot(fig)

elif chart_type == "Pie Chart (Distribusi jenis, diseluruh pilihan)":
    if not col_jenis or not col_jumlah:
        st.error("Butuh kolom Jenis dan Jumlah untuk pie chart.")
    else:
        dist = filtered.groupby(col_jenis)[col_jumlah].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(7,7))
        ax.pie(dist.values, labels=dist.index.astype(str), autopct="%1.1f%%")
        ax.set_title("Distribusi jenis kekerasan (dari data saat ini)")
        st.pyplot(fig)

# --- 8) Statistik ringkas ---
st.markdown("---")
st.subheader("Statistik Ringkas")
try:
    st.write(filtered.select_dtypes(include="number").describe().T)
except Exception:
    st.write("Tidak ada kolom numerik untuk dihitung statistik.")



