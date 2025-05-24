import streamlit as st
import pandas as pd
import numpy as np
from datetime import time
import re

from pymongo import MongoClient
from mqtt_handler import setup_mqtt, publish_command, get_latest_data

# =======================
# SETUP MQTT (hanya sekali)
# =======================
if "mqtt_initialized" not in st.session_state:
    setup_mqtt()
    st.session_state["mqtt_initialized"] = True

# =======================
# SETUP MongoDB
# =======================
client = MongoClient("mongodb+srv://kel4iot:kel4jarkomiot@kelompok4.wjbawdf.mongodb.net/?retryWrites=true&w=majority&appName=kelompok4")
collection = client["smart_home"]["sensor_data"]

def ambil_data_terakhir(jumlah=24):
    data = list(collection.find().sort("timestamp", -1).limit(jumlah))[::-1]
    for d in data:
        d["_id"] = str(d["_id"])
    return pd.DataFrame(data)

# =======================
# AMBIL DATA DARI DB
# =======================
df = ambil_data_terakhir()

biaya_per_kwh = 1500
if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.rename(columns={"timestamp": "Waktu"}, inplace=True)

    if "daya" not in df.columns:
        df["daya"] = np.random.randint(50, 150, len(df))  # fallback jika tidak ada
    df["Energi (kWh)"] = df["daya"] / 1000
    df["Biaya (Rp)"] = df["Energi (kWh)"] * biaya_per_kwh

# =======================
# STATUS SENSOR / PERANGKAT
# =======================
status = get_latest_data()
if not status:
    status = {"lampu": "UNKNOWN", "kipas": "UNKNOWN", "lux": 0, "temp": 0}

# =======================
# DASHBOARD
# =======================
st.set_page_config(layout="wide")
st.title("💡 Sistem Rumah Pintar IoT Berbasis MQTT")
st.markdown("---")

col1, col2 = st.columns(2)
if not df.empty:
    col1.metric("Total Energi", f"{df['Energi (kWh)'].sum():.2f} kWh")
    col2.metric("Estimasi Biaya", f"Rp {int(df['Biaya (Rp)'].sum()):,}")
else:
    col1.warning("Tidak ada data energi.")
    col2.info("Biaya belum tersedia.")

st.markdown("### 📈 Konsumsi Daya (24 jam terakhir)")
if not df.empty:
    st.line_chart(df.set_index("Waktu")[["daya"]])
else:
    st.warning("Data belum tersedia untuk grafik.")

st.markdown("### 💡 Status Sensor & Perangkat")
col3, col4 = st.columns(2)
col3.success(f"Lampu: {status.get('lampu', 'UNKNOWN')}")
col4.info(f"Kipas: {status.get('kipas', 'UNKNOWN')}")
st.caption(f"🔆 Lux: {status.get('lux', 0)} lx | 🌡️ Suhu: {status.get('temp', 0)}°C")

# =======================
# TIMER OTOMATIS
# =======================
st.sidebar.header("⏰ Timer Otomatis")
timer_lampu = st.sidebar.time_input("Matikan Lampu Jam", time(21, 0))
timer_kipas = st.sidebar.time_input("Matikan Kipas Jam", time(22, 0))
st.sidebar.success(f"Jadwal Lampu: {timer_lampu} | Kipas: {timer_kipas}")

# =======================
# KONTROL MANUAL
# =======================
st.markdown("### 🎛️ Kontrol Manual")

col5, col6 = st.columns(2)
with col5:
    if st.button("🔌 Nyalakan Lampu"):
        publish_command("rumah/lampu/control", "ON")
        st.success("Lampu dinyalakan.")
    if st.button("❌ Matikan Lampu"):
        publish_command("rumah/lampu/control", "OFF")
        st.warning("Lampu dimatikan.")

with col6:
    if st.button("🌬️ Nyalakan Kipas"):
        publish_command("rumah/kipas/control", "ON")
        st.success("Kipas dinyalakan.")
    if st.button("❌ Matikan Kipas"):
        publish_command("rumah/kipas/control", "OFF")
        st.warning("Kipas dimatikan.")

# =======================
# CHATBOT
# =======================
st.markdown("### 🤖 Chatbot Perintah Suara")
user_input = st.text_input("Perintah (contoh: matikan lampu, hidupkan kipas)")

if user_input:
    if re.search(r"mati.*lampu", user_input, re.IGNORECASE):
        publish_command("rumah/lampu/control", "OFF")
        st.success("✅ Mematikan lampu...")
    elif re.search(r"hidup.*kipas", user_input, re.IGNORECASE):
        publish_command("rumah/kipas/control", "ON")
        st.success("✅ Menyalakan kipas...")
    elif "suhu" in user_input:
        st.info(f"🌡️ Suhu: {status.get('temp', 0)}°C")
    elif "status" in user_input:
        st.info(f"Lampu: {status.get('lampu', 'UNKNOWN')}, Kipas: {status.get('kipas', 'UNKNOWN')}")
    else:
        st.warning("⚠️ Perintah tidak dikenali.")

# =======================
# TABEL DATA
# =======================
if not df.empty:
    with st.expander("📊 Tabel Konsumsi Energi"):
        st.dataframe(df)
else:
    st.info("Belum ada data sensor untuk ditampilkan.")

# =======================
# NOTIFIKASI BOROS
# =======================
if not df.empty:
    threshold = 180
    terlampaui = df[df["daya"] > threshold]
    if not terlampaui.empty:
        st.warning(f"⚠️ {len(terlampaui)} jam dengan konsumsi > {threshold}W")
    else:
        st.success("✅ Konsumsi daya aman sepanjang hari.")

# =======================
# FOOTER
# =======================
st.markdown("---")
st.caption("📡 Kelompok 4 – Teknik Komputer A – Sistem Rumah Pintar IoT")
