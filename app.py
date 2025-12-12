import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# =========================================================
# DATABASE SETUP
# =========================================================
conn = sqlite3.connect("cashflow.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    kategori TEXT,
    tipe TEXT,
    nominal REAL,
    keterangan TEXT
)
""")
conn.commit()

# =========================================================
# STREAMLIT PAGE
# =========================================================
st.set_page_config(
    page_title="Cashflow Analyzer UMKM",
    layout="wide"
)

st.title("📊 Cashflow Analyzer UMKM")
st.caption("Aplikasi analisis arus kas tanpa upload file — semua input langsung di aplikasi")

# =========================================================
# FORM INPUT TRANSAKSI
# =========================================================

st.subheader("➕ Tambah Transaksi")

with st.form("input_form"):
    tanggal = st.date_input("Tanggal", datetime.now())
    kategori = st.selectbox(
        "Kategori",
        ["Penjualan", "Bahan Baku", "Operasional", "Gaji", "Transportasi", "Lainnya"]
    )
    tipe = st.radio("Tipe Transaksi", ["Pemasukan", "Pengeluaran"])
    nominal = st.number_input("Nominal", min_value=0.0, format="%.2f")
    keterangan = st.text_input("Keterangan", "")

    submit = st.form_submit_button("Tambah")

if submit:
    cursor.execute("""
        INSERT INTO transaksi (tanggal, kategori, tipe, nominal, keterangan)
        VALUES (?, ?, ?, ?, ?)
    """, (str(tanggal), kategori, tipe, nominal, keterangan))
    conn.commit()
    st.success("Transaksi berhasil ditambahkan!")

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_sql_query("SELECT * FROM transaksi", conn)

st.subheader("📄 Data Transaksi")
st.dataframe(df)

# =========================================================
# KPI / METRICS
# =========================================================
st.subheader("📌 Ringkasan Arus Kas")

total_income = df[df['tipe'] == 'Pemasukan']['nominal'].sum()
total_expense = df[df['tipe'] == 'Pengeluaran']['nominal'].sum()
net_cashflow = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Pemasukan", f"Rp {total_income:,.0f}")
col2.metric("Total Pengeluaran", f"Rp {total_expense:,.0f}")
col3.metric("Cashflow Bersih", f"Rp {net_cashflow:,.0f}")

# =========================================================
# VISUALISASI
# =========================================================

if not df.empty:
    # Grafik kategori
    st.subheader("📊 Pengeluaran & Pemasukan per Kategori")

    cat_sum = df.groupby(["kategori", "tipe"])["nominal"].sum().reset_index()
    fig_cat = px.bar(
        cat_sum,
        x="kategori",
        y="nominal",
        color="tipe",
        barmode="group",
        title="Total per Kategori"
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    # Tren bulanan
    st.subheader("📈 Tren Arus Kas Bulanan")
    df['bulan'] = pd.to_datetime(df['tanggal']).dt.to_period('M').astype(str)
    monthly = df.groupby(["bulan", "tipe"])["nominal"].sum().reset_index()

    fig_ts = px.line(
        monthly,
        x="bulan",
        y="nominal",
        color="tipe",
        markers=True,
        title="Tren Arus Kas per Bulan"
    )
    st.plotly_chart(fig_ts, use_container_width=True)

else:
    st.info("Belum ada data transaksi.")

# =========================================================
# REKOMENDASI OTOMATIS
# =========================================================
st.subheader("📝 Rekomendasi Arus Kas (Rule-Based)")

recommend = ""

if total_expense > total_income:
    recommend += "- ⚠️ Arus kas negatif. Pertimbangkan mengurangi biaya operasional.\n"

if "Bahan Baku" in df['kategori'].values:
    bb = df[df['kategori'] == "Bahan Baku"]['nominal'].sum()
    if bb > total_expense * 0.4:
        recommend += "- 🔍 Biaya bahan baku mendominasi, cek efisiensi pembelian.\n"

if recommend == "":
    recommend = "✔ Arus kas dalam kondisi stabil."

st.write(recommend)

# =========================================================
# DOWNLOAD EXPORT
# =========================================================
st.subheader("⬇️ Export Data")

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, file_name="cashflow.csv")
