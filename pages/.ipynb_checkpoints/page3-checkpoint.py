











# pages/page3.py
import streamlit as st

st.set_page_config(page_title="Informasi Kekerasan Seksual", page_icon="📚", layout="wide")

st.title("📚 Informasi Kekerasan Seksual")
st.write(
    "Halaman ini berisi penjelasan tentang 15 bentuk kekerasan seksual menurut Komnas Perempuan. "
    "Tujuannya untuk membantu pembaca memahami cakupan tindakan yang termasuk kekerasan seksual."
)
st.markdown("---")

st.subheader("🟣 15 Bentuk Kekerasan Seksual (Komnas Perempuan)")

bentuk = [
    ("Pemerkosaan",
     "Pemaksaan hubungan seksual melalui ancaman, kekerasan, atau kondisi di mana korban tidak mampu memberi persetujuan."),
    ("Intimidasi seksual",
     "Ancaman, tekanan, atau percobaan pemerkosaan yang menimbulkan rasa takut dan membuat korban tidak berdaya."),
    ("Pelecehan seksual",
     "Perilaku bernuansa seksual yang tidak diinginkan, mis. komentar, sentuhan, siulan, atau gesture yang mengganggu."),
    ("Eksploitasi seksual",
     "Pemanfaatan tubuh atau kondisi korban untuk keuntungan pelaku, seperti pembuatan konten seksual tanpa izin."),
    ("Perdagangan perempuan untuk tujuan seksual",
     "Memperjualbelikan perempuan untuk eksploitasi dan tujuan seksual."),
    ("Prostitusi paksa",
     "Pemaksaan korban untuk bekerja di industri seks tanpa persetujuan."),
    ("Perbudakan seksual",
     "Kondisi di mana korban dikendalikan dan dipaksa melakukan aktivitas seksual."),
    ("Pemaksaan perkawinan",
     "Memaksa seseorang menikah tanpa persetujuan, termasuk pernikahan anak paksa."),
    ("Pemaksaan kehamilan",
     "Pemaksaan korban untuk hamil melalui pemaksaan atau manipulasi."),
    ("Pemaksaan aborsi",
     "Pemaksaan korban untuk menggugurkan kandungan tanpa persetujuan."),
    ("Pemaksaan kontrasepsi / sterilisasi",
     "Tindakan medis yang dilakukan tanpa persetujuan korban untuk mengendalikan reproduksi."),
    ("Penyiksaan seksual",
     "Penggunaan kekerasan bernuansa seksual yang menyebabkan penderitaan atau luka."),
    ("Penghukuman/penindasan bernuansa seksual",
     "Menghukum atau mempermalukan seseorang dengan cara yang menyinggung seksualitasnya."),
    ("Praktik tradisi/aturan diskriminatif bernuansa seksual",
     "Aturan adat atau praktik budaya yang merugikan perempuan dan mengandung unsur seksual."),
    ("Kontrol seksual",
     "Pembatasan dan pengawasan terhadap tubuh atau pilihan seksual seseorang berdasarkan norma yang menindas.")
]

for title, desc in bentuk:
    st.markdown(f"### 🔹 {title}")
    st.write(desc)
    st.markdown("---")

st.caption("Sumber: Komnas Perempuan — '15 Bentuk Kekerasan Seksual'. Halaman ini dibuat untuk tujuan edukasi dan peningkatan awareness.")
