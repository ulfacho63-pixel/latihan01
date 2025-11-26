import streamlit as st

# --- Konfigurasi halaman ---
st.set_page_config(page_title="Ulfa App - Home", page_icon="🏠", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("Menu")
    page = st.radio("Halaman", ["Home"], index=0)
    st.markdown("---")
    st.write("Made by Ulfa 🎓")

# --- Halaman Home ---
if page == "Home":
    # Header
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 7])

    with col1:
        st.image(
            "https://placehold.co/600x300/8f5dff/ffffff?text=Data+Kekerasan+Seksual", 
            use_column_width=True
        )

    with col2:
        st.title("Welcome to Ulfa's Home Page")
        st.write(
            "Aplikasi ini dibuat untuk menampilkan data terkait **kekerasan seksual terhadap perempuan di Indonesia**. "
            "Tujuannya adalah meningkatkan awareness, memberikan informasi yang mudah dipahami, serta mendukung upaya pencegahan melalui pemahaman data."
        )
        st.write(
            "Melalui visualisasi data sederhana, kamu dapat melihat pola, tren tahunan, dan perubahan kasus kekerasan seksual berdasarkan sumber data yang tersedia."
        )

    st.markdown("---")

    # Fitur
    # Upload Data Section
    st.subheader("📁 Upload Data Kekerasan Seksual")
    uploaded = st.file_uploader("Upload file CSV", type=["csv"])

if uploaded:
    try:
        df = pd.read_csv(uploaded)
        st.session_state["data"] = df
        st.success("Data berhasil diupload! Sekarang kamu bisa membuka halaman Visualisasi Data.")

        st.write("Preview Data:")
        st.dataframe(df)

    except Exception as e:
        st.error(f"Gagal membaca file: {e}")

st.markdown("---")

# Fitur
st.subheader("Fitur Utama")
f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("### 📁 Upload Data")
    st.write("Unggah file CSV berisi data kekerasan seksual untuk melihat tabel dan grafiknya.")

with f2:
    st.markdown("### 📊 Visualisasi Kasus")
    st.write("Lihat grafik tren, perbandingan tahunan, dan pola data lainnya.")

with f3:
    st.markdown("### 📝 Informasi Pendukung")
    st.write("Tampilkan ringkasan data, penjelasan, dan interpretasi sederhana.")

    st.markdown("---")

    # Tentang aplikasi
    st.subheader("Mengapa Data Ini Penting?")
    st.write(
        "Kekerasan seksual adalah isu serius dan masih banyak terjadi di Indonesia. "
        "Dengan menampilkan data secara terbuka dan mudah dipahami, diharapkan semakin banyak orang yang sadar, "
        "peduli, dan ikut mendorong lingkungan yang lebih aman bagi perempuan."
    )
    st.write(
        "Data bukan hanya angka — tetapi cerminan dari kasus nyata yang dialami perempuan. "
        "Dengan memahami data, kita bisa melihat urgensi permasalahan ini dan mendorong solusi yang lebih bermakna."
    )

    st.markdown("---")

    st.subheader("Kontak")
    st.write("Jika kamu ingin menambahkan fitur atau analisis tertentu, silakan sampaikan.")
    st.write("Email: ulfa@example.com (ganti sesuai kebutuhan).")

    st.markdown("---")
    st.caption("Note: Setelah memperbarui kode, lakukan git push lalu redeploy agar perubahan muncul di web.")

