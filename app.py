from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import logging

import db_helper
import regex_helper


app = FastAPI()
inprogress_orders = {}
cek="\n\n\n\n\n\n===========================================================\n\n\n\\n\n\n\n"


# Konfigurasi logging untuk debugging
logging.basicConfig(level=logging.INFO)


@app.post("/")  # Ubah ke POST karena membaca JSON dari request body
async def handle_req(request: Request):
    
    try:
        payload = await request.json()  # Mendapatkan JSON dari request

        # Mengambil intent dan parameter jika tersedia
        

        parameter=payload['queryResult']['parameters']
        
        intent_name=payload['queryResult']["intent"]['displayName']
        outputContexts=payload['queryResult']['outputContexts']

        sesion_id_raw=outputContexts[0]['name']

        sesion_id=regex_helper.get_sesion(sesion_id_raw)
        logging.error(f"sesion id adalah{sesion_id}")

        intent_handler_dict = {
        'add.order-contexts:ongoing-order': add_to_order,
        # 'order.remove - context: ongoing-order': remove_from_order,
        'order.complate-contexts :ongoing-order': complete_order,
        'lacak_id-trackorder': track_order
    }
        if not sesion_id:
            logging.error("Session ID kosong. Tidak dapat memproses permintaan.")
            return JSONResponse(content={"fulfillmentText": "Terjadi kesalahan, sesi tidak valid. Coba lagi nanti."})
        else:
            logging.error("Session ID Ada. memproses permintaan.")
        return intent_handler_dict[intent_name](parameter,sesion_id)



    except Exception as e:
        logging.error(f"Error pada request: {e}")
        # intent_name=payload['queryResult']["intent"]['displayName']
        return JSONResponse(content={f"fulfillmentText: Terjadi kesalahan pada server. Coba lagi nanti. {intent_name}"})
        # return JSONResponse(content={f"fulfillmentText": "Terjadi kesalahan pada server. Coba lagi nanti.{in}"})



def complete_order(parameter:dict,sesion_id:str):
        global inprogress_orders 
        #logging.error(cek)
        semua_pesanan=regex_helper.pesanan(inprogress_orders[sesion_id])
        makanan_dipesan=inprogress_orders[sesion_id]
       
        

        id_max=db_helper.get_max_id()
       
        for nama_makanan, jumlah_makanan in makanan_dipesan.items():
            harga_total=db_helper.get_harga_makanan(nama_makanan,jumlah_makanan)
            id_makanan=db_helper.get_id_makanan(nama_makanan,jumlah_makanan)

         


            logging.error(f"{id_makanan} jumlah {jumlah_makanan} total {harga_total}")
            db_helper.input_makanan_track(id_max,id_makanan,jumlah_makanan,harga_total)

        db_helper.input_status_makanan_track(id_max)
        inprogress_orders=inprogress_orders.pop(sesion_id)



        
        
        return JSONResponse(content={"fulfillmentText": f"Baik! Pesanan Anda telah kami terima {semua_pesanan} dan sedang diproses. Terima kasih telah memesan di Warung Sate Pak Bagogo! ini nomer pesanan anda : {id_max}"})


def add_to_order(parameter,sesion_id):
    global inprogress_orders 

    #raw data
    list_nama_makanan_db=db_helper.get_list_makanan()
    list_jumlah=parameter["number"]
    list_nama_makanan=parameter['food_item']

    #data_makanan lower
    list_nama_makanan_db_lower = [item.lower() for item in list_nama_makanan_db]
    list_nama_makanan_lower = [item.lower() for item in list_nama_makanan]

    # Cek apakah ada makanan yang tidak ada dalam database (case-insensitive)
    makanan_tidak_valid =len( [item for item in list_nama_makanan_lower if item not in list_nama_makanan_db_lower])>0

    #cek apakah valid tidak valid??
    if len(list_jumlah) != len(list_nama_makanan) or makanan_tidak_valid:
        return JSONResponse(content={"fulfillmentText": f" pastikan pesanan anda sudah tepat"})
    
    #valid
    else:
        order_dict = dict(zip(list_nama_makanan_lower, map(int, list_jumlah)))
        if sesion_id not in inprogress_orders:
            inprogress_orders[sesion_id] = order_dict
        else:
            inprogress_orders[sesion_id] = regex_helper.tambahkan(inprogress_orders[sesion_id], order_dict)
        semua_pesanan = regex_helper.pesanan(inprogress_orders[sesion_id])



        return JSONResponse(content={"fulfillmentText": f"pesanan anda telah saya catat {semua_pesanan} ada lagi pesanan"})




def track_order(parameter,sesion_id:str):
    number_value =parameter["number"]
    saat_ini = db_helper.get_order_status(number_value)  # Ambil status dari database
    # logging.info(f"Status order {number_value}: {saat_ini}")
    if saat_ini=='Order ID tidak ditemukan':
        return JSONResponse(content={"fulfillmentText": f" {saat_ini}"})
    else:
        biaya=db_helper.get_total_biaya(number_value)


        if saat_ini == "Pesanan anda dimakan kurir kebenaran":
            pesanan=f"Maaf pesanan anda dimakan kurir kebenaran"
        else:
            pesanan=f"Status pesanan untuk nomor pesanan {int(number_value)} : \n{saat_ini} dengan total Rp {regex_helper.format(int(biaya))} \n\nSelamat Anda Adalah Pelanggan yang beruntung\nAnda mendapatkan diskon special jadi anda hanya perlu membayar sebesar  Rp {regex_helper.format(int(biaya)-1000)}"


       
        return JSONResponse(content={"fulfillmentText": pesanan})