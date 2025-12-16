import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🗺️ Peta Penyebaran Kasus Kekerasan (Online Map Source)")

# ============================
# 1. Load CSV
# ============================
df = pd.read_csv("data_sebaran_kasus.csv")
prov_col = "Cakupan"
jumlah_col = df.columns[2]

df[jumlah_col] = (
    df[jumlah_col].astype(str)
    .str.replace(",", "")
    .str.replace(".", "", regex=False)
    .str.extract(r"(\d+)", expand=False)
)
df[jumlah_col] = pd.to_numeric(df[jumlah_col], errors="coerce").fillna(0)

# ============================
# 2. Load GeoJSON ONLINE
# ============================
geo_url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province.json"

geojson = requests.get(geo_url).json()

# cek key nama provinsi
props = geojson["features"][0]["properties"]
key_name = [k for k in props.keys() if "name" in k.lower() or "prov" in k.lower()][0]

# ============================
# 3. Peta Folium
# ============================
m = folium.Map(
    location=[-2.5, 118],
    zoom_start=5,
    tiles="cartodbpositron"
)

folium.Choropleth(
    geo_data=geojson,
    data=df,
    columns=[prov_col, jumlah_col],
    key_on=f"feature.properties.{key_name}",
    fill_color="YlOrRd",
    fill_opacity=0.8,
    line_opacity=0.3,
    nan_fill_color="white",
    legend_name="Jumlah Kasus Kekerasan",
).add_to(m)

st_folium(m, width="100%", height=650)
