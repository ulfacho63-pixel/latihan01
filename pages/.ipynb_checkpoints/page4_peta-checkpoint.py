# pages/page4_peta.py
import streamlit as st
import pandas as pd
import json
import os

# Optional: folium
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

# -------------------------------------------------------------------
# APP HEADER
# -------------------------------------------------------------------
st.set_page_config(layout="wide")
st.title("🗺️ Peta Sebaran Kasus Kekerasan terhadap Perempuan")

# -------------------------------------------------------------------
# LOAD CSV
# -------------------------------------------------------------------
CSV_PATH = "data_sebaran_kasus.csv"  # Ganti jika nama file berbeda

if not os.path.exists(CSV_PATH):
    st.error(f"File CSV tidak ditemukan: {CSV_PATH}")
    st.stop()

def read_csv_tolerant(path):
    """Deteksi otomatis delimiter CSV"""
    try:
        df = pd.read_csv(path)
        if len(df.columns) == 1:  # salah delimiter
            df = pd.read_csv(path, sep=";")
        return df
    except:
        pass

    try:
        return pd.read_csv(path, sep=";")
    except:
        pass

    try:
        return pd.read_table(path, sep=None, engine="python")
    except Exception as e:
        raise e

# Baca CSV
try:
    df = read_csv_tolerant(CSV_PATH)
except Exception as e:
    st.exception(f"Gagal membaca CSV: {e}")
    st.stop()

df.columns = df.columns.str.strip()

st.subheader("📌 Kolom terdeteksi:")
st.write(list(df.columns))

# -------------------------------------------------------------------
# DETEKSI KOLOM PROVINSI & JUMLAH KASUS
# -------------------------------------------------------------------
def find_col(cols, keywords):
    cols_lower = [c.lower() for c in cols]
    # exact match
    for kw in keywords:
        if kw.lower() in cols_lower:
            return cols[cols_lower.index(kw.lower())]
    # substring match
    for c in cols:
        for kw in keywords:
            if kw.lower() in c.lower():
                return c
    return None

prov_candidates = ["provinsi", "prov", "cakupan", "nama provinsi", "wilayah"]
jumlah_candidates = ["jumlah", "total", "kasus", "korban"]

prov_col = find_col(df.columns, prov_candidates)
jumlah_col = find_col(df.columns, jumlah_candidates)

if not prov_col or not jumlah_col:
    st.warning("❗ Tidak menemukan kolom provinsi atau kolom jumlah.")
    st.info("Periksa ulang CSV Anda.")
    st.dataframe(df.head(), use_container_width=True)
    st.stop()

# -------------------------------------------------------------------
# BERSIHKAN KOLOM JUMLAH
# -------------------------------------------------------------------
df[jumlah_col] = (
    df[jumlah_col]
    .astype(str)
    .str.replace(",", "")
    .str.replace(".", "", regex=False)
    .str.extract(r"(\d+)", expand=False)
)

df[jumlah_col] = pd.to_numeric(df[jumlah_col], errors="coerce").fillna(0).astype(int)

df = df.dropna(subset=[prov_col])
df[prov_col] = df[prov_col].astype(str).str.strip()

# -------------------------------------------------------------------
# LOAD GEOJSON
# -------------------------------------------------------------------
GEOJSON_LOCAL = "indonesia-provinsi.json"
geojson_data = None

if os.path.exists(GEOJSON_LOCAL):
    try:
        with open(GEOJSON_LOCAL, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
        st.success("GeoJSON ditemukan dan dimuat.")
    except Exception as e:
        st.warning(f"GeoJSON gagal dibaca: {e}")
else:
    st.info(f"GeoJSON lokal `{GEOJSON_LOCAL}` tidak ditemukan.")
    geojson_data = None

# -------------------------------------------------------------------
# DETEKSI KEY GEOJSON
# -------------------------------------------------------------------
def detect_geo_property(geojson, prov_sample):
    if not geojson or "features" not in geojson:
        return None
    sample = prov_sample.lower()
    keys = list(geojson["features"][0]["properties"].keys())
    for key in keys:
        for feat in geojson["features"]:
            val = feat["properties"].get(key, "")
            if isinstance(val, str) and sample in val.lower():
                return key
    return None

# -------------------------------------------------------------------
# CHOROPLETH MAP (JIKA FOLIUM TERSEDIA)
# -------------------------------------------------------------------
if FOLIUM_AVAILABLE and geojson_data:
    st.success("✔ Folium & GeoJSON tersedia — membuat peta choropleth...")

    sample_prov = df[prov_col].dropna().iloc[0]
    prop_key = detect_geo_property(geojson_data, sample_prov)

    if prop_key:
        try:
            m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles="cartodbpositron")

            folium.Choropleth(
                geo_data=geojson_data,
                data=df,
                columns=[prov_col, jumlah_col],
                key_on=f"feature.properties.{prop_key}",
                fill_color="YlOrRd",
                fill_opacity=0.8,
                line_opacity=0.2,
                legend_name=f"Jumlah kasus ({jumlah_col})",
            ).add_to(m)

            st_folium(m, width="100%", height=650)
            st.markdown("💡 **Jika data tidak cocok dengan peta, periksa ejaan nama provinsi.**")
            st.stop()
        except Exception as e:
            st.error(f"Gagal membuat choropleth: {e}")

# -------------------------------------------------------------------
# FALLBACK: BAR CHART
# -------------------------------------------------------------------
st.info("🔄 Menampilkan fallback: grafik batang per provinsi.")

grouped = df.groupby(prov_col)[jumlah_col].sum().sort_values(ascending=False)

st.subheader("📊 Sebaran Kasus per Provinsi")
st.bar_chart(grouped)

st.subheader("📄 Tabel Ringkasan")
st.dataframe(
    grouped.reset_index().rename(columns={prov_col: "Provinsi", jumlah_col: "Jumlah"}),
    use_container_width=True,
)
