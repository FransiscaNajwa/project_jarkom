import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime, time

# =======================
# SIMULASI DATA SENSOR
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
# TAMPILAN UTAMA
# =======================
st.title("💡 Dashboard Manajemen Energi Rumah Pintar")
st.subheader("Pemantauan Konsumsi Daya Listrik & Kendali Perangkat IoT")
st.markdown("---")

col1, col2 = st.columns(2)
col1.metric("Total Konsumsi Energi", f"{df['Energi (kWh)'].sum():.2f} kWh")
col2.metric("Estimasi Biaya", f"Rp {int(df['Biaya (Rp)'].sum()):,}")

st.markdown("### 📈 Konsumsi Daya (24 jam terakhir)")
st.line_chart(df.set_index("Waktu")[["Daya (W)"]])

# =======================
# STATUS PERANGKAT
# =======================
st.markdown("### 💡 Status Perangkat")
col3, col4 = st.columns(2)
col3.success(f"Lampu: {status['lampu']}")
col4.info(f"Kipas: {status['kipas']}")

st.caption(f"Lux: {status['lux']} lx | Suhu: {status['temp']}°C")

# =======================
# TIMER OTOMATIS
# =======================
st.sidebar.header("⏰ Atur Timer Otomatis")
timer_lampu = st.sidebar.time_input("Waktu matikan lampu", time(21, 0))
timer_kipas = st.sidebar.time_input("Waktu matikan kipas", time(22, 0))
st.sidebar.success(f"Lampu akan mati pukul: {timer_lampu}")
st.sidebar.success(f"Kipas akan mati pukul: {timer_kipas}")

# =======================
# CHATBOT IoT CONTROL
# =======================
st.markdown("### 🤖 Chatbot Kendali IoT")
user_input = st.text_input("Ketik perintah Anda:")

if user_input:
    if re.search(r"mati.*lampu", user_input, re.IGNORECASE):
        st.success("✅ Perintah diterima: Mematikan lampu...")
        # mqtt.publish("rumah/lampu/control", "OFF")
    elif re.search(r"hidup.*kipas", user_input, re.IGNORECASE):
        st.success("✅ Perintah diterima: Menyalakan kipas...")
        # mqtt.publish("rumah/kipas/control", "ON")
    elif "suhu" in user_input:
        st.info(f"🌡️ Suhu saat ini: {status['temp']}°C")
    elif "status" in user_input:
        st.info(f"💡 Lampu: {status['lampu']}, 🌬️ Kipas: {status['kipas']}")
    else:
        st.warning("⚠️ Maaf, perintah tidak dikenali.")

# =======================
# DATA DETAIL (Expandable)
# =======================
with st.expander("📊 Lihat Data Konsumsi Lengkap"):
    st.dataframe(df)

# =======================
# NOTIFIKASI KONSUMSI TINGGI
# =======================
threshold = 180
terlampaui = df[df["Daya (W)"] > threshold]
if not terlampaui.empty:
    st.warning(f"⚠️ Terdapat {len(terlampaui)} jam dengan konsumsi > {threshold}W")
else:
    st.success("✅ Konsumsi daya aman sepanjang hari.")

st.markdown("---")
st.caption("📡 Kelompok 4 – Sistem Rumah Pintar IoT – Teknik Komputer")
