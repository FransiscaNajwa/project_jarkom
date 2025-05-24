# mqtt_flask_server.py
from flask import Flask
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime
import json

# -------------------------------
# KONFIGURASI MONGODB
# -------------------------------
mongo_client = MongoClient("mongodb+srv://kel4iot:<kel4jarkomiot>@kelompok4.wjbawdf.mongodb.net/?retryWrites=true&w=majority&appName=kelompok4")
db = mongo_client["smart_home"]
collection = db["sensor_data"]

# -------------------------------
# KONFIGURASI MQTT
# -------------------------------
mqtt_broker = "broker.hivemq.com"
mqtt_port = 1883
topic = "rumah/status"

# -------------------------------
# MQTT Callback
# -------------------------------
def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected with result code", rc)
    client.subscribe(topic)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        payload["timestamp"] = datetime.now()
        print("[MQTT] Received:", payload)
        collection.insert_one(payload)  # Simpan ke MongoDB
        print("[MongoDB] Data inserted.")
    except Exception as e:
        print("[ERROR] Gagal memproses pesan:", e)

# -------------------------------
# Inisialisasi MQTT Client
# -------------------------------
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

# -------------------------------
# FLASK SERVER
# -------------------------------
app = Flask(__name__)

@app.route("/")
def index():
    return "MQTT to MongoDB Flask Server is running."

@app.route("/data")
def get_data():
    # Ambil 10 data terakhir
    latest = list(collection.find().sort("timestamp", -1).limit(10))
    for doc in latest:
        doc["_id"] = str(doc["_id"])
        doc["timestamp"] = doc["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return latest

# -------------------------------
# JALANKAN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)