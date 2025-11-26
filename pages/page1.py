# pages/page1.py (Home - versi khusus untuk format tabel yang kamu tunjukkan)
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Ulfa App - Home", page_icon="📊", layout="wide")

# Sidebar sederhana
with st.sidebar:
    st.title("Menu")
    st.write("🏠 Visualisasi Data Kekerasan Seksual Tahun 2024")
    st.write("📰 Berita")
    st.write("⚠️ Tentang Kekerasan Seksual")
    st.markdown("---")
    st.write("Made by Ulfa 🎓")

# Header
st.title("🏠 Kekerasan Seksual terhadap Perempuan — Tahun 2024")
st.write("Halaman ini menampilkan ringkasan data untuk **tahun 2024** berdasarkan file CSV yang kamu upload/simpan.")
st.markdown("---")

# --- Baca data (session_state atau file lokal) ---
df = None
if "data" in st.session_state:
    df = st.session_state["data"]
else:
    for f in ["data_kekerasan_perempuan.csv", "pages/data_kekerasan_perempuan.csv"]:
        if os.path.exists(f):
            df = pd.read_csv(f)
            st.session_state["data"] = df
            st.info(f"Membaca data dari {f}")
            break

if df is None:
    st.warning("Data belum tersedia. Silakan upload CSV di halaman Visualisasi Data atau taruh file data_kekerasan_perempuan.csv ke folder project.")
    st.stop()

# --- Normalisasi nama kolom (hilangkan spasi awal/akhir) ---
df.columns = df.columns.str.strip()

# --- Tentukan kolom provinsi dan daftar kolom jenis yang relevan ---
# Berdasarkan screenshot: 'Cakupan' = provinsi, kolom jenis: Fisik, Psikis, Seksual, Eksploitasi, TPPO, Penelantaran, Lainnya
# Gunakan case-insensitive pencarian untuk lebih aman
cols_lower = [c.lower() for c in df.columns]

# cari kolom provinsi (fallback jika header berbeda)
prov_candidates = ["cakupan", "provinsi", "wilayah", "nama provinsi"]
prov_col = None
for k in prov_candidates:
    if k in cols_lower:
        prov_col = df.columns[cols_lower.index(k)]
        break

if prov_col is None:
    st.error("Kolom provinsi/cakupan tidak ditemukan. Pastikan ada kolom 'Cakupan' atau 'Provinsi'.")
    st.write("Kolom yang tersedia:", df.columns.tolist())
    st.stop()

# daftar kolom jenis yang diharapkan (biarkan aman jika ada perbedaan huruf besar/kecil)
expected_jenis = ["Fisik","Psikis","Seksual","Eksploitasi","TPPO","Penelantaran","Lainnya"]
jenis_cols = [c for c in df.columns if c.strip().lower() in [e.lower() for e in expected_jenis]]

if len(jenis_cols) == 0:
    st.error("Tidak menemukan kolom jenis kekerasan (Fisik, Psikis, Seksual, ...).")
    st.write("Kolom yang tersedia:", df.columns.tolist())
    st.stop()

# pastikan numeric
for c in jenis_cols:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(",","").str.strip(), errors="coerce")

# hapus baris total 'INDONESIA' bila ada
df = df[~df[prov_col].astype(str).str.strip().str.upper().eq("INDONESIA")]

# --- Hitung ringkasan nasional dan per-provinsi ---
total_nasional = int(df[jenis_cols].sum().sum())

st.subheader("📋 Ringkasan Utama (2024)")
st.metric("Total kasus (terlapor) — nasional", f"{total_nasional:,}")

# jumlah baris (entri provinsi)
st.write(f"Jumlah baris (entri provinsi): **{len(df)}**")

# Top 10 provinsi berdasarkan total (jumlah semua jenis)
df["Total_Provinsi"] = df[jenis_cols].sum(axis=1)
top10 = df[[prov_col, "Total_Provinsi"]].sort_values("Total_Provinsi", ascending=False).head(10)
st.markdown("### 🔥 Provinsi dengan jumlah kasus terbanyak (Top 10)")
st.bar_chart(top10.set_index(prov_col)["Total_Provinsi"])
st.table(top10.rename(columns={prov_col: "Provinsi", "Total_Provinsi": "Jumlah Kasus"}).reset_index(drop=True))

# Distribusi per jenis
st.markdown("### 💠 Distribusi kasus menurut jenis kekerasan (2024)")
jenis_total = df[jenis_cols].sum().sort_values(ascending=False)
st.bar_chart(jenis_total)
st.table(jenis_total.reset_index().rename(columns={"index":"Jenis Kekerasan", 0:"Jumlah"}))

# Preview data (head)
st.markdown("---")
st.subheader("Contoh Data (preview)")
st.dataframe(df[[prov_col] + jenis_cols + ["Total_Provinsi"]].head(15), use_container_width=True)

# Penjelasan singkat
st.markdown("---")
st.subheader("✍️ Mengapa isu ini penting untuk dibahas?")
st.write(
    "1. Kekerasan seksual berdampak langsung pada keselamatan, kesehatan mental, dan hak asasi korban.\n"
    "2. Data membantu mengidentifikasi area/geografi dengan tingkat kasus tinggi sehingga intervensi bisa ditargetkan.\n"
    "3. Banyak kasus tidak dilaporkan — angka yang terlihat kemungkinan lebih rendah dari kenyataan.\n"
)
st.info("Catatan: angka yang ditampilkan adalah angka terlapor pada dataset. Hormati privasi korban saat membagikan data ini.")
