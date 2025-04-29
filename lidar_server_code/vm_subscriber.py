"""Computer Subscriber for LIDAR Distance Logging (Immediate Start)"""

import paho.mqtt.client as mqtt
import csv
import os

CSV_FILENAME = "lidar_log.csv"

# Create CSV with headers if it doesn't exist
if not os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Distance (cm)"])

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("drone/lidar")

def lidar_callback(client, userdata, msg):
    try:
        payload = msg.payload.decode()

        # Expected format: "2025-04-28 21:00:00.123, Distance: 237 cm"
        if ", Distance:" in payload:
            timestamp_part, distance_part = payload.split(", Distance:")
            timestamp = timestamp_part.strip()
            distance = float(distance_part.replace("cm", "").strip())

            print(f"{timestamp}, Distance: {distance} cm")

            with open(CSV_FILENAME, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, distance])
        else:
            print(f"Unexpected payload format: {payload}")

    except Exception as e:
        print(f"Error handling message: {e}")

def on_message(client, userdata, msg):
    pass  # Not used

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.message_callback_add("drone/lidar", lidar_callback)
    client.connect("test.mosquitto.org", 1883, 60)
    client.loop_forever()
