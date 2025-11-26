
# pages/page2.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Visualisasi Data", page_icon="📊", layout="wide")

st.title("📊 Visualisasi Data — Tabel & Grafik")

# 1) Ambil dataframe: session -> local files -> uploader
df = None
if "data" in st.session_state:
    df = st.session_state["data"]
else:
    for candidate in ["data_kekerasan_perempuan.csv", "pages/data_kekerasan_perempuan.csv"]:
        if os.path.exists(candidate):
            try:
                df = pd.read_csv(candidate)
                st.info(f"Membaca data dari: {candidate}")
                st.session_state["data"] = df
                break
            except Exception:
                try:
                    df = pd.read_excel(candidate)
                    st.info(f"Membaca Excel dari: {candidate}")
                    st.session_state["data"] = df
                    break
                except Exception:
                    df = None

if df is None:
    st.warning("Data belum tersedia. Unggah file di halaman Input Data atau letakkan 'data_kekerasan_perempuan.csv' di folder project.")
    st.stop()

# 2) Tampilkan kolom asli singkat (helpful)
st.markdown("**Kolom asli:**")
st.write(df.columns.tolist())

# 3) Jika wide (banyak kolom numeric), ubah ke long
# Cari provinsi / cakupan
cols_lower = [c.lower() for c in df.columns]
prov_candidates = ["cakupan", "provinsi", "prov", "nama provinsi", "wilayah", "region"]
prov_col = None
for p in prov_candidates:
    if p in cols_lower:
        prov_col = df.columns[cols_lower.index(p)]
        break

if prov_col is None:
    # fallback: pilih first non-numeric column
    non_num = df.select_dtypes(exclude="number").columns.tolist()
    prov_col = non_num[0] if non_num else None

# Tentukan kolom numeric (jenis kekerasan)
exclude_cols = {prov_col, "no", "satuan"} if prov_col else {"no", "satuan"}
numeric_cols = []
for c in df.columns:
    if c in exclude_cols:
        continue
    # treat as numeric if dtype numeric or convertible
    try:
        pd.to_numeric(df[c].dropna().astype(str).str.replace(",", "").str.strip(), errors="raise")
        numeric_cols.append(c)
    except Exception:
        pass

# If numeric columns look like types (wide), melt
if len(numeric_cols) >= 1:
    # remove possible total row (INDONESIA)
    if prov_col and prov_col in df.columns:
        df = df[~df[prov_col].astype(str).str.strip().str.upper().eq("INDONESIA")]
        df = df[~df[prov_col].astype(str).str.strip().str.lower().isin(["no", ""])]
    id_vars = [prov_col] if prov_col else []
    df_long = df.melt(id_vars=id_vars, value_vars=numeric_cols, var_name="Jenis", value_name="Jumlah")
    if prov_col:
        df_long = df_long.rename(columns={prov_col: "Provinsi"})
    else:
        df_long = df_long.rename(columns={id_vars[0]: "Provinsi"} if id_vars else {"variable": "Provinsi"})
    df_long["Jumlah"] = pd.to_numeric(df_long["Jumlah"].astype(str).str.replace(",", "").str.strip(), errors="coerce")
    # jika tidak ada kolom Tahun, kita asumsikan data satu tahun; tambahkan Tahun default 2024
    if "Tahun" not in df_long.columns and "tahun" not in cols_lower:
        df_long["Tahun"] = 2024
    df = df_long.copy()
