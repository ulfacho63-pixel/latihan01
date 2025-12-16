# pages/page4_peta.py
import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🗺️ Peta Choropleth Kasus Kekerasan terhadap Perempuan")

# ==============================================================
# 1. LOAD CSV
# ==============================================================
CSV_PATH = "data_sebaran_kasus.csv"

df = pd.read_csv(CSV_PATH, sep=None, engine="python")
df.columns = df.columns.str.strip()

prov_col = "Cakupan"
jumlah_col = df.columns[2]  # Jumlah Kasus (Kasus)

# Cleaning angka
df[jumlah_col] = (
    df[jumlah_col]
    .astype(str)
    .str.replace(",", "")
    .str.replace(".", "", regex=False)
    .str.extract(r"(\d+)", expand=False)
)
df[jumlah_col] = pd.to_numeric(df[jumlah_col], errors="coerce").fillna(0)

# ==============================================================
# 2. MAPPING NAMA PROVINSI CSV → 34 PROVINSI GEOJSON
# ==============================================================

mapping = {
    "ACEH": "Aceh",
    "SUMATERA UTARA": "Sumatera Utara",
    "SUMATERA BARAT": "Sumatera Barat",
    "RIAU": "Riau",
    "JAMBI": "Jambi",
    "SUMATERA SELATAN": "Sumatera Selatan",
    "BENGKULU": "Bengkulu",
    "LAMPUNG": "Lampung",
    "JUAN BANGKA BELITUNG": "Kepulauan Bangka Belitung",  # typo diperbaiki
    "KEPULAUAN RIAU": "Kepulauan Riau",
    "DKI JAKARTA": "Jakarta Raya",
    "JAWA BARAT": "Jawa Barat",
    "JAWA TENGAH": "Jawa Tengah",
    "DI YOGYAKARTA": "Yogyakarta",
    "JAWA TIMUR": "Jawa Timur",
    "BANTEN": "Banten",
    "BALI": "Bali",
    "USA TENGGARA BARAT": "Nusa Tenggara Barat",  # typo
    "USA TENGGARA TIMUR": "Nusa Tenggara Timur",  # typo
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

# Drop baris tidak relevan
df = df[df[prov_col] != "INDONESIA"]

valid_raw = list(mapping.keys())
df = df[df[prov_col].isin(valid_raw)]

# Terapkan mapping
df[prov_col] = df[prov_col].replace(mapping)

# ==============================================================
# 🔍 DEBUG 1 — Tampilkan hasil mapping provinsi
# ==============================================================
st.write("### 🔍 DEBUG: Nama Provinsi Setelah Mapping")
st.write(df[prov_col].unique())
st.write("Jumlah baris data setelah mapping:", len(df))

# ==============================================================
# 3. LOAD GEOJSON 34 PROVINSI
# ==============================================================
geojson_url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province.json"

try:
    r = requests.get(geojson_url)
    r.raise_for_status()
    geojson_data = r.json()
    st.success("GeoJSON 34 provinsi berhasil dimuat.")
except Exception as e:
    st.error(f"Gagal mengambil GeoJSON: {e}")
    st.stop()

# ==============================================================
# 4. DETEKSI KEY PROVINSI DALAM GEOJSON
# ==============================================================
first_props = geojson_data["features"][0]["properties"]
possible_keys = ["NAME_1", "Propinsi", "PROVINSI", "provinsi", "name"]

prop_key = None
for k in possible_keys:
    if k in first_props:
        prop_key = k
        break

# DEBUG 2 → tampilkan keys
st.write("### 🔍 DEBUG: Keys pada GeoJSON")
st.write(first_props)

if not prop_key:
    st.error("❌ Tidak menemukan key untuk nama provinsi di GeoJSON!")
    st.stop()

st.success(f"GeoJSON menggunakan key provinsi: **{prop_key}**")

# ==============================================================
# 5. BUAT PETA CHOROPLETH
# ==============================================================
m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles="cartodbpositron")

folium.Choropleth(
    geo_data=geojson_data,
    data=df,
    columns=[prov_col, jumlah_col],
    key_on=f"feature.properties.{prop_key}",
    fill_color="YlOrRd",
    fill_opacity=0.8,
    line_opacity=0.2,
    nan_fill_color="white",
    legend_name="Jumlah Kasus Kekerasan",
).add_to(m)

st.subheader("🗺️ Peta Choropleth")
st_folium(m, width="100%", height=650)
