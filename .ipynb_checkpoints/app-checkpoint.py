










import streamlit as st

pages = [
    st.Page(
        page="pages/page1.py",
        title="Visualisasi Data Kekerasan Seksual Tahun 2024",
        icon="📊",   # sesuai halaman utama
    ),
    st.Page(
        page="pages/page2.py",
        title="Berita",
        icon="📰",   # icon berita
    ),
    st.Page(
        page="pages/page3.py",
        title="Tentang Kekerasan Seksual",
        icon="⚠️",   # icon awareness
    ),

    # ======== PAGE BARU YANG DITAMBAHKAN ========

    st.Page(
        page="pages/page4_peta.py",
        title="Peta Sebaran Kasus",
        icon="🗺️",   # icon peta
    ),

    st.Page(
        page="pages/page5_korban.py",
        title="Profil Korban",
        icon="👩‍🦰",   # icon korban/perempuan
    ),

    st.Page(
        page="pages/page6_pelaku.py",
        title="Profil Pelaku",
        icon="🧑‍⚖️",   # icon pelaku/hukum
    ),
]

pg = st.navigation(
    pages,
    position="sidebar",
    expanded=True
)

pg.run()
