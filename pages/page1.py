# pages/page1.py (Home - menangani long & wide)
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Ulfa App - Home", page_icon="📊", layout="wide")

# Sidebar sederhana
with st.sidebar:
    st.title("Menu")
    st.write("📊 Visualisasi Data Kekerasan Seksual Tahun 2024")
    st.write("📰 Berita")
    st.write("⚠️ Tentang Kekerasan Seksual")
    st.markdown("---")
    st.write("Made by Ulfa 🎓")

# Header
st.title("⚠️ Kekerasan Seksual terhadap Perempuan — Tahun 2024")
st.write("Halaman ini menampilkan ringkasan data untuk **tahun 2024** berdasarkan file CSV yang kamu upload/simpan.")
st.markdown("---")

# ---------- ambil data ----------
df = None
if "data" in st.session_state:
    df = st.session_state["data"]
else:
    for f in ["data_kekerasan_perempuan.csv", "pages/data_kekerasan_perempuan.csv"]:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f)
                st.session_state["data"] = df
                st.info(f"Membaca data dari {f}")
                break
            except Exception:
                try:
                    df = pd.read_excel(f)
                    st.session_state["data"] = df
                    st.info(f"Membaca excel dari {f}")
                    break
                except Exception:
                    df = None

if df is None:
    st.warning("Data belum tersedia. Silakan upload CSV di halaman Visualisasi Data atau simpan file 'data_kekerasan_perempuan.csv' di folder project.")
    st.stop()

# ---------- normalize header ----------
df.columns = df.columns.str.strip()
cols = [c for c in df.columns]
st.write("Kolom yang tersedia:", cols)  # bantu debugging di layar

# ---------- deteksi format ----------
cols_lower = [c.lower() for c in df.columns]
is_long = ("jenis" in cols_lower and "jumlah" in cols_lower) or ("jenis" in cols_lower and any(k in cols_lower for k in ["kasus","jumlah","total"]))
# if long form present (Provinsi, Jenis, Jumlah)
if is_long:
    # cari nama kolom yang cocok
    def find_col(keywords):
        for k in keywords:
            for c in df.columns:
                if k.lower() in c.lower():
                    return c
        return None

    col_prov = find_col(["provinsi", "cakupan", "wilayah", "nama provinsi"])
    col_jenis = find_col(["jenis", "kekerasan", "kategori", "type"])
    col_jumlah = find_col(["jumlah", "kasus", "total", "count", "nilai"])
    col_tahun = find_col(["tahun", "year"])

    # pastikan semua ada
    if col_prov is None or col_jenis is None or col_jumlah is None:
        st.error("Format long terdeteksi tetapi tidak semua kolom penting ditemukan. Periksa header CSV (Provinsi, Jenis, Jumlah).")
        st.stop()

    # cast jumlah numeric
    df[col_jumlah] = pd.to_numeric(df[col_jumlah].astype(str).str.replace(",","").str.strip(), errors="coerce")

    # kalau tahun tidak ada, tambahkan default 2024
    if col_tahun is None:
        df["Tahun"] = 2024
        col_tahun = "Tahun"

    # gunakan df_long variable
    df_long = df[[col_prov, col_jenis, col_jumlah, col_tahun]].rename(columns={col_prov:"Provinsi", col_jenis:"Jenis", col_jumlah:"Jumlah", col_tahun:"Tahun"}).copy()

