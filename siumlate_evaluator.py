import json
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 8000  # WebSockets Port matching index.html

test_cases = [
    {
        "case_name": "Case 1: Normal Night Operation",
        "topic": "city/streetlights/PMC_POLE_101/telemetry",
        "data": {"pole_id": "PMC_POLE_101", "voltage": 230.5, "current": 0.45, "lux": 2.1, "motion": 1, "lat": 18.5204, "lon": 73.8567}
    },
    {
        "case_name": "Case 2: Normal Off-Peak Idle (Dimmed Standby)",
        "topic": "city/streetlights/PMC_POLE_102/telemetry",
        "data": {"pole_id": "PMC_POLE_102", "voltage": 228.0, "current": 0.09, "lux": 1.5, "motion": 0, "lat": 18.5314, "lon": 73.8446}
    },
    {
        "case_name": "Case 3: Daytime Standby (Auto Off)",
        "topic": "city/streetlights/PMC_POLE_103/telemetry",
        "data": {"pole_id": "PMC_POLE_103", "voltage": 0.0, "current": 0.0, "lux": 450.0, "motion": 1, "lat": 18.5074, "lon": 73.8077}
    },
    {
        "case_name": "Case 4: CRITICAL FAULT - LED Driver Burnout",
        "topic": "city/streetlights/PMC_POLE_104/telemetry",
        "data": {"pole_id": "PMC_POLE_104", "voltage": 231.2, "current": 0.00, "lux": 3.0, "motion": 1, "lat": 18.4967, "lon": 73.8584}
    },
    {
        "case_name": "Case 5: WARNING FAULT - Power Line Cut",
        "topic": "city/streetlights/PMC_POLE_105/telemetry",
        "data": {"pole_id": "PMC_POLE_105", "voltage": 0.0, "current": 0.00, "lux": 1.2, "motion": 0, "lat": 18.5602, "lon": 73.9125}
    }
]

print("🚀 STARTING LIVE EVALUATION SIMULATOR (WebSocket Mode)\n")

# Use WebSockets to align with the browser dashboard
client = mqtt.Client(transport="websockets")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

time.sleep(1) # Ensure connection is established

for idx, case in enumerate(test_cases, 1):
    print(f"[{idx}/5] Sending {case['case_name']}...")
    client.publish(case["topic"], json.dumps(case["data"]))
    print(" ✅ Sent successfully!\n")
    time.sleep(2)

client.loop_stop()
client.disconnect()
print("🎉 All 5 cases sent live!")