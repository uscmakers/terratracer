"""Computer Subscriber for LIDAR Distance Logging with Elapsed Time"""

import paho.mqtt.client as mqtt
import csv
import os
import time

CSV_FILENAME = "lidar_log.csv"
START_TIME = time.time()  # Record start time

# Create CSV with headers if it doesn't exist
if not os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Elapsed Time (s)", "Distance (cm)"])

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("drone/lidar")

def lidar_callback(client, userdata, msg):
    try:
        distance = float(msg.payload.decode())
        elapsed = round(time.time() - START_TIME, 2)  # Elapsed time in seconds
        print(f"{elapsed}s, Distance: {distance} cm")

        with open(CSV_FILENAME, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([elapsed, distance])
    except Exception as e:
        print(f"Error handling message: {e}")

def on_message(client, userdata, msg):
    pass  # Unused

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.message_callback_add("drone/lidar", lidar_callback)
    client.connect("test.mosquitto.org", 1883, 60)
    client.loop_forever()
