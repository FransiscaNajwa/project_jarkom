import paho.mqtt.client as mqtt
import json
from datetime import datetime

# =========================
# Variabel global
# =========================
client = None
latest_data = {}

# =========================
# Callback ketika terhubung
# =========================
def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    client.subscribe("rumah/status")  # Sesuaikan topik dengan yang digunakan ESP32

# =========================
# Callback ketika menerima pesan
# =========================
def on_message(client, userdata, msg):
    global latest_data
    try:
        payload = json.loads(msg.payload.decode())
        payload["timestamp"] = datetime.now()
        latest_data = payload
        print(f"[MQTT] Message received: {latest_data}")
    except Exception as e:
        print(f"[MQTT] Error parsing message: {e}")

# =========================
# Inisialisasi MQTT
# =========================
def setup_mqtt(broker="broker.hivemq.com", port=1883):
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port, 60)
    client.loop_start()  # jalankan non-blocking loop
    return client

# =========================
# Fungsi publish MQTT
# =========================
def publish_command(topic, payload):
    if client:
        client.publish(topic, payload)
        print(f"[MQTT] Published: {topic} → {payload}")
    else:
        print("[MQTT] Client belum diinisialisasi. Jalankan setup_mqtt() terlebih dahulu.")

# =========================
# Ambil data terbaru (jika dibutuhkan)
# =========================
def get_latest_data():
    return latest_data