else:
    # asumsi wide: 1 baris = 1 provinsi, kolom jenis seperti Fisik, Psikis, Seksual, ...
    # deteksi provinsi kolom
    prov_candidates = ["cakupan","provinsi","prov","nama provinsi","wilayah"]
    prov_col = None
    for p in prov_candidates:
        if p in cols_lower:
            prov_col = df.columns[cols_lower.index(p)]
            break
    if prov_col is None:
        # fallback: first non-numeric column
        nonnum = df.select_dtypes(exclude="number").columns.tolist()
        prov_col = nonnum[0] if nonnum else None

    # numeric columns candidates (jenis)
    exclude = {prov_col, "no", "satuan"} if prov_col else {"no","satuan"}
    jenis_cols = []
    for c in df.columns:
        if c in exclude:
            continue
        try:
            pd.to_numeric(df[c].dropna().astype(str).str.replace(",","").str.strip(), errors="raise")
            jenis_cols.append(c)
        except Exception:
            pass

    if not jenis_cols:
        st.error("Format wide terdeteksi tetapi tidak ditemukan kolom jenis numeric. Pastikan kolom jenis seperti Fisik/Psikis/Seksual exist.")
        st.stop()

    # drop possible total row 'INDONESIA'
    if prov_col:
        df = df[~df[prov_col].astype(str).str.strip().str.upper().eq("INDONESIA")]

    # melt menjadi long
    id_vars = [prov_col] if prov_col else []
    df_long = df.melt(id_vars=id_vars, value_vars=jenis_cols, var_name="Jenis", value_name="Jumlah")
    if prov_col:
        df_long = df_long.rename(columns={prov_col:"Provinsi"})
    # tambah Tahun default jika tidak ada
    if not any(k in cols_lower for k in ["tahun","year"]):
        df_long["Tahun"] = 2024
    else:
        # jika ada kolom tahun, cari dan gunakan
        for k in ["tahun","year"]:
            if k in cols_lower:
                df_long["Tahun"] = df[k] if k in df.columns else 2024
                break
    # bersihkan jumlah
    df_long["Jumlah"] = pd.to_numeric(df_long["Jumlah"].astype(str).str.replace(",","").str.strip(), errors="coerce")

# simpan ke session
st.session_state["data"] = df_long

# ---------- filter 2024 ----------
df_long = df_long.copy()
df_long["Tahun"] = pd.to_numeric(df_long["Tahun"], errors="coerce")
data2024 = df_long[df_long["Tahun"] == 2024]

if data2024.empty:
    st.warning("Tidak ditemukan data untuk tahun 2024 dalam dataset.")
    st.write("Preview beberapa baris:")
    st.dataframe(df_long.head(10))
    st.stop()

# ---------- ringkasan ----------
st.subheader("📋 Ringkasan Utama (2024)")
total = int(data2024["Jumlah"].sum(skipna=True))
st.metric("Total kasus (2024, jumlah terlapor)", f"{total:,}")
st.write(f"Jumlah baris (entri): **{len(data2024)}**")

# Top provinsi
topprov = data2024.groupby("Provinsi")["Jumlah"].sum().sort_values(ascending=False).head(10)
st.markdown("**Provinsi dengan jumlah kasus terbanyak (2024)**")
st.bar_chart(topprov)
st.table(topprov.reset_index().rename(columns={"Provinsi":"Provinsi","Jumlah":"Jumlah Kasus"}))

# Distribusi jenis
distjenis = data2024.groupby("Jenis")["Jumlah"].sum().sort_values(ascending=False)
st.markdown("**Distribusi menurut jenis kekerasan (2024)**")
st.bar_chart(distjenis)
st.table(distjenis.reset_index().rename(columns={"Jenis":"Jenis Kekerasan","Jumlah":"Jumlah Kasus"}))

# Preview
st.markdown("---")
st.subheader("Contoh baris data (2024)")
st.dataframe(data2024.head(12), use_container_width=True)

st.markdown("---")
st.subheader("✍️ Mengapa isu ini penting untuk dibahas?")
st.write(
    "1. Kekerasan seksual berdampak langsung pada keselamatan, kesehatan mental, dan hak asasi korban.\n"
    "2. Data membantu mengidentifikasi area/geografi dengan tingkat kasus tinggi sehingga intervensi bisa ditargetkan.\n"
    "3. Banyak kasus tidak dilaporkan — angka yang terlihat kemungkinan lebih rendah dari kenyataan.\n"
)
st.info("Catatan: angka yang ditampilkan adalah angka terlapor pada dataset. Hormati privasi korban saat membagikan data ini.")
