from pymongo import MongoClient
from datetime import datetime

# ================================
# KONEKSI MONGODB (sesuaikan URI)
# ================================
client = MongoClient("mongodb+srv://kel4iot:kel4jarkomiot@kelompok4.wjbawdf.mongodb.net/?retryWrites=true&w=majority&appName=kelompok4")

# Ganti nama database dan koleksi sesuai proyekmu
db = client["smart_home"]
collection = db["sensor_data"]

# ================================
# Simpan data ke MongoDB
# ================================
def simpan_data(data: dict):
    if "timestamp" not in data:
        data["timestamp"] = datetime.now()
    collection.insert_one(data)
    print(f"[MongoDB] Data disimpan: {data}")

# ================================
# Ambil data terbaru
# ================================
def ambil_data_terbaru():
    return collection.find_one(sort=[("timestamp", -1)])

# ================================
# Ambil data historis (grafik)
# ================================
def ambil_data_harian(jumlah=24):
    return list(collection.find().sort("timestamp", -1).limit(jumlah))[::-1]
