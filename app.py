import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cashflow UMKM", layout="wide")

# ------------------------------------------------------------------
# Inisialisasi session state untuk transaksi
# ------------------------------------------------------------------
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Tanggal", "Kategori", "Tipe", "Nominal", "Keterangan"]
    )

# ------------------------------------------------------------------
# Judul Aplikasi
# ------------------------------------------------------------------
st.title("📊 Cashflow UMKM Dashboard")
st.write("Aplikasi pencatatan keuangan sederhana untuk UMKM.")

# ------------------------------------------------------------------
# Form Input Transaksi
# ------------------------------------------------------------------
st.subheader("➕ Tambah Transaksi")

with st.form("input_form"):
    tanggal = st.date_input("Tanggal Transaksi")
    kategori = st.selectbox("Kategori", ["Penjualan", "Bahan Baku", "Operasional", "Gaji", "Transportasi", "Lainnya"])
    tipe = st.selectbox("Tipe Transaksi", ["Pemasukan", "Pengeluaran"])
    nominal = st.number_input("Nominal", min_value=0, step=1000)
    keterangan = st.text_input("Keterangan")

    submitted = st.form_submit_button("Tambah Transaksi")

    if submitted:
        new_data = {
            "Tanggal": tanggal,
            "Kategori": kategori,
            "Tipe": tipe,
            "Nominal": nominal,
            "Keterangan": keterangan
        }
        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, pd.DataFrame([new_data])],
            ignore_index=True
        )
        st.success("Transaksi berhasil ditambahkan!")
        st.rerun()

# ------------------------------------------------------------------
# Dashboard Ringkasan
# ------------------------------------------------------------------
st.subheader("📌 Ringkasan Cashflow")

df = st.session_state.transactions

if not df.empty:
    pemasukan = df[df["Tipe"] == "Pemasukan"]["Nominal"].sum()
    pengeluaran = df[df["Tipe"] == "Pengeluaran"]["Nominal"].sum()
    saldo = pemasukan - pengeluaran

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Pemasukan", f"Rp {pemasukan:,.0f}")
    col2.metric("Total Pengeluaran", f"Rp {pengeluaran:,.0f}")
    col3.metric("Cashflow Bersih", f"Rp {saldo:,.0f}")

    # ------------------------------------------------------------------
    # Grafik Cashflow Bulanan
    # ------------------------------------------------------------------
    st.subheader("📈 Grafik Cashflow Bulanan")

    df_chart = df.copy()
    df_chart["Tanggal"] = pd.to_datetime(df_chart["Tanggal"])
    df_chart["Bulan"] = df_chart["Tanggal"].dt.to_period("M").astype(str)

    monthly_summary = df_chart.groupby(["Bulan", "Tipe"])["Nominal"].sum().reset_index()

    fig = px.bar(
        monthly_summary,
        x="Bulan",
        y="Nominal",
        color="Tipe",
        barmode="group",
        title="Pemasukan vs Pengeluaran per Bulan"
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Belum ada data untuk ditampilkan.")

# ------------------------------------------------------------------
# Tabel Transaksi + Hapus Transaksi
# ------------------------------------------------------------------
st.subheader("📋 Daftar Transaksi")

if not df.empty:
    st.dataframe(df, use_container_width=True)

    st.write("### 🗑 Hapus Transaksi")

    index_list = df.index.tolist()
    delete_index = st.selectbox(
        "Pilih transaksi yang ingin dihapus berdasarkan index:",
        index_list
    )

    if st.button("Hapus Transaksi Ini"):
        st.session_state.transactions = df.drop(delete_index).reset_index(drop=True)
        st.success("Transaksi berhasil dihapus!")
        st.rerun()

    # Tombol hapus semua
    st.warning("Hapus Semua Transaksi")
    if st.button("HAPUS SEMUA"):
        st.session_state.transactions = st.session_state.transactions.iloc[0:0]
        st.error("Semua transaksi berhasil dihapus!")
        st.rerun()

else:
    st.info("Belum ada transaksi tercatat.")
