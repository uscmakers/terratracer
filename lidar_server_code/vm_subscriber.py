"""Computer Subscriber for LIDAR Distance Logging (Starts at 9 PM)"""

import paho.mqtt.client as mqtt
import csv
import os
import datetime
import time

CSV_FILENAME = "lidar_log.csv"

# Create CSV with headers if it doesn't exist
if not os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Distance (cm)"])

# Wait until 9:00 PM local time
def wait_until_9pm():
    now = datetime.datetime.now()
    target = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if now >= target:
        target += datetime.timedelta(days=1)
    wait_time = (target - now).total_seconds()
    print(f"Waiting until 9:00 PM to start logging... ({int(wait_time)} seconds)")
    time.sleep(wait_time)
    print("Started logging at 9:00 PM.")

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("drone/lidar")

def lidar_callback(client, userdata, msg):
    try:
        distance = float(msg.payload.decode())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp}, Distance: {distance} cm")

        with open(CSV_FILENAME, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, distance])
    except Exception as e:
        print(f"Error handling message: {e}")

def on_message(client, userdata, msg):
    pass  # Unused

if __name__ == '__main__':
    wait_until_9pm()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.message_callback_add("drone/lidar", lidar_callback)
    client.connect("test.mosquitto.org", 1883, 60)
    client.loop_forever()
