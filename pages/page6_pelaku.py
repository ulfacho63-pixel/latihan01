import streamlit as st
import pandas as pd
import numpy as np

st.title("🧑‍⚖️ Profil Pelaku (Contoh Data)")

n = 200
np.random.seed(12)

df = pd.DataFrame({
    "Usia": np.random.randint(15, 70, n),
    "Jenis Kelamin": np.random.choice(["Laki-laki","Perempuan"], n, p=[0.9, 0.1]),
    "Status": np.random.choice(["Teman","Pacar","Suami","Keluarga","Tetangga","Orang Asing"], n),
    "Pekerjaan": np.random.choice(["Pengangguran","Buruh","Pegawai","Wiraswasta","Pelajar"], n)
})

st.subheader("Distribusi Usia Pelaku")
st.bar_chart(df["Usia"].value_counts().sort_index())

st.subheader("Jenis Kelamin Pelaku")
st.dataframe(df["Jenis Kelamin"].value_counts())

st.subheader("Hubungan Pelaku dengan Korban")
st.dataframe(df["Status"].value_counts())
