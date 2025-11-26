
# pages/page2.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Visualisasi Data", page_icon="📊", layout="wide")

st.title("📊 Visualisasi Data Kekerasan Seksual terhadap Perempuan")

# --- 1) Dapatkan dataframe: prioritas session_state, lalu file lokal (root atau pages/) ---
df = None
if "data" in st.session_state:
    df = st.session_state["data"]
else:
    # coba fallback: cari file di root atau di pages/
    for candidate in ["data_kekerasan_perempuan.csv", "pages/data_kekerasan_perempuan.csv"]:
        if os.path.exists(candidate):
            try:
                df = pd.read_csv(candidate)
                st.info(f"Membaca data dari file lokal: {candidate}")
                st.session_state["data"] = df
                break
            except Exception:
                # coba pakai read_excel jika csv gagal (just in case)
                try:
                    df = pd.read_excel(candidate)
                    st.info(f"Membaca data Excel dari: {candidate}")
                    st.session_state["data"] = df
                    break
                except Exception:
                    df = None

# Jika masih tidak ada, tampilkan uploader minimal (tidak jadi judul)
if df is None:
    uploaded = st.file_uploader("", type=["csv", "xlsx"], label_visibility="collapsed")
    if uploaded:
        try:
            # simpan sementara ke disk (memudahkan debugging/persistent)
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
        st.warning("Data belum tersedia. Silakan upload file CSV/Excel (di kotak atas).")
        st.stop()

# --- 2) Normalisasi kolom: temukan kolom tahun, provinsi, jumlah, jenis (case-insensitive, substring) ---
def find_col(columns, keywords):
    cols_low = [c.lower() for c in columns]
    for kw in keywords:
        for i, col in enumerate(cols_low):
            if kw.lower() in col:
                return columns[i]
    return None

cols = df.columns.tolist()
col_tahun = find_col(cols, ["tahun", "year"])
col_prov = find_col(cols, ["provinsi", "province", "propinsi", "region"])
col_jumlah = find_col(cols, ["jumlah", "kasus", "total", "count", "nilai"])
col_jenis = find_col(cols, ["jenis", "kekerasan", "kategori", "type"])

# Pastikan kolom jumlah dan tahun numeric bila ada
if col_jumlah:
    df[col_jumlah] = pd.to_numeric(df[col_jumlah], errors="coerce")
if col_tahun:
    df[col_tahun] = pd.to_numeric(df[col_tahun], errors="coerce")

# Debug kecil (tampilkan kolom terdeteksi)
st.write("Kolom terdeteksi:", {"tahun": col_tahun, "provinsi": col_prov, "jumlah": col_jumlah, "jenis": col_jenis})

# --- 3) UI Filter ---
st.markdown("---")
st.subheader("Filter Data")

# provinsi options
if col_prov:
    prov_options = sorted(df[col_prov].dropna().astype(str).unique().tolist())
else:
    prov_options = []

prov_selected = st.multiselect("Pilih provinsi (kosong = semua)", options=prov_options)

# tahun range
if col_tahun:
    year_min = int(df[col_tahun].dropna().min())
    year_max = int(df[col_tahun].dropna().max())
    tahun_range = st.slider("Rentang Tahun", min_value=year_min, max_value=year_max, value=(year_min, year_max))
else:
    tahun_range = None

# jenis
if col_jenis:
    jenis_options = sorted(df[col_jenis].dropna().astype(str).unique().tolist())
else:
    jenis_options = []
jenis_selected = st.multiselect("Pilih jenis kekerasan (kosong = semua)", options=jenis_options)

# tombol terapkan (opsional)
if st.button("Terapkan filter"):
    st.experimental_rerun()

# --- 4) Terapkan filter ---
filtered = df.copy()
if prov_selected and col_prov:
    filtered = filtered[filtered[col_prov].astype(str).isin(prov_selected)]
if tahun_range and col_tahun:
    filtered = filtered[(filtered[col_tahun] >= tahun_range[0]) & (filtered[col_tahun] <= tahun_range[1])]
