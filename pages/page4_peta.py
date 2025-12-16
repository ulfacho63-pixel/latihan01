import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")
st.title("📊 Ringkasan Kekerasan KemenPPPA — Ditampilkan di Streamlit")

url = "https://kekerasan.kemenpppa.go.id/ringkasan"

st.subheader("🔹 Metode 1: Iframe (langsung embed website)")
st.info("Streamlit mencoba menampilkan halaman asli... Jika kosong → website menolak iframe.")

# ===============================================================
# 1️⃣ COBA TAMPILKAN IFRAME
# ===============================================================
try:
    st.components.v1.iframe(url, width=1350, height=850, scrolling=True)
    st.success("Iframe ditampilkan (jika terlihat).")
except Exception as e:
    st.error(f"Iframe gagal: {e}")

st.markdown("---")

# ===============================================================
# 2️⃣ COBA SCRAPE HTML (fallback)
# ===============================================================
st.subheader("🔹 Metode 2: Render HTML (fallback jika iframe ditolak)")
try:
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Render seluruh HTML ke Streamlit
        st.components.v1.html(str(soup), height=850, scrolling=True)
        st.success("HTML berhasil dimuat dari server KemenPPPA.")

    else:
        st.error(f"Gagal memuat HTML. Status code: {response.status_code}")

except Exception as e:
    st.error("Tidak bisa mengambil HTML dari website.")
    st.exception(e)

st.markdown("---")

# ===============================================================
# 3️⃣ INFO TAMBAHAN: Jika website berbasis React (SPA)
# ===============================================================
st.subheader("ℹ️ Catatan Penting")
st.write("""
Dashboard KemenPPPA dibuat menggunakan framework **React/JavaScript**. 
Banyak website SPA (Single Page Application) tidak bisa:
- ditampilkan via iframe, atau  
- di-scrape HTML-nya (karena konten dimuat via JavaScript, bukan HTML statis).

Jika kedua metode di atas tidak muncul kontennya, berarti:
- Website melarang iframe (X-Frame-Options), dan
- JavaScript dinonaktifkan saat scraping.

Solusi terbaik: **akses API backend mereka** untuk mengambil datanya secara langsung.
""")

# ===============================================================
# 4️⃣ Arahkan ke API jika diperlukan
# ===============================================================
st.write("Jika kamu ingin, saya bisa buatkan script untuk mengambil data dari API KemenPPPA.")
