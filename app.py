from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import requests
import logging
import time
import threading
import os
import db_helper
import regex_helper

app = FastAPI()
inprogress_orders = {}

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Root endpoint untuk menghindari error 405
@app.get("/")
def home():
    return {"message": "FastAPI is running!"}

# Fungsi untuk menjaga API tetap online
def keep_alive():
    while True:
        try:
            requests.get("https://chatbot-diagflow2.onrender.com/")
        except Exception as e:
            logging.error(f"Keep-alive error: {e}")
        time.sleep(200)  # Ping setiap 3 menit 20 detik

# Jalankan keep-alive hanya di lokal
@app.on_event("startup")
def startup_event():
    if "RENDER" not in os.environ:  # Render punya environment variable ini
        threading.Thread(target=keep_alive, daemon=True).start()

@app.post("/")
async def handle_req(request: Request):
    try:
        payload = await request.json()
        parameter = payload['queryResult']['parameters']
        intent_name = payload['queryResult']["intent"]['displayName']
        outputContexts = payload['queryResult']['outputContexts']

        sesion_id_raw = outputContexts[0]['name']
        sesion_id = regex_helper.get_sesion(sesion_id_raw)
        logging.info(f"Session ID: {sesion_id}")

        intent_handler_dict = {
            'add.order-contexts:ongoing-order': add_to_order,
            'order.complate-contexts :ongoing-order': complete_order,
            'lacak_id-trackorder': track_order
        }

        if not sesion_id:
            logging.error("Session ID kosong. Tidak dapat memproses permintaan.")
            return JSONResponse(content={"fulfillmentText": "Terjadi kesalahan, sesi tidak valid. Coba lagi nanti."})
        
        logging.info("Session ID valid. Memproses permintaan.")
        return intent_handler_dict[intent_name](parameter, sesion_id)

    except Exception as e:
        logging.error(f"Error pada request: {e}")
        return JSONResponse(content={"fulfillmentText": "Terjadi kesalahan pada server. Coba lagi nanti."})

def complete_order(parameter: dict, sesion_id: str):
    global inprogress_orders
    semua_pesanan = regex_helper.pesanan(inprogress_orders[sesion_id])
    makanan_dipesan = inprogress_orders[sesion_id]

    id_max = db_helper.get_max_id()
    
    for nama_makanan, jumlah_makanan in makanan_dipesan.items():
        harga_total = db_helper.get_harga_makanan(nama_makanan, jumlah_makanan)
        id_makanan = db_helper.get_id_makanan(nama_makanan)

        logging.info(f"{id_makanan} jumlah {jumlah_makanan} total {harga_total}")
        db_helper.input_makanan_track(id_max, id_makanan, jumlah_makanan, harga_total)

    db_helper.input_status_makanan_track(id_max)
    inprogress_orders.pop(sesion_id, None)

    return JSONResponse(content={"fulfillmentText": f"Pesanan Anda telah kami terima {semua_pesanan} dan sedang diproses. Ini nomor pesanan Anda: {id_max}"})

def add_to_order(parameter, sesion_id):
    global inprogress_orders

    list_nama_makanan_db = db_helper.get_list_makanan()
    list_jumlah = parameter["number"]
    list_nama_makanan = parameter['food_item']

    list_nama_makanan_db_lower = [item.lower() for item in list_nama_makanan_db]
    list_nama_makanan_lower = [item.lower() for item in list_nama_makanan]

    makanan_tidak_valid = len([item for item in list_nama_makanan_lower if item not in list_nama_makanan_db_lower]) > 0

    if len(list_jumlah) != len(list_nama_makanan) or makanan_tidak_valid:
        return JSONResponse(content={"fulfillmentText": "Pastikan pesanan Anda sudah tepat"})
    
    order_dict = dict(zip(list_nama_makanan_lower, map(int, list_jumlah)))
    if sesion_id not in inprogress_orders:
        inprogress_orders[sesion_id] = order_dict
    else:
        inprogress_orders[sesion_id] = regex_helper.tambahkan(inprogress_orders[sesion_id], order_dict)

    semua_pesanan = regex_helper.pesanan(inprogress_orders[sesion_id])
    return JSONResponse(content={"fulfillmentText": f"Pesanan Anda telah dicatat {semua_pesanan}. Ada lagi pesanan?"})

def track_order(parameter, sesion_id: str):
    number_value = parameter["number"]
    saat_ini = db_helper.get_order_status(number_value)

    if saat_ini == 'Order ID tidak ditemukan':
        return JSONResponse(content={"fulfillmentText": f"{saat_ini}"})
    
    biaya = db_helper.get_total_biaya(number_value)
    
    if saat_ini == "Pesanan anda dimakan kurir kebenaran":
        pesanan = "Maaf, pesanan Anda dimakan kurir kebenaran."
    else:
        pesanan = (f"Status pesanan untuk nomor pesanan {int(number_value)} : \n{saat_ini} "
                   f"dengan total Rp {regex_helper.format(int(biaya))} \n\n"
                   "Selamat! Anda adalah pelanggan beruntung.\n"
                   f"Anda mendapatkan diskon spesial, jadi Anda hanya perlu membayar Rp {regex_helper.format(int(biaya)-1000)}.")

    return JSONResponse(content={"fulfillmentText": pesanan})

@app.get("/ping")
def ping():
    return {"message": "I'm alive!"}