else:
    # dataset mungkin sudah long; usahakan rename kolom penting ke standar
    cols = df.columns.tolist()
    def find_col(columns, keywords):
        for k in keywords:
            for c in columns:
                if k.lower() in c.lower():
                    return c
        return None
    prov_guess = find_col(cols, ["provinsi","cakupan","prov","region"])
    jumlah_guess = find_col(cols, ["jumlah","kasus","total","nilai","count"])
    jenis_guess = find_col(cols, ["jenis","kekerasan","kategori","type"])
    if prov_guess and prov_guess != "Provinsi":
        df = df.rename(columns={prov_guess: "Provinsi"})
    if jumlah_guess and jumlah_guess != "Jumlah":
        df = df.rename(columns={jumlah_guess: "Jumlah"})
    if jenis_guess and jenis_guess != "Jenis":
        df = df.rename(columns={jenis_guess: "Jenis"})
    # ensure numeric
    if "Jumlah" in df.columns:
        df["Jumlah"] = pd.to_numeric(df["Jumlah"].astype(str).str.replace(",", "").str.strip(), errors="coerce")
    if "Tahun" not in df.columns:
        df["Tahun"] = 2024

# final minimal cleaning
df = df.dropna(subset=["Provinsi", "Jenis", "Jumlah"], how='any')
df["Provinsi"] = df["Provinsi"].astype(str).str.strip()

# save back to session
st.session_state["data"] = df

# --- UI: pilihan grafik & filters (minimal) ---
st.markdown("---")
st.subheader("Filter dan Visualisasi")

# filter provinsi & jenis
prov_options = sorted(df["Provinsi"].unique())
jenis_options = sorted(df["Jenis"].unique())

sel_prov = st.multiselect("Pilih provinsi (kosong = semua)", options=prov_options)
sel_jenis = st.multiselect("Pilih jenis (kosong = semua)", options=jenis_options)

df_vis = df.copy()
if sel_prov:
    df_vis = df_vis[df_vis["Provinsi"].isin(sel_prov)]
if sel_jenis:
    df_vis = df_vis[df_vis["Jenis"].isin(sel_jenis)]

if df_vis.empty:
    st.warning("Hasil filter kosong. Pilih opsi lain atau hapus filter.")
    st.stop()

# tampilkan tabel ringkas (preview)
st.markdown("---")
st.subheader("Tabel Data (preview)")
st.dataframe(df_vis.reset_index(drop=True), use_container_width=True)

# --- Grafik ---
st.markdown("---")
st.subheader("Grafik")

chart_type = st.selectbox("Pilih jenis grafik", [
    "Bar per Provinsi (untuk 1 jenis)",
    "Stacked Bar per Provinsi (semua jenis)",
    "Pie: Distribusi jenis (total)"])

if chart_type == "Bar per Provinsi (untuk 1 jenis)":
    jenis_for_bar = st.selectbox("Pilih jenis untuk bar chart", options=jenis_options)
    plot_df = df_vis[df_vis["Jenis"] == jenis_for_bar].groupby("Provinsi")["Jumlah"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(plot_df.index.astype(str), plot_df.values)
    ax.set_xlabel("Provinsi")
    ax.set_ylabel("Jumlah Kasus")
    ax.set_title(f"Jumlah kasus jenis '{jenis_for_bar}' per Provinsi")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

elif chart_type == "Stacked Bar per Provinsi (semua jenis)":
    stacked = df_vis.groupby(["Provinsi","Jenis"])["Jumlah"].sum().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(12,6))
    stacked.plot(kind="bar", stacked=True, ax=ax)
    ax.set_xlabel("Provinsi")
    ax.set_ylabel("Jumlah Kasus")
    ax.set_title("Jumlah kasus per Provinsi menurut Jenis (Stacked)")
    plt.xticks(rotation=45)
    st.pyplot(fig)

elif chart_type == "Pie: Distribusi jenis (total)":
    dist = df_vis.groupby("Jenis")["Jumlah"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7,7))
    ax.pie(dist.values, labels=dist.index.astype(str), autopct="%1.1f%%")
    ax.set_title("Distribusi jenis kekerasan (dari dataset)")
    st.pyplot(fig)

st.markdown("---")
st.caption("Catatan: grafik dibuat dari data yang dipilih. Pastikan kolom numeric di CSV tidak berisi karakter non-digit (koma sepah ribuan atau spasi).")




