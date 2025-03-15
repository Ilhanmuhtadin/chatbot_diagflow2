# ====================================================================
# number[
#           1,
#           1
#         ]
# food_item: [
#           "gulai sapi",
#           "Tongseng Ayam"
#         ]

# -------------------------------------------------------------
# order_dict = dict(zip(food_item, number))

# print(order_dict)
# --------------------------------------------------------------
# ================================
list_nama_makanan_db = ['Sates']
list_nama_makanan = ['sate']

list_nama_makanan_db_lower = [item.lower() for item in list_nama_makanan_db]
list_nama_makanan_lower = [item.lower() for item in list_nama_makanan]

print(list_nama_makanan_db_lower, list_nama_makanan_lower)

# Cek apakah ada makanan yang tidak ada dalam database (case-insensitive)
makanan_tidak_valid =len( [item for item in list_nama_makanan_lower if item not in list_nama_makanan_db_lower])>0


print("Makanan tidak valid:", makanan_tidak_valid)