if jenis_selected and col_jenis:
    filtered = filtered[filtered[col_jenis].astype(str).isin(jenis_selected)]

if filtered.empty:
    st.warning("Hasil filter kosong. Coba opsi filter lain.")
    st.stop()

# --- 5) Tampilkan tabel & download ---
st.markdown("---")
st.subheader("Preview Data (hasil filter)")
st.dataframe(filtered, use_container_width=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV hasil filter", data=csv, file_name="data_kekerasan_filtered.csv", mime="text/csv")

# --- 6) Visualisasi ---
st.markdown("---")
st.subheader("Visualisasi")

chart_type = st.selectbox("Pilih jenis grafik", options=[
    "Line Chart (Tren per Tahun)",
    "Bar Chart (Per Provinsi)",
    "Grouped Bar (Provinsi per Tahun)",
    "Stacked Bar (Per Tahun by Jenis)"])

# Line chart: total per tahun
if chart_type == "Line Chart (Tren per Tahun)":
    if not col_tahun or not col_jumlah:
        st.error("Butuh kolom Tahun dan Jumlah untuk membuat line chart.")
    else:
        agg = filtered.groupby(col_tahun)[col_jumlah].sum().reset_index().sort_values(col_tahun)
        fig, ax = plt.subplots(figsize=(9,4))
        ax.plot(agg[col_tahun], agg[col_jumlah], marker="o")
        ax.set_xlabel(col_tahun)
        ax.set_ylabel("Jumlah Kasus")
        ax.set_title("Tren Jumlah Kasus per Tahun")
        ax.grid(True)
        st.pyplot(fig)

# Bar chart: per provinsi (sum)
elif chart_type == "Bar Chart (Per Provinsi)":
    if not col_prov or not col_jumlah:
        st.error("Butuh kolom Provinsi dan Jumlah untuk bar chart.")
    else:
        agg = filtered.groupby(col_prov)[col_jumlah].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10,5))
        ax.bar(agg.index.astype(str), agg.values)
        ax.set_xlabel("Provinsi")
        ax.set_ylabel("Jumlah Kasus")
        ax.set_title("Jumlah Kasus per Provinsi")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

# Grouped bar (provinsi per tahun)
elif chart_type == "Grouped Bar (Provinsi per Tahun)":
    if not col_prov or not col_tahun or not col_jumlah:
        st.error("Butuh kolom Provinsi, Tahun, dan Jumlah untuk grouped bar.")
    else:
        # pilih beberapa provinsi (jika belum dipilih)
        sel_prov = prov_selected if prov_selected else prov_options[:6]
        df_group = filtered[filtered[col_prov].astype(str).isin(sel_prov)].groupby([col_tahun, col_prov])[col_jumlah].sum().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(12,5))
        df_group.plot(kind="bar", ax=ax)
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Jumlah Kasus")
        ax.set_title("Perbandingan Jumlah Kasus per Provinsi per Tahun")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# Stacked bar per tahun by jenis
elif chart_type == "Stacked Bar (Per Tahun by Jenis)":
    if not col_tahun or not col_jenis or not col_jumlah:
        st.error("Butuh kolom Tahun, Jenis, dan Jumlah untuk stacked bar.")
    else:
        df_stack = filtered.groupby([col_tahun, col_jenis])[col_jumlah].sum().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(12,5))
        df_stack.plot(kind="bar", stacked=True, ax=ax)
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Jumlah Kasus")
        ax.set_title("Jumlah Kasus per Tahun menurut Jenis Kekerasan (Stacked)")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# --- 7) Statistik ringkas ---
st.markdown("---")
st.subheader("Statistik Ringkas")
try:
    st.write(filtered.select_dtypes(include="number").describe().T)
except Exception:
    st.write("Tidak ada kolom numerik untuk dihitung statistik.")

st.info("Jika grafik tidak muncul, periksa apakah kolom 'Jumlah' terdeteksi sebagai numerik. Kamu bisa men-rename kolom di file CSV agar sesuai (mis: 'Jumlah' atau 'Kasus').")




