import streamlit as st
import pandas as pd
import altair as alt

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(
    page_title="Sebaran Kasus Kekerasan Perempuan",
    layout="wide"
)

# ============================
# JUDUL UTAMA
# ============================
st.title("📊 Sebaran Kasus Kekerasan Perempuan")
st.caption("Data berdasarkan jumlah kasus & jumlah korban per provinsi di Indonesia")

# ============================
# 1. LOAD DATA
# ============================
df = pd.read_csv("data_sebaran_kasus.csv", sep=None, engine="python")

# Hapus baris total nasional
df = df[df["Cakupan"] != "INDONESIA"]

prov_col = "Cakupan"
kasus = "Jumlah Kasus (Kasus)"
korban = "Jumlah Korban (Orang)"

# Cleaning angka
for col in [kasus, korban]:
    df[col] = (
        df[col].astype(str)
        .str.replace(",", "")
        .str.extract(r"(\d+)")
        .astype(float)
    )

# ============================
# 2. SUMMARY STATISTICS
# ============================
total_kasus = int(df[kasus].sum())
total_korban = int(df[korban].sum())
prov_tertinggi_kasus = df.sort_values(kasus, ascending=False).iloc[0]
prov_tertinggi_korban = df.sort_values(korban, ascending=False).iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Kasus", f"{total_kasus:,}")
col2.metric("Total Korban", f"{total_korban:,}")
col3.metric("Provinsi dengan Kasus Tertinggi", prov_tertinggi_kasus[prov_col])
col4.metric("Jumlah Kasus Tertinggi", f"{int(prov_tertinggi_kasus[kasus]):,}")

st.markdown("---")

# ============================
# 3. BAR CHART — KASUS PER PROVINSI
# ============================
st.subheader("📈 Jumlah Kasus per Provinsi")

chart_kasus = alt.Chart(df).mark_bar().encode(
    x=alt.X(prov_col, sort='-y', title="Provinsi"),
    y=alt.Y(kasus, title="Jumlah Kasus"),
    tooltip=[prov_col, kasus]
).properties(height=350)

st.altair_chart(chart_kasus, use_container_width=True)

# ============================
# 4. BAR CHART — KORBAN PER PROVINSI
# ============================
st.subheader("📉 Jumlah Korban per Provinsi")

chart_korban = alt.Chart(df).mark_bar(color="salmon").encode(
    x=alt.X(prov_col, sort='-y', title="Provinsi"),
    y=alt.Y(korban, title="Jumlah Korban"),
    tooltip=[prov_col, korban]
).properties(height=350)

st.altair_chart(chart_korban, use_container_width=True)

st.markdown("---")

# ============================
# 5. PIE CHART — TOP 10 PROVINSI
# ============================
st.subheader("🍩 10 Provinsi dengan Kasus Tertinggi")

df_top10 = df.sort_values(kasus, ascending=False).head(10)

pie = alt.Chart(df_top10).mark_arc().encode(
    theta=alt.Theta(kasus, type="quantitative"),
    color=alt.Color(prov_col, legend=None),
    tooltip=[prov_col, kasus]
).properties(
    width=300,
    height=300
)

st.altair_chart(pie, use_container_width=False)

st.markdown("---")

# ============================
# 6. DATA TABLE
# ============================
st.subheader("📄 Tabel Lengkap — Sebaran Kasus Kekerasan Perempuan per Provinsi")

st.dataframe(
    df.sort_values(kasus, ascending=False).reset_index(drop=True),
    use_container_width=True
)

# Download Button
csv = df.to_csv(index=False)
st.download_button("⬇ Download Data CSV", csv, "sebaran_kekerasan_perempuan.csv", "text/csv")
