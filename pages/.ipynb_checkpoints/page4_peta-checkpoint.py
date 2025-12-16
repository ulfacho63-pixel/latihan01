# pages/page4_peta.py
import streamlit as st
import pandas as pd
import json
import requests

from streamlit_folium import st_folium
import folium

st.set_page_config(layout="wide")
st.title("🗺️ Peta Sebaran Kasus Kekerasan terhadap Perempuan")

# ======================================================================
# 1. LOAD CSV
# ======================================================================
CSV_PATH = "data_sebaran_kasus.csv"

df = pd.read_csv(CSV_PATH, sep=None, engine="python")
df.columns = df.columns.str.strip()

prov_col = "Cakupan"
jumlah_col = df.columns[2]   # kolom Jumlah Kasus

# cleaning angka
df[jumlah_col] = (
    df[jumlah_col]
    .astype(str)
    .str.replace(",", "")
    .str.replace(".", "", regex=False)
    .str.extract(r"(\d+)", expand=False)
)
df[jumlah_col] = pd.to_numeric(df[jumlah_col], errors="coerce").fillna(0).astype(int)

# ======================================================================
# 2. MAPPING CSV NAMA PROVINSI → GEOJSON 34 PROVINSI
# ======================================================================
mapping = {
    "ACEH": "Aceh",
    "SUMATERA UTARA": "Sumatera Utara",
    "SUMATERA BARAT": "Sumatera Barat",
    "RIAU": "Riau",
    "JAMBI": "Jambi",
    "SUMATERA SELATAN": "Sumatera Selatan",
    "BENGKULU": "Bengkulu",
    "LAMPUNG": "Lampung",
    "JUAN BANGKA BELITUNG": "Kepulauan Bangka Belitung",
    "KEPULAUAN RIAU": "Kepulauan Riau",
    "DKI JAKARTA": "Jakarta Raya",
    "JAWA BARAT": "Jawa Barat",
    "JAWA TENGAH": "Jawa Tengah",
    "DI YOGYAKARTA": "Yogyakarta",
    "JAWA TIMUR": "Jawa Timur",
    "BANTEN": "Banten",
    "BALI": "Bali",
    "USA TENGGARA BARAT": "Nusa Tenggara Barat",
    "USA TENGGARA TIMUR": "Nusa Tenggara Timur",
    "KALIMANTAN BARAT": "Kalimantan Barat",
    "KALIMANTAN TENGAH": "Kalimantan Tengah",
    "KALIMANTAN SELATAN": "Kalimantan Selatan",
    "KALIMANTAN TIMUR": "Kalimantan Timur",
    "KALIMANTAN UTARA": "Kalimantan Utara",
    "SULAWESI UTARA": "Sulawesi Utara",
    "SULAWESI TENGAH": "Sulawesi Tengah",
    "SULAWESI SELATAN": "Sulawesi Selatan",
    "SULAWESI TENGGARA": "Sulawesi Tenggara",
    "GORONTALO": "Gorontalo",
    "SULAWESI BARAT": "Sulawesi Barat",
    "MALUKU": "Maluku",
    "MALUKU UTARA": "Maluku Utara",
    "PAPUA": "Papua",
    "PAPUA BARAT": "Papua Barat"
}

# provinsi yang tidak ada di GeoJSON 34 → dibuang
valid_keys = list(mapping.keys())

df = df[df[prov_col].isin(valid_keys)]

df[prov_col] = df[prov_col].replace(mapping)

st.subheader("📌 Data setelah mapping & pembersihan:")
st.dataframe(df, use_container_width=True)

# ======================================================================
# 3. LOAD GEOJSON 34 PROVINSI
# ======================================================================
geojson_url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province.json"

try:
    r = requests.get(geojson_url)
    r.raise_for_status()
    geojson_data = r.json()
    st.success("GeoJSON 34 provinsi berhasil dimuat.")
except Exception as e:
    st.error(f"Gagal memuat GeoJSON: {e}")
    st.stop()

# ======================================================================
# 4. DETEKSI OTOMATIS KEY NAMA PROVINSI DI GEOJSON
# ======================================================================
first_properties = geojson_data["features"][0]["properties"]

possible_keys = ["NAME_1", "Propinsi", "PROVINSI", "provinsi", "name"]
prop_key = None

for k in possible_keys:
    if k in first_properties:
        prop_key = k
        break

if not prop_key:
    st.error(f"Tidak menemukan key nama provinsi dalam GeoJSON. Keys ditemukan: {list(first_properties.keys())}")
    st.stop()

st.success(f"Menggunakan key GeoJSON: {prop_key}")

# ======================================================================
# 5. CHOROPLETH MAP
# ======================================================================
m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles="cartodbpositron")

folium.Choropleth(
    geo_data=geojson_data,
    data=df,
    columns=[prov_col, jumlah_col],
    key_on=f"feature.properties.{prop_key}",
    fill_color="YlOrRd",
    fill_opacity=0.8,
    line_opacity=0.2,
    legend_name="Jumlah Kasus Kekerasan",
    nan_fill_color="white",
).add_to(m)

folium.LayerControl().add_to(m)

st.subheader("🗺️ Peta Choropleth Kasus Kekerasan terhadap Perempuan")
st_folium(m, width="100%", height=650)
