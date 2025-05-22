# File: backend/mqtt_handler.py
import paho.mqtt.client as mqtt
import json

data_store = {
    "temperature": 0,
    "humidity": 0,
    "ldr": 0,
    "gas": 0,
    "lamp_status": "OFF",
    "fan_status": "OFF",
    "gas_alert": False
}

def on_connect(client, userdata, flags, rc):
    client.subscribe("smart_home/data")
    client.subscribe("smart_home/lamp")
    client.subscribe("smart_home/fan")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == "smart_home/data":
        data = json.loads(payload)
        data_store.update(data)
        data_store["gas_alert"] = data["gas"] > 500
    elif topic == "smart_home/lamp":
        data_store["lamp_status"] = payload
    elif topic == "smart_home/fan":
        data_store["fan_status"] = payload

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()
    return client, data_store
