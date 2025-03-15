import pandas as pd
from datetime import datetime, timedelta

# Path file CSV untuk menyimpan data
STATUS_CSV = "status_pesanan.csv"
MAKANAN_CSV = "makanan.csv"
TRACK_CSV = "track_makanan.csv"

# Fungsi untuk membaca CSV dengan penanganan jika file tidak ada
def read_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame()

def ubah_status(order_id: int):
    df = read_csv(STATUS_CSV)
    if df.empty or order_id not in df["id_order"].values:
        return "Order ID tidak ditemukan atau waktu tidak tersedia"
    
    waktu_pesan = pd.to_datetime(df.loc[df["id_order"] == order_id, "waktu_makanan_masuk"].values[0])
    waktu_sekarang = datetime.now()
    selisih_menit = (waktu_sekarang - waktu_pesan).total_seconds() / 60
    
    if selisih_menit >= 25:
        status_pesanan = "Pesanan anda dimakan kurir kebenaran"
    elif selisih_menit >= 20:
        status_pesanan = "Pesanan anda Diantar kurir Kebenaran"
    elif selisih_menit >= 15:
        status_pesanan = "Pesanan anda sedang Menunggu kurir Kebenaran mengambil"
    elif selisih_menit >= 10:
        status_pesanan = "Pesanan anda Sedang dimasak oleh enchef Bagaga"
    else:
        status_pesanan = "Pesanan anda sudah diterima pihak Bagogo"
    
    df.loc[df["id_order"] == order_id, "status_pesanan_cs"] = status_pesanan
    df.to_csv(STATUS_CSV, index=False)
    print(f'\n\n=================| {status_pesanan} |=====================\n\n')

def get_order_status(order_id: int):
    ubah_status(order_id)
    df = read_csv(STATUS_CSV)
    if order_id in df["id_order"].values:
        return df.loc[df["id_order"] == order_id, "status_pesanan_cs"].values[0]
    return "Order ID tidak ditemukan"

def get_harga_makanan(nama_makanan: str, jumlah_item: int):
    df = read_csv(MAKANAN_CSV)
    harga = df.loc[df["nama_makanan"].str.lower() == nama_makanan.lower(), "harga"].values
    return int(harga[0]) * jumlah_item if len(harga) > 0 else "Makanan tidak ditemukan"

def get_id_makanan(nama_makanan: str):
    df = read_csv(MAKANAN_CSV)
    id_makanan = df.loc[df["nama_makanan"].str.lower() == nama_makanan.lower(), "id_makanan"].values
    return id_makanan[0] if len(id_makanan) > 0 else "Makanan tidak ditemukan"

def get_list_makanan():
    df = read_csv(MAKANAN_CSV)
    return df["nama_makanan"].tolist() if not df.empty else []

def get_total_biaya(id_order: int):
    df = read_csv(TRACK_CSV)
    return df.loc[df["id_order"] == id_order, "total_harga"].sum() if not df.empty else 0

def get_max_id():
    df = read_csv(TRACK_CSV)
    return df["id_order"].max() + 1 if not df.empty else 1

def input_makanan_track(id_order, id_makanan, jumlah, total_harga):
    df = read_csv(TRACK_CSV)
    new_data = pd.DataFrame([{ "id_order": id_order, "id_makanan": id_makanan, "jumlah": jumlah, "total_harga": total_harga }])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(TRACK_CSV, index=False)

def input_status_makanan_track(id_order):
    df = read_csv(STATUS_CSV)
    new_data = pd.DataFrame([{ "id_order": id_order, "status_pesanan_cs": "Pesanan sudah diterima pihak Bagogo", "waktu_makanan_masuk": datetime.now() }])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(STATUS_CSV, index=False)
