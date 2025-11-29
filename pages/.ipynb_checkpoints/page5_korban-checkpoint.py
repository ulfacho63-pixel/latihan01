import streamlit as st
import pandas as pd
import numpy as np

st.title("👩‍🦰 Profil Korban (Contoh Data)")

# Data contoh
n = 300
np.random.seed(42)

df = pd.DataFrame({
    "Usia": np.random.randint(5, 70, n),
    "Pendidikan": np.random.choice(["SD","SMP","SMA","D3/S1","Tidak Sekolah"], n),
    "Pekerjaan": np.random.choice(["Pelajar","Ibu Rumah Tangga","Pekerja Formal","Buruh","Tidak Bekerja"], n),
    "Relasi Pelaku": np.random.choice(["Keluarga","Teman","Pacar","Suami","Orang Asing"], n),
})

st.subheader("Distribusi Usia")
st.bar_chart(df["Usia"].value_counts().sort_index())

st.subheader("Pendidikan")
st.dataframe(df["Pendidikan"].value_counts())

st.subheader("Relasi Pelaku terhadap Korban")
st.dataframe(df["Relasi Pelaku"].value_counts())
