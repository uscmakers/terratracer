"""Computer Subscriber for Drone's LIDAR Data"""

import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    client.subscribe("drone/lidar")

def lidar_callback(client, userdata, msg):
    # Process and display the LIDAR data
    lidar_distance = float(msg.payload.decode())
    print(f"LIDAR Distance: {lidar_distance} cm")

# Default message callback. Unused since we're using a custom callback.
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
