import re

def get_sesion(text: str):
    pattern = r"(?<=/sessions/)(.*?)(?=/contexts/)"
    match = re.search(pattern, text)
    if match:
        return match.group(0)  # Kembalikan nilai, bukan hanya print
    return None



def tambahkan(y:dict,z:dict):
    result = {}
    for key in set(y) | set(z):  # Menggunakan union untuk semua key yang ada di y dan z
        result[key] = y.get(key, 0) + z.get(key, 0)

    return result


def pesanan(data:dict):
    # Mengubah dictionary menjadi string dengan format yang diinginkan
    hasil = ", ".join(f"{v} {k}" for k, v in data.items())

    # Mengganti koma terakhir dengan "dan" jika ada lebih dari satu item
    if "," in hasil:
        hasil = " dan".join(hasil.rsplit(",", 1))

    return hasil


def format(num):
    
    return f"{num:,}".replace(",", ".")

  