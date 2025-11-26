











import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Visualisasi Data Kekerasan Seksual", page_icon="📊", layout="wide")

st.title("📊 Visualisasi Data Kekerasan Seksual terhadap Perempuan")

# --- Cek apakah data sudah tersedia ---
if "data" not in st.session_state:
    st.warning("⚠ Data belum tersedia. Silakan upload data terlebih dahulu di halaman Home atau halaman Input Data.")
    st.stop()

# Ambil data
df = st.session_state["data"]

# --- Tampilkan tabel ---
st.subheader("📄 Preview Data")
st.dataframe(df, use_container_width=True)

st.markdown("---")

# --- Pilih Kolom ---
st.subheader("🔎 Pilihan Kolom untuk Visualisasi")

# Deteksi kolom numerik dan kategori
numeric_cols = df.select_dtypes(include="number").columns.tolist()
category_cols = df.select_dtypes(exclude="number").columns.tolist()

# Dropdown sumbu X & Y
col1, col2 = st.columns(2)

with col1:
    x_col = st.selectbox("Pilih kolom untuk sumbu X (kategori)", options=category_cols)

with col2:
    y_col = st.selectbox("Pilih kolom untuk sumbu Y (nilai numerik)", options=numeric_cols)

st.markdown("---")

# --- Line Chart ---
st.subheader("📈 Line Chart")
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(df[x_col], df[y_col], marker="o")
ax.set_xlabel(x_col)
ax.set_ylabel(y_col)
ax.set_title(f"{y_col} berdasarkan {x_col}")
ax.grid(True)

st.pyplot(fig)

# --- Bar Chart ---
st.subheader("📊 Bar Chart")
fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.bar(df[x_col], df[y_col])
ax2.set_xlabel(x_col)
ax2.set_ylabel(y_col)
ax2.set_title(f"{y_col} berdasarkan {x_col}")

st.pyplot(fig2)

st.markdown("---")

# --- Ringkasan Statistik ---
st.subheader("📋 Statistik Deskriptif")
st.write(df[numeric_cols].describe())
