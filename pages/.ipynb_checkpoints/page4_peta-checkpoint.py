import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium

st.title("🗺️ Peta Sebaran Kasus Kekerasan terhadap Perempuan")

# Load data kasus
df = pd.read_csv("data_sebaran_kasus.csv")

# Nama kolom (sesuaikan dengan CSV kamu)
prov_col = "Cakupan"
jumlah_col = "Jumlah Kasus (Kasus)"

# Load GeoJSON lokal
geojson_path = "indonesia-provinsi.json"
with open(geojson_path, "r") as f:
    geojson_data = json.load(f)

# Membuat peta
m = folium.Map(location=[-2.5, 118], zoom_start=5)

# Gabungkan data kasus dengan GeoJSON
folium.Choropleth(
    geo_data=geojson_data,
    data=df,
    columns=[prov_col, jumlah_col],
    key_on="feature.properties.Propinsi",
    fill_color="YlOrRd",
    line_opacity=0.5,
    legend_name="Jumlah Kasus"
).add_to(m)

st_folium(m, width=900, height=550)
