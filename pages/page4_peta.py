# pages/page4_peta.py
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(layout="wide")
st.title("🗺️ Peta Sebaran Kasus Kekerasan terhadap Perempuan")

# -------------------------
# Cek apakah folium & st_folium tersedia (tidak memaksa user install)
# -------------------------
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

# -------------------------
# Baca dataset lokal (pastikan file ada di project)
# -------------------------
CSV_PATH = "data_sebaran_kasus.csv"  # nama file kamu
if not os.path.exists(CSV_PATH):
    st.error(
        f"File data tidak ditemukan: `{CSV_PATH}`. "
        "Letakkan file CSV (mis: data_sebaran_kasus.csv) di folder project atau unggah di halaman Visualisasi."
    )
    st.stop()

df = pd.read_csv(CSV_PATH)

st.subheader("Kolom terdeteksi:")
st.json(list(df.columns))

# -------------------------
# Cari kolom provinsi & jumlah (heuristik sederhana)
# -------------------------
def find_col(cols, keywords):
    cols_lower = [c.lower() for c in cols]
    for k in keywords:
        if k.lower() in cols_lower:
            return cols[cols_lower.index(k.lower())]
    # substring match
    for c in cols:
        for k in keywords:
            if k.lower() in c.lower():
                return c
    return None

prov_candidates = ["provinsi", "prov", "cakupan", "nama provinsi", "region", "wilayah"]
jumlah_candidates = ["jumlah", "kasus", "total", "nilai", "korban"]

prov_col = find_col(df.columns, prov_candidates)
jumlah_col = find_col(df.columns, jumlah_candidates)

if not prov_col or not jumlah_col:
    st.warning("Tidak menemukan kolom provinsi atau kolom jumlah/kasus secara otomatis.")
    st.info("Periksa nama kolom CSV-mu atau ubah nama kolom agar mengandung kata 'provinsi' dan 'jumlah' / 'kasus'.")
    # tapi kita tetap coba menampilkan tabel
    st.subheader("Tabel sumber (preview)")
    st.dataframe(df.head(30), use_container_width=True)
    st.stop()

# Bersihkan jumlah jadi numeric
df[jumlah_col] = pd.to_numeric(df[jumlah_col].astype(str).str.replace(",", "").str.strip(), errors="coerce")
df = df.dropna(subset=[prov_col])  # hapus baris tanpa provinsi

# -------------------------
# Coba load GeoJSON lokal
# -------------------------
GEOJSON_LOCAL = "indonesia-provinsi.json"
geojson_data = None
if os.path.exists(GEOJSON_LOCAL):
    try:
        with open(GEOJSON_LOCAL, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
    except Exception as e:
        st.warning(f"Gagal membaca GeoJSON lokal `{GEOJSON_LOCAL}`: {e}")
else:
    st.info(f"GEOJSON lokal tidak ditemukan: `{GEOJSON_LOCAL}`. Jika ingin peta choropleth, simpan GeoJSON provinsi dengan nama tersebut di folder project.")

# -------------------------
# Helper: cari property GeoJSON yang cocok untuk join (heuristik)
# -------------------------
def detect_geo_property_key(geojson, sample_prov_name):
    """
    Mencari property key di feature.properties yang mengandung substring dari nama provinsi sample.
    Kembalikan string property key (mis: 'propinsi', 'NAME_1', dsb.) atau None.
    """
    if not geojson or "features" not in geojson:
        return None
    features = geojson["features"]
    if not features:
        return None
    # ambil candidate keys dari properties pertama
    prop_keys = list(features[0].get("properties", {}).keys())
    sample = sample_prov_name.lower()
    for key in prop_keys:
        # lihat apakah banyak fitur yang punya nilai mirip sample (heuristik)
        matches = 0
        total = min(40, len(features))
        for feat in features[:total]:
            val = feat.get("properties", {}).get(key, "")
            if isinstance(val, str) and sample in val.lower():
                matches += 1
        # jika ditemukan beberapa match, pilih kunci ini
        if matches >= 1:
            return key
    return None

# -------------------------
# Jika folium tersedia dan geojson ada -> buat choropleth
# -------------------------
if FOLIUM_AVAILABLE and geojson_data:
    st.success("Folium tersedia — mencoba membuat peta choropleth.")
    # ambil contoh provinsi dari data untuk mendeteksi key property
    sample_prov = str(df[prov_col].dropna().iloc[0])
    prop_key = detect_geo_property_key(geojson_data, sample_prov)
    if not prop_key:
        st.warning(
            "Tidak menemukan property GeoJSON yang jelas cocok dengan nama provinsi. "
            "Mungkin nama provinsi di GeoJSON berbeda format. Akan ditampilkan fallback (bar chart)."
        )
    else:
        # buat peta Folium
        m = folium.Map(location=[-2.5, 118], zoom_start=5)
        # gabungkan data: gunakan key_on seperti feature.properties.<prop_key>
        key_on = f"feature.properties.{prop_key}"
        # buat choropleth
        try:
            folium.Choropleth(
                geo_data=geojson_data,
                data=df,
                columns=[prov_col, jumlah_col],
                key_on=key_on,
                fill_color="YlOrRd",
                fill_opacity=0.8,
                line_opacity=0.2,
                nan_fill_color="white",
                legend_name=f"Jumlah kasus ({jumlah_col})"
            ).add_to(m)
            st_folium(m, width=900, height=550)
            st.markdown("**Catatan:** Jika warna tidak tepat, periksa kecocokan penamaan provinsi antara CSV dan GeoJSON.")
            st.stop()
        except Exception as e:
            st.error(f"Gagal membuat choropleth: {e}")
            # jatuhkan ke fallback di bawah

# -------------------------
# FALLBACK: tampilkan bar chart per provinsi + tabel
# -------------------------
st.info("Menampilkan fallback: chart batang per provinsi (karena Folium/GeoJSON tidak tersedia atau gagal).")

grouped = df.groupby(prov_col)[jumlah_col].sum().sort_values(ascending=False)
st.subheader("Sebaran (Fallback) — Bar chart per provinsi")
# gunakan st.bar_chart (simple) atau altair untuk label
st.bar_chart(grouped)

st.markdown("---")
st.subheader("Tabel ringkasan per provinsi")
st.dataframe(grouped.reset_index().rename(columns={prov_col: "Provinsi", jumlah_col: "Jumlah"}), use_container_width=True)

st.markdown(
    """
