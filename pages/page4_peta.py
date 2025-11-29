# pages/page4_peta.py
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(layout="wide")
st.title("🗺️ Peta Sebaran Kasus Kekerasan terhadap Perempuan")

# Try optional geo libs (don't crash if not installed)
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

# ---------- Load CSV ----------
CSV_PATH = "data_sebaran_kasus.csv"  # ubah jika file berbeda
if not os.path.exists(CSV_PATH):
    st.error(
        f"File data tidak ditemukan: `{CSV_PATH}`. "
        "Letakkan CSV (mis: data_sebaran_kasus.csv) di folder project atau unggah di halaman Visualisasi Data."
    )
    st.stop()

# baca CSV dengan delimiter deteksi (toleran terhadap ; atau ,)
def read_csv_tolerant(path):
    # coba dengan pandas default
    try:
        df = pd.read_csv(path)
        return df
    except Exception:
        # coba delimiter semicolon
        try:
            df = pd.read_csv(path, sep=";")
            return df
        except Exception:
            # coba read with engine python and guess
            try:
                df = pd.read_table(path, sep=None, engine="python")
                return df
            except Exception as e:
                raise e

try:
    df = read_csv_tolerant(CSV_PATH)
except Exception as e:
    st.exception(f"Gagal membaca CSV: {e}")
    st.stop()

st.subheader("Kolom terdeteksi:")
st.write(list(df.columns))

# ---------- heuristik cari kolom ----------
def find_col(cols, keywords):
    """Return first column name that contains any keyword (case-insensitive)."""
    cols_lower = [c.lower() for c in cols]
    for kw in keywords:
        # exact lower match first
        if kw.lower() in cols_lower:
            return cols[cols_lower.index(kw.lower())]
    # substring match
    for c in cols:
        for kw in keywords:
            if kw.lower() in c.lower():
                return c
    return None

prov_candidates = ["provinsi", "prov", "cakupan", "nama provinsi", "region", "wilayah", "cakupan"]
jumlah_candidates = ["jumlah", "kasus", "total", "nilai", "korban", "jumlah korban", "jumlah kasus"]

prov_col = find_col(df.columns, prov_candidates)
jumlah_col = find_col(df.columns, jumlah_candidates)

if not prov_col or not jumlah_col:
    st.warning("Tidak menemukan kolom provinsi atau kolom jumlah/kasus otomatis.")
    st.info("Periksa nama kolom CSV atau ubah nama menjadi mengandung kata 'provinsi' dan 'jumlah' / 'kasus'.")
    st.subheader("Preview data sumber")
    st.dataframe(df.head(50), use_container_width=True)
    st.stop()

# bersihkan jumlah jadi numeric
df[jumlah_col] = (
    df[jumlah_col].astype(str)
    .str.replace(",", "")
    .str.replace(".", "", regex=False)  # jika format ribuan menggunakan titik
    .str.extract(r"(\d+)", expand=False)  # ambil angka pertama
)
df[jumlah_col] = pd.to_numeric(df[jumlah_col], errors="coerce").fillna(0).astype(int)

# drop baris tanpa provinsi
df = df.dropna(subset=[prov_col])
df[prov_col] = df[prov_col].astype(str).str.strip()

# ---------- GeoJSON loading ----------
GEOJSON_LOCAL = "indonesia-provinsi.json"  # nama file di repo/project
geojson_data = None
if os.path.exists(GEOJSON_LOCAL):
    try:
        with open(GEOJSON_LOCAL, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
        st.success("GeoJSON lokal ditemukan dan dimuat.")
    except Exception as e:
        st.warning(f"Gagal baca GeoJSON lokal `{GEOJSON_LOCAL}`: {e}")
else:
    st.info(f"GeoJSON lokal `{GEOJSON_LOCAL}` tidak ditemukan di folder project.")
    # optional: coba remote URL (contoh repositori publik)
    remote_try = st.checkbox("Coba ambil GeoJSON provinsi dari internet (jika tersedia)?", value=False)
    if remote_try:
        import requests
        # contoh URL publik — jika ingin ganti, ubah di bawah
        candidate_urls = [
            "https://raw.githubusercontent.com/ardian28/GeoJson-Indonesia-38-Provinsi/main/Provinsi/38%20Provinsi%20Indonesia%20-%20Provinsi.json",
            "https://raw.githubusercontent.com/novacept/geojson-indonesia/master/province.json",
        ]
        for url in candidate_urls:
            try:
                st.info(f"Mencoba: {url}")
                r = requests.get(url, timeout=8)
                r.raise_for_status()
                geojson_data = r.json()
                st.success("GeoJSON remote berhasil diambil.")
                break
            except Exception as e:
                st.warning(f"Gagal ambil dari {url}: {e}")
        if geojson_data is None:
            st.error("Gagal mengambil GeoJSON remote. Lanjut ke fallback grafik batang.")

# ---------- helper untuk deteksi property join ----------
def detect_geo_property_key(geojson, sample_prov_name):
    if not geojson or "features" not in geojson:
        return None
    sample = sample_prov_name.lower()
    prop_keys = list(geojson["features"][0].get("properties", {}).keys())
    # coba semua keys, lihat berapa fitur mengandung substring sample
    for key in prop_keys:
        matches = 0
        total = min(40, len(geojson["features"]))
        for feat in geojson["features"][:total]:
            val = feat.get("properties", {}).get(key, "")
            if isinstance(val, str) and sample in val.lower():
                matches += 1
        if matches >= 1:
            return key
    return None

# ---------- Jika folium & geojson tersedia -> choropleth ----------
if FOLIUM_AVAILABLE and geojson_data:
    st.success("Folium tersedia & GeoJSON dimuat — mencoba menampilkan peta choropleth.")
    sample_prov = df[prov_col].dropna().astype(str).iloc[0]
    prop_key = detect_geo_property_key(geojson_data, sample_prov)
    if not prop_key:
        st.warning("Tidak menemukan property GeoJSON yang cocok secara jelas. Akan tampilkan fallback.")
    else:
        try:
            m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles="cartodbpositron")
            # buat choropleth
            folium.Choropleth(
                geo_data=geojson_data,
                name="choropleth",
                data=df,
                columns=[prov_col, jumlah_col],
                key_on=f"feature.properties.{prop_key}",
                fill_color="YlOrRd",
                fill_opacity=0.8,
                line_opacity=0.2,
                legend_name=f"Jumlah kasus ({jumlah_col})",
                nan_fill_color="white",
            ).add_to(m)
            folium.LayerControl().add_to(m)
            st_folium(m, width="100%", height=650)
            st.markdown(
                "**Catatan:** Jika warna/penempatan tidak sesuai, periksa kecocokan nama provinsi antara CSV dan GeoJSON (format/spelling)."
            )
            st.stop()
        except Exception as e:
            st.error(f"Gagal membuat choropleth: {e}")
            # lanjut ke fallback

# ---------- FALLBACK: bar chart per provinsi + tabel ----------
st.info("Menampilkan fallback: chart batang per provinsi (karena Folium/GeoJSON tidak tersedia atau gagal).")

grouped = df.groupby(prov_col)[jumlah_col].sum().sort_values(ascending=False)
st.subheader("Sebaran (Fallback) — Bar chart per provinsi")
# simple chart
st.bar_chart(grouped)

st.markdown("---")
st.subheader("Tabel ringkasan per provinsi")
st.dataframe(grouped.reset_index().rename(columns={prov_col: "Provinsi", jumlah_col: "Jumlah"}), use_container_width=True)

st.markdown(
)