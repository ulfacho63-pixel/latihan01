# app.py - Home (ringkasan 2024)
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ulfa App - Home", page_icon="🏠", layout="wide")

# --------------------------
# Sidebar sederhana (tidak duplikat menu)
# --------------------------
with st.sidebar:
    st.title("Menu")
    st.write("🏠 Home")
    st.write("📊 Visualisasi Data")
    st.markdown("---")
    st.write("Made by Ulfa 🎓")

# --------------------------
# Header utama
# --------------------------
st.title("🏠 Ringkasan Data Kekerasan Seksual terhadap Perempuan — Tahun 2024")
st.write(
    "Halaman ini menampilkan ringkasan data untuk **tahun 2024**. "
    "Tujuannya untuk meningkatkan kesadaran (awareness) dan memberikan gambaran singkat yang mudah dipahami."
)
st.markdown("---")

# --------------------------
# Fungsi bantu: cari kolom relevan
# --------------------------
def find_col(df, keywords):
    for k in keywords:
        for c in df.columns:
            if k.lower() in c.lower():
                return c
    return None

# --------------------------
# Ambil data: prioritas session_state, lalu file lokal "data_kekerasan_perempuan.csv"
# --------------------------
df = None
if "data" in st.session_state:
    df = st.session_state["data"]
else:
    # coba baca file lokal (jika kamu menyimpan CSV di repo)
    try:
        df = pd.read_csv("data_kekerasan_perempuan.csv")
    except Exception:
        df = None

# Jika tidak ada data, tampilkan pesan singkat (tanpa upload box)
if df is None:
    st.warning(
        "Data untuk ringkasan 2024 belum tersedia pada sesi ini. "
        "Silakan unggah file data di halaman *Visualisasi Data* atau simpan file `data_kekerasan_perempuan.csv` ke folder project."
    )
    st.info("Setelah mengunggah data, kembali ke halaman ini untuk melihat ringkasan 2024.")
    st.markdown("---")
    st.subheader("Mengapa Data Ini Penting?")
    st.write(
        "- Kekerasan seksual adalah masalah serius yang berdampak fisik, psikologis, dan sosial bagi korban.\n"
        "- Menampilkan data membantu publik melihat skala masalah, pola geografis, dan jenis kekerasan yang paling sering terjadi.\n"
        "- Data bukan hanya angka — ini indikator kebutuhan perlindungan, layanan pendampingan, dan kebijakan pencegahan.\n"
    )
    st.write(
        "Jika kamu sudah mengunggah data di halaman Visualisasi Data namun ringkasan belum muncul, pastikan kamu mengunggah pada sesi browser yang sama sehingga `session_state` bisa membaca datanya."
    )
    st.stop()

# --------------------------
# Normalisasi: temukan kolom penting
# --------------------------
col_tahun = find_col(df, ["tahun", "year"])
col_prov = find_col(df, ["provinsi", "province", "propinsi", "region"])
col_jumlah = find_col(df, ["jumlah", "kasus", "total", "count", "nilai"])
col_jenis = find_col(df, ["jenis", "kekerasan", "kategori", "type"])

# Pastikan kolom jumlah numeric bila ada
if col_jumlah:
    df[col_jumlah] = pd.to_numeric(df[col_jumlah], errors="coerce")

# Jika kolom tahun ada, coba ubah ke numeric
if col_tahun:
    df[col_tahun] = pd.to_numeric(df[col_tahun], errors="coerce")

# --------------------------
# Filter untuk tahun 2024
# --------------------------
if col_tahun:
    data2024 = df[df[col_tahun] == 2024]
else:
    # jika tidak ada kolom tahun, coba cari kolom yang berisi "2024" (case-insensitive)
    mask_2024 = df.apply(lambda row: row.astype(str).str.contains("2024", case=False).any(), axis=1)
    data2024 = df[mask_2024]

