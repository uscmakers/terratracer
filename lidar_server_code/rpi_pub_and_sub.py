"""Raspberry Pi LIDAR Distance Publisher"""

import smbus2
import time
import paho.mqtt.client as mqtt

# I2C constants for LIDAR
LIDAR_I2C_ADDRESS = 0x62
LIDAR_COMMAND_REGISTER = 0x00
LIDAR_DISTANCE_REGISTER = 0x8f

# Initialize I2C
i2c = smbus2.SMBus(1)

def read_lidar():
    try:
        i2c.write_byte_data(LIDAR_I2C_ADDRESS, LIDAR_COMMAND_REGISTER, 0x04)
        time.sleep(0.02)
        high = i2c.read_byte_data(LIDAR_I2C_ADDRESS, LIDAR_DISTANCE_REGISTER)
        low = i2c.read_byte_data(LIDAR_I2C_ADDRESS, LIDAR_DISTANCE_REGISTER + 1)
        return (high << 8) + low
    except Exception as e:
        print(f"Error reading LIDAR: {e}")
        return None

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("test.mosquitto.org", 1883, 60)
    client.loop_start()

    while True:
        distance = read_lidar()
        if distance is not None:
            print(f"Distance: {distance} cm")
            client.publish("drone/lidar", str(distance))
        time.sleep(0.1)
