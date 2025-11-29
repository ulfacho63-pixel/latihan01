
import streamlit as st
import pandas as pd
import random

st.title("🗺️ Peta Sebaran Kasus (Contoh Data)")

# Jika tidak ada dataset asli, gunakan mock data
prov = [
    "Aceh","Sumatera Utara","Sumatera Barat","Riau","Jambi","Sumatera Selatan",
    "Bengkulu","Lampung","DKI Jakarta","Jawa Barat","Jawa Tengah","DI Yogyakarta",
    "Jawa Timur","Banten","Bali","NTB","NTT","Kalimantan Barat","Kalimantan Tengah",
    "Kalimantan Selatan","Kalimantan Timur","Sulawesi Utara","Sulawesi Tengah",
    "Sulawesi Selatan","Sulawesi Tenggara","Gorontalo","Maluku","Maluku Utara",
    "Papua","Papua Barat"
]

rows = []
for p in prov:
    rows.append({
        "Provinsi": p,
        "Jumlah": random.randint(50, 1500),
        "Tahun": 2024
    })

df = pd.DataFrame(rows)

st.subheader("Total Kasus per Provinsi")
st.bar_chart(df.set_index("Provinsi")["Jumlah"])

st.dataframe(df)
