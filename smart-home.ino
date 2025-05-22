// File: esp32/esp32_firmware.ino
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define LED_PIN 2
#define FAN_PIN 4
#define GAS_SENSOR_PIN 34
#define LDR_PIN 35
#define DHTPIN 5
#define DHTTYPE DHT11

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
const char* mqtt_server = "broker.hivemq.com";

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (int i = 0; i < length; i++) msg += (char)payload[i];
  if (String(topic) == "smart_home/lamp") digitalWrite(LED_PIN, msg == "ON" ? HIGH : LOW);
  if (String(topic) == "smart_home/fan") digitalWrite(FAN_PIN, msg == "ON" ? HIGH : LOW);
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP32Client")) {
      client.subscribe("smart_home/lamp");
      client.subscribe("smart_home/fan");
    } else {
      delay(5000);
    }
  }
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  dht.begin();
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  int ldr = analogRead(LDR_PIN);
  int gas = analogRead(GAS_SENSOR_PIN);

  String data = "{";
  data += "\"temperature\":" + String(temp) + ",";
  data += "\"humidity\":" + String(hum) + ",";
  data += "\"ldr\":" + String(ldr) + ",";
  data += "\"gas\":" + String(gas);
  data += "}";

  client.publish("smart_home/data", data.c_str());
  delay(2000);
}
