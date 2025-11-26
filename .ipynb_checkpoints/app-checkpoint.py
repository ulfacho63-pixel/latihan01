










import streamlit as st

pages = [
    st.Page(
        page="pages/page1.py",
        title="Visualisasi Data Kekerasan Seksual Tahun 2024",
        icon="📊 📈"   # icon untuk halaman visualisasi utama
    ),
    st.Page(
        page="pages/page2.py",
        title="Berita",
        icon="📰"   # icon berita
    ),
    st.Page(
        page="pages/page3.py",
        title="Tentang Kekerasan Seksual",
        icon="🚺 ⚠️ 🛡️"  # icon untuk awareness
    )
]

pg = st.navigation(
    pages,
    position="sidebar",
    expanded=True
)

pg.run()

