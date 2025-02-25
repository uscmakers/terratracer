"""Computer Subscriber for LIDAR Data with CSV Logging"""

import paho.mqtt.client as mqtt
import csv
import datetime
import os

START_TIME = datetime.datetime.now() 
CSV_FILENAME = "lidar_log.csv"

# Create the CSV file if it doesn't exist
if not os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Distance (cm)"])  # Write header

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code " + str(rc))
    client.subscribe("drone/lidar")

def lidar_callback(client, userdata, msg):
    # Process the LIDAR data received
    lidar_distance = float(msg.payload.decode())
    
    # Generate timestamp based on elapsed time from START_TIME
    timestamp = START_TIME + datetime.timedelta(seconds=int((datetime.datetime.now() - START_TIME).total_seconds()))
    
    print(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}, LIDAR Distance: {lidar_distance} cm")

    # Log data to CSV file
    with open(CSV_FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp.strftime("%Y-%m-%d %H:%M:%S"), lidar_distance])

# Default message callback (unused here)
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    # Initialize the MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.message_callback_add("drone/lidar", lidar_callback)
    client.connect(host="test.mosquitto.org", port=1883, keepalive=60)

    client.loop_forever()
