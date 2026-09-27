import json
import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_TELEMETRY = "city/streetlights/+/telemetry"

def init_db():
    conn = sqlite3.connect("smart_streetlights.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pole_id TEXT,
            timestamp TEXT,
            voltage REAL,
            current REAL,
            lux REAL,
            motion_status INTEGER,
            system_status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_telemetry_to_db(pole_id, voltage, current, lux, motion, status):
    conn = sqlite3.connect("smart_streetlights.db")
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO telemetry (pole_id, timestamp, voltage, current, lux, motion_status, system_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (pole_id, timestamp, voltage, current, lux, motion, status))
    conn.commit()
    conn.close()

def run_diagnostics(pole_id, voltage, current, lux, lat, lon):
    if voltage >= 180 and current > 0.05:
        return "HEALTHY"
    elif voltage < 50 and current == 0:
        return "DAYTIME_OFF"
    elif voltage >= 180 and current <= 0.05:
        dispatch_alert(pole_id, "CRITICAL: LED Driver / Lamp Burnout", lat, lon)
        return "FAULT_LED_BURNOUT"
    elif voltage < 50 and lux < 10:
        dispatch_alert(pole_id, "WARNING: Main Power Line Failure or Cable Cut", lat, lon)
        return "FAULT_POWER_LOSS"
    else:
        return "UNKNOWN_ANOMALY"

def dispatch_alert(pole_id, fault_type, lat, lon):
    google_maps_link = f"https://maps.google.com/?q={lat},{lon}"
    print("\n" + "="*60)
    print("🚨 [AUTOMATED MAINTENANCE ALERT DISPATCHED] 🚨")
    print(f"Pole ID      : {pole_id}")
    print(f"Fault Type   : {fault_type}")
    print(f"Location GPS : {lat}, {lon}")
    print(f"Action Map   : {google_maps_link}")
    print("="*60 + "\n")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to Cloud MQTT Broker ({MQTT_BROKER})")
        client.subscribe(MQTT_TOPIC_TELEMETRY)
        print(f"📡 Subscribed to: {MQTT_TOPIC_TELEMETRY}\n")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        pole_id = data.get("pole_id", "UNKNOWN")
        voltage = float(data.get("voltage", 0.0))
        current = float(data.get("current", 0.0))
        lux = float(data.get("lux", 0.0))
        motion = int(data.get("motion", 0))
        lat = data.get("lat", 18.5204)
        lon = data.get("lon", 73.8567)

        print(f"📩 [Data Received] {pole_id} | V: {voltage}V | I: {current}A | Lux: {lux}")
        status = run_diagnostics(pole_id, voltage, current, lux, lat, lon)
        log_telemetry_to_db(pole_id, voltage, current, lux, motion, status)
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    init_db()
    client = mqtt.Client(client_id="Central_Diagnostic_Server")
    client.on_connect = on_connect
    client.on_message = on_message
    print("🚀 Starting Central Command Diagnostic Engine...\n")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()