import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Sebaran Kasus", layout="wide")
st.title("📊 Dashboard Sebaran Kasus Kekerasan Terhadap Perempuan")

# ==========================================================
# 1. LOAD DATA
# ==========================================================
CSV_PATH = "data_sebaran_kasus.csv"
df = pd.read_csv(CSV_PATH, sep=None, engine="python")

prov_col = "Cakupan"
jumlah_col = df.columns[2]  # kolom jumlah kasus

# Bersihkan angka
df[jumlah_col] = (
    df[jumlah_col].astype(str)
    .str.replace(",", "")
    .str.replace(".", "", regex=False)
    .str.extract(r"(\d+)", expand=False)
)
df[jumlah_col] = pd.to_numeric(df[jumlah_col], errors="coerce").fillna(0)

# ==========================================================
# 2. RINGKASAN STATISTIK
# ==========================================================
total_kasus = df[jumlah_col].sum()
prov_tertinggi = df.sort_values(jumlah_col, ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric("Total Kasus", f"{total_kasus:,}")
col2.metric("Provinsi Tertinggi", prov_tertinggi[prov_col])
col3.metric("Jumlah Pada Provinsi Tertinggi", f"{prov_tertinggi[jumlah_col]:,}")

st.markdown("---")

# ==========================================================
# 3. GRAFIK BATANG PER PROVINSI
# ==========================================================
st.subheader("📈 Grafik Kasus per Provinsi")

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X(prov_col, sort='-y', title="Provinsi"),
    y=alt.Y(jumlah_col, title="Jumlah Kasus"),
    tooltip=[prov_col, jumlah_col]
).properties(
    width="container",
    height=400
)

st.altair_chart(chart, use_container_width=True)

st.markdown("---")

# ==========================================================
# 4. PIE CHART 10 PROVINSI TERBESAR
# ==========================================================
st.subheader("🍩 10 Provinsi Dengan Kasus Tertinggi")

df_top10 = df.sort_values(jumlah_col, ascending=False).head(10)

pie = alt.Chart(df_top10).mark_arc().encode(
    theta=alt.Theta(jumlah_col, type="quantitative"),
    color=alt.Color(prov_col, legend=None),
    tooltip=[prov_col, jumlah_col]
).properties(
    width=300,
    height=300
)

st.altair_chart(pie, use_container_width=False)

st.markdown("---")

# ==========================================================
# 5. TABEL INTERAKTIF
# ==========================================================
st.subheader("📄 Tabel Sebaran Kasus per Provinsi")

st.dataframe(
    df.sort_values(jumlah_col, ascending=False).reset_index(drop=True),
    use_container_width=True
)
