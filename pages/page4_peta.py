# pages/page4_peta.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from pathlib import Path

st.set_page_config(layout="wide")
st.title("🗺️ Peta Sebaran Kasus Kekerasan terhadap Perempuan")

# --- CONFIG: file/data names ---
CSV_FILE = "data_sebaran_kasus.csv"   # ganti jika nama file berbeda
LOCAL_GEOJSON = "indonesia-provinsi.json"  # file lokal fallback (letakkan di repo)
REMOTE_GEOJSON_URL = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-provinsi.json"

# --- Load dataset ---
if not Path(CSV_FILE).exists():
    st.warning(f"File data '{CSV_FILE}' tidak ditemukan di folder project. Unggah atau simpan file CSV dan refresh.")
    st.stop()

try:
    df = pd.read_csv(CSV_FILE)
except Exception as e:
    st.error(f"Gagal membaca file CSV: {e}")
    st.stop()

st.write("Kolom terdeteksi:", list(df.columns))

# Coba tentukan nama kolom prov/jumlah secara heuristik
def find_col(cols, keywords):
    for k in keywords:
        for c in cols:
            if k.lower() in c.lower():
                return c
    return None

prov_col = find_col(df.columns, ["provinsi", "prov", "cakupan", "region", "nama provinsi"])
jumlah_col = find_col(df.columns, ["jumlah", "kasus", "total", "nilai", "count"])

if prov_col is None or jumlah_col is None:
    st.error("Tidak menemukan kolom provinsi atau jumlah pada file CSV. Silakan pastikan ada kolom nama provinsi dan kolom jumlah/kasus.")
    st.stop()

# normalisasi sederhana
df[prov_col] = df[prov_col].astype(str).str.strip()
df[jumlah_col] = pd.to_numeric(df[jumlah_col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)

st.info(f"Menggunakan kolom provinsi='{prov_col}', jumlah='{jumlah_col}'")

# --- Try load GeoJSON remote (dengan pengecekan) ---
geojson = None
def try_load_remote(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}"
        # cek content-type
        ctype = resp.headers.get("Content-Type", "")
        if "application/json" not in ctype and "application/octet-stream" not in ctype:
            # mungkin HTML page atau redirect
            # tapi kita coba parse anyway with json.loads and handle exception
            try:
                return resp.json(), None
            except Exception as e:
                return None, f"Content-Type tidak JSON ({ctype})"
        # parse json
        return resp.json(), None
    except Exception as e:
        return None, str(e)

with st.spinner("Mengambil GeoJSON provinsi dari internet..."):
    geojson, err = try_load_remote(REMOTE_GEOJSON_URL)

if geojson is None:
    st.warning(f"Gagal mengambil GeoJSON remote: {err}. Mencoba file lokal '{LOCAL_GEOJSON}'...")
    # coba file lokal
    local_path = Path(LOCAL_GEOJSON)
    if local_path.exists():
        try:
            geojson = json.loads(local_path.read_text(encoding="utf-8"))
            st.success(f"Memuat GeoJSON dari file lokal: {LOCAL_GEOJSON}")
        except Exception as e:
            st.error(f"Gagal membaca file GeoJSON lokal: {e}")
            geojson = None
    else:
        st.error("Tidak ditemukan GeoJSON lokal. Untuk menampilkan peta, silakan download GeoJSON provinsi dan simpan sebagai 'indonesia-provinsi.json' di folder project atau pastikan koneksi ke internet dapat mengakses URL GeoJSON.")
        # fallback: tampilkan bar chart
        st.subheader("Sebaran (Fallback) — Bar chart per provinsi")
        top = (df.groupby(prov_col)[jumlah_col].sum()
                 .sort_values(ascending=False).reset_index().rename(columns={prov_col: "Provinsi", jumlah_col: "Jumlah"}))
        st.bar_chart(top.set_index("Provinsi")["Jumlah"])
        st.dataframe(top.head(50))
        st.stop()

# --- At this point geojson is loaded ---
# Karena property pada file geojson bisa berbeda (contoh: 'properties.Propinsi' atau 'properties.PROVINSI' dll)
# Kita cari nama property yang berisi nama provinsi
first_feat = geojson.get("features", [None])[0]
if first_feat is None:
    st.error("Format GeoJSON tidak seperti yang diharapkan (tidak ada features).")
    st.stop()

props = first_feat.get("properties", {})
# cari key yang mengandung 'prov' atau 'name'
prop_key = None
for k in props.keys():
    if "prov" in k.lower() or "name" in k.lower():
        prop_key = k
        break
if prop_key is None:
    # fallback: ambil first property
    prop_key = list(props.keys())[0]

st.write(f"Menghubungkan geojson menggunakan feature property: '{prop_key}' (cocokkan jika perlu)")

# normalisasi nama pada geojson untuk matching
def norm(x):
    return str(x).strip().lower().replace(".", "").replace("  ", " ")

# buat map nama_geo -> feature id
name_to_id = {}
for i, feat in enumerate(geojson["features"]):
    name = feat.get("properties", {}).get(prop_key, "")
    name_to_id[norm(name)] = feat["id"] if "id" in feat else i  # gunakan id jika ada, else index

# normalisasi nama provinsi di df lalu map ke id (jika ada)
df["__prov_norm__"] = df[prov_col].apply(norm)
df["__feature_id__"] = df["__prov_norm__"].map(name_to_id)

# beri pesan jika ada yang tidak cocok
missing = df[df["__feature_id__"].isna()][prov_col].unique().tolist()
if missing:
    st.warning(f"Ada {len(missing)} provinsi pada data yang tidak cocok dengan GeoJSON: {missing[:10]}")
    st.info("Jika jumlahnya sedikit, kamu bisa rename provinsi di CSV agar sesuai (contoh: 'DI Yogyakarta' bukan 'D.I. Yogyakarta').")
    # kita tetap lanjut untuk yang cocok

# pilih baris yang match
df_match = df.dropna(subset=["__feature_id__"]).groupby(["__feature_id__"])[jumlah_col].sum().reset_index()
df_match.columns = ["feature_id", "Jumlah"]

# Prepare choropleth with plotly
# plotly expects locations equal to feature.id or a property value depending on featureidkey.
# Kita prefer feature.id, karena lebih stabil: feature.id harus ada di geojson. Jika tidak ada, kita used index above.
fig = px.choropleth(
    df_match,
    geojson=geojson,
    locations="feature_id",
    color="Jumlah",
    color_continuous_scale="Reds",
    labels={"Jumlah":"Jumlah kasus"},
    title="Sebaran Kasus per Provinsi",
    featureidkey="id"  # menggunakan id property dari fitur geojson
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=700)

st.plotly_chart(fig, use_container_width=True)

# juga tampilkan tabel ringkasan provinsi teratas
st.subheader("Top Provinsi (terurut berdasarkan jumlah kasus)")
topprov = df.groupby(prov_col)[jumlah_col].sum().sort_values(ascending=False).reset_index()
st.table(topprov.head(20).rename(columns={prov_col:"Provinsi", jumlah_col:"Jumlah"}))
