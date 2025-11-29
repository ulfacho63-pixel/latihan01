import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests

st.title("🗺️ Peta Sebaran Kasus Kekerasan terhadap Perempuan")

# --- Load data CSV ---
df = pd.read_csv("data_sebaran_kasus.csv")

# Sesuaikan nama kolom jika perlu
prov_col = "Provinsi"
jumlah_col = "Jumlah"

# --- Load GeoJSON Indonesia ---
geojson_url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-provinsi.json"
geojson = requests.get(geojson_url).json()

# --- Plot Peta ---
fig = px.choropleth(
    df,
    geojson=geojson,
    locations=prov_col,
    featureidkey="properties.Propinsi",
    color=jumlah_col,
    color_continuous_scale="Reds",
    hover_name=prov_col,
    title="Sebaran Kasus Kekerasan terhadap Perempuan per Provinsi"
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(height=700)

st.plotly_chart(fig, use_container_width=True)

