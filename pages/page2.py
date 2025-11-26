
# pages/page2.py
# pages/page2.py
import streamlit as st

st.set_page_config(page_title="Berita KemenPPPA", page_icon="📰", layout="wide")

# -----------------------
# Konten utama
# -----------------------
st.title("📰 Angka Kekerasan terhadap Perempuan di Indonesia Menurun")
st.markdown("**Siaran Pers — Kementerian Pemberdayaan Perempuan dan Perlindungan Anak (KemenPPPA)**")
st.caption("Sumber: KemenPPPA — Siaran Pers (10 Oktober 2025).")

st.markdown("---")

# Lead / intro
st.write(
    "Hasil analisis awal dari Survei Pengalaman Hidup Perempuan Nasional (SPHPN) 2024 menunjukkan adanya penurunan "
    "prevalensi kekerasan terhadap perempuan di Indonesia. Hasil ini dipresentasikan oleh Deputi Bidang Perlindungan Hak "
    "Perempuan KemenPPPA dan menjadi bahan bagi penyusunan kebijakan yang lebih responsif gender."
)

# Temuan kunci (angka singkat)
st.subheader("Temuan Kunci")
cols = st.columns([1, 1, 1])
with cols[0]:
    st.metric("Prevalensi Kekerasan Fisik (2024)", "7.2%", delta="-1.0 pp vs 2021")
with cols[1]:
    st.metric("Prevalensi Kekerasan Seksual (2024)", "5.3%", delta="-0.4 pp vs 2021")
with cols[2]:
    st.metric("Prevalensi P2GP (sunat perempuan)", "46.3%", help="Angka prevalensi praktik Pemotongan/Pelukaan Genital Perempuan (2024).")

st.markdown(
    "Data SPHPN 2024 dikumpulkan secara kuantitatif di 178 kabupaten/kota dengan 13.914 responden perempuan usia 15–64 tahun; "
    "pendekatan kualitatif juga dilakukan di 5 provinsi untuk melengkapi analisis."
)

st.markdown("---")

# Block ringkasan lebih panjang dan poin penting
st.subheader("Ringkasan Penjelasan")
st.write(
    "- Penurunan prevalensi tercatat untuk kekerasan fisik (dari 8.2% di 2021 menjadi 7.2% di 2024) dan kekerasan seksual "
    "(dari 5.7% di 2021 menjadi 5.3% di 2024)."
)
st.write(
    "- Ada peningkatan keterbukaan korban untuk melaporkan pengalaman kekerasan—proporsi yang melapor kepada orang yang dipercaya meningkat (tercatat 4.2% pada 2024)."
)
st.write(
    "- Wilayah dengan prevalensi tinggi: Nusa Tenggara, Maluku, Papua (kekerasan oleh pasangan); Sulawesi (kekerasan oleh selain pasangan)."
)

# Expandable: kutipan dan konteks acara
with st.expander("Baca kutipan & konteks acara"):
    st.write(
        "Menurut Desy Andriani (Deputi Bidang Perlindungan Hak Perempuan KemenPPPA), hasil awal SPHPN 2024 "
        "diharapkan menjadi dasar penyusunan kebijakan yang responsif gender, berbasis bukti, dan berorientasi pada pencegahan "
        "serta pemulihan korban. Analisis awal ini dibahas dalam pertemuan konsultatif bersama UNFPA dan LD FEB UI."
    )
    st.write(
        "Penelitian menunjukkan juga adanya peningkatan pelaporan ke instansi resmi seperti kepolisian dan fasilitas kesehatan, "
        "yang diduga dipengaruhi oleh kampanye publik, pengesahan UU Tindak Pidana Kekerasan Seksual (TPKS), dan intervensi LSM."
    )
    st.write(
        "KemenPPPA menegaskan komitmennya untuk melakukan analisis mendalam (in-depth analysis) agar rekomendasi dapat dihasilkan "
        "dengan akurat dan dapat ditindaklanjuti oleh pemangku kepentingan lintas sektor."
    )

st.markdown("---")

# Saran ringkas untuk pembaca (edukasi)
st.subheader("Apa artinya bagi publik?")
st.write(
    "Angka penurunan adalah sinyal bahwa upaya pencegahan dan peningkatan kesadaran mungkin mulai berdampak — namun angka terlapor "
    "masih merefleksikan kasus yang diketahui; banyak kasus tetap tidak dilaporkan. Data ini menegaskan perlunya: "
)
st.write("- Peningkatan layanan pendampingan korban (kesehatan fisik & mental).")
st.write("- Peningkatan akses pelaporan dan respons cepat dari lembaga terkait.")
st.write("- Pendidikan dan kampanye pencegahan di daerah dengan prevalensi tinggi.")

st.markdown("---")

# Link sumber & meta
st.markdown("**Sumber resmi & bacaan lengkap:**")
st.write("[KemenPPPA — Angka Kekerasan terhadap Perempuan di Indonesia Menurun]("
         "https://www.kemenpppa.go.id/siaran-pers/angka-kekerasan-terhadap-perempuan-di-indonesia-menurun)")

st.caption("Jika ingin menautkan atau menampilkan kutipan langsung di publikasi lain, mohon cantumkan sumber resmi KemenPPPA.")