# Jika kosong
if data2024.empty:
    st.warning("Tidak ditemukan data untuk tahun 2024 dalam dataset.")
    st.markdown("---")
    st.subheader("Mengapa Data Ini Penting?")
    st.write(
        "Ringkasan tahun 2024 tidak tersedia karena dataset tidak mengandung baris dengan tahun 2024. "
        "Periksa kolom tahun pada file data kamu atau gunakan dataset yang memuat data 2024."
    )
    st.stop()

# --------------------------
# Hitung ringkasan utama untuk 2024
# --------------------------
st.subheader("📋 Ringkasan Utama (2024)")

# Total kasus (jika kolom jumlah tersedia)
if col_jumlah:
    total_2024 = int(data2024[col_jumlah].sum(skipna=True))
    st.metric("Total kasus (2024, jumlah terlapor)", f"{total_2024:,}")
else:
    st.info("Kolom jumlah/kasus tidak terdeteksi — total kasus tidak dapat dihitung otomatis.")

# Rentang waktu & baris
st.write(f"Jumlah baris (entri) untuk 2024: **{len(data2024)}**")

# Top provinsi
if col_prov and col_jumlah:
    top_prov = data2024.groupby(col_prov)[col_jumlah].sum().sort_values(ascending=False).head(10)
    st.markdown("**Provinsi dengan jumlah kasus terbanyak (2024)**")
    st.bar_chart(top_prov)
    st.table(top_prov.reset_index().rename(columns={col_prov: "Provinsi", col_jumlah: "Jumlah Kasus"}))
elif col_prov:
    st.write("Kolom provinsi terdeteksi tetapi kolom jumlah tidak ditemukan — tidak dapat menghitung total per provinsi.")
else:
    st.write("Kolom provinsi tidak terdeteksi otomatis.")

# Distribusi jenis kekerasan (opsional)
if col_jenis and col_jumlah:
    st.markdown("**Distribusi menurut jenis kekerasan (2024)**")
    dist_jenis = data2024.groupby(col_jenis)[col_jumlah].sum().sort_values(ascending=False)
    st.bar_chart(dist_jenis)
    st.table(dist_jenis.reset_index().rename(columns={col_jenis: "Jenis Kekerasan", col_jumlah: "Jumlah Kasus"}))
elif col_jenis:
    st.write("Kolom jenis kekerasan terdeteksi tetapi kolom jumlah tidak ditemukan.")
else:
    st.info("Kolom jenis kekerasan tidak ada atau tidak terdeteksi (opsional).")

# Preview sample baris (opsional, singkat)
st.markdown("---")
st.subheader("Contoh baris data (2024)")
st.dataframe(data2024.head(10), use_container_width=True)

# --------------------------
# Penjelasan singkat / edukatif
# --------------------------
st.markdown("---")
st.subheader("✍️ Mengapa isu ini penting untuk dibahas?")
st.write(
    "1. Kekerasan seksual berdampak langsung pada keselamatan, kesehatan mental, dan hak asasi korban.\n"
    "2. Data membantu mengidentifikasi area/geografi dengan tingkat kasus tinggi sehingga intervensi bisa ditargetkan.\n"
    "3. Banyak kasus tidak dilaporkan — angka yang terlihat kemungkinan lebih rendah dari kenyataan. Oleh karena itu data harus dibaca dengan hati-hati.\n"
    "4. Penyebaran informasi berbasis data penting untuk mendorong kebijakan perlindungan, layanan korban, dan pendidikan pencegahan.\n\n"
    "Jika kamu ingin analisis lanjut (tren tahunan, peta sebaran, atau analisis per jenis korban), buka halaman *Visualisasi Data*."
)

st.info("Catatan: angka yang ditampilkan adalah angka terlapor/tercatat pada dataset. Hormati privasi dan martabat korban saat membagikan data ini.")
st.markdown("---")
st.caption("Tip: Jika kamu ingin Home selalu menampilkan ringkasan 2024 tanpa perlu upload tiap sesi, simpan file CSV di folder project dengan nama 'data_kekerasan_perempuan.csv'.")
