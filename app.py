import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime, time
import mqtt_handler  # pastikan file mqtt_handler.py ada di folder yang sama

# =======================
# INISIALISASI MQTT (sekali di awal)
# =======================
mqtt_handler.setup_mqtt()

# =======================
# SIMULASI DATA SENSOR (dummy)
# =======================
waktu = pd.date_range(end=datetime.now(), periods=24, freq='H')
daya = np.random.randint(50, 200, size=24)
biaya_per_kwh = 1500

df = pd.DataFrame({
    "Waktu": waktu,
    "Daya (W)": daya,
    "Energi (kWh)": daya / 1000
})
df["Biaya (Rp)"] = df["Energi (kWh)"] * biaya_per_kwh

# =======================
# STATUS PERANGKAT
# =======================
status = {
    "lampu": "ON" if df["Daya (W)"].iloc[-1] > 100 else "OFF",
    "kipas": "ON" if df["Daya (W)"].iloc[-1] > 150 else "OFF",
    "lux": 180,
    "temp": 31.2
}

# =======================
# DASHBOARD UTAMA
# =======================
st.set_page_config(layout="wide")
st.title("💡 Sistem Rumah Pintar IoT Berbasis MQTT untuk Manajemen Energi")
st.markdown("---")

col1, col2 = st.columns(2)
col1.metric("Total Konsumsi Energi", f"{df['Energi (kWh)'].sum():.2f} kWh")
col2.metric("Estimasi Biaya", f"Rp {int(df['Biaya (Rp)'].sum()):,}")

st.markdown("### 📈 Konsumsi Daya (24 jam terakhir)")
st.line_chart(df.set_index("Waktu")[["Daya (W)"]])

# =======================
# STATUS SENSOR & PERANGKAT
# =======================
st.markdown("### 💡 Status Perangkat & Sensor")
col3, col4 = st.columns(2)
col3.success(f"Lampu: {status['lampu']}")
col4.info(f"Kipas: {status['kipas']}")
st.caption(f"🔆 Lux: {status['lux']} lx | 🌡️ Suhu: {status['temp']}°C")

# =======================
# TIMER OTOMATIS
# =======================
st.sidebar.header("⏰ Timer")
timer_lampu = st.sidebar.time_input("Waktu matikan lampu", time(21, 0))
timer_kipas = st.sidebar.time_input("Waktu matikan kipas", time(22, 0))
st.sidebar.success(f"Lampu dijadwalkan mati pukul: {timer_lampu}")
st.sidebar.success(f"Kipas dijadwalkan mati pukul: {timer_kipas}")

# =======================
# KONTROL MANUAL
# =======================
st.markdown("### 🎛️ Kontrol Manual Perangkat")

col5, col6 = st.columns(2)
with col5:
    if st.button("🔌 Nyalakan Lampu"):
        mqtt_handler.publish_command("rumah/lampu/control", "ON")
        st.success("Lampu dinyalakan.")
    if st.button("❌ Matikan Lampu"):
        mqtt_handler.publish_command("rumah/lampu/control", "OFF")
        st.warning("Lampu dimatikan.")

with col6:
    if st.button("🌬️ Nyalakan Kipas"):
        mqtt_handler.publish_command("rumah/kipas/control", "ON")
        st.success("Kipas dinyalakan.")
    if st.button("❌ Matikan Kipas"):
        mqtt_handler.publish_command("rumah/kipas/control", "OFF")
        st.warning("Kipas dimatikan.")

# =======================
# CHATBOT IoT CONTROL
# =======================
st.markdown("### 🤖 Chatbot")
user_input = st.text_input("Ketik perintah Anda:")

if user_input:
    if re.search(r"mati.*lampu", user_input, re.IGNORECASE):
        mqtt_handler.publish_command("rumah/lampu/control", "OFF")
        st.success("✅ Mematikan lampu...")
    elif re.search(r"hidup.*kipas", user_input, re.IGNORECASE):
        mqtt_handler.publish_command("rumah/kipas/control", "ON")
        st.success("✅ Menyalakan kipas...")
    elif "suhu" in user_input:
        st.info(f"🌡️ Suhu saat ini: {status['temp']}°C")
    elif "status" in user_input:
        st.info(f"Lampu: {status['lampu']}, Kipas: {status['kipas']}")
    else:
        st.warning("⚠️ Perintah tidak dikenali.")

# =======================
# TAMPILKAN DATA DETAIL
# =======================
with st.expander("📊 Lihat Data Konsumsi"):
    st.dataframe(df)

# =======================
# NOTIFIKASI KONSUMSI BERLEBIHAN
# =======================
threshold = 180
terlampaui = df[df["Daya (W)"] > threshold]
if not terlampaui.empty:
    st.warning(f"⚠️ {len(terlampaui)} jam dengan konsumsi > {threshold}W")
else:
    st.success("✅ Konsumsi daya aman sepanjang hari.")

# =======================
# FOOTER
# =======================
st.markdown("---")
st.caption("📡 Kelompok 4 – Teknik Komputer A – Sistem Rumah Pintar IoT")
