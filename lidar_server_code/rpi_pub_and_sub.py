"""Raspberry Pi LIDAR Publisher (Starts Measuring at 9 PM)"""

import smbus2
import time
import datetime
import paho.mqtt.client as mqtt

# LIDAR constants
LIDAR_I2C_ADDRESS = 0x62
LIDAR_COMMAND_REGISTER = 0x00
LIDAR_DISTANCE_REGISTER = 0x8f

i2c = smbus2.SMBus(1)

def wait_until_9pm():
    now = datetime.datetime.now()
    target = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if now >= target:
        target += datetime.timedelta(days=1)
    wait_time = (target - now).total_seconds()
    print(f"[RPI] Waiting until 9:00 PM to start measuring... ({int(wait_time)} seconds)")
    time.sleep(wait_time)
    print("[RPI] Started measuring at 9:00 PM.")

def read_lidar():
    try:
        i2c.write_byte_data(LIDAR_I2C_ADDRESS, LIDAR_COMMAND_REGISTER, 0x04)
        time.sleep(0.02)  # wait for measurement
        high_byte = i2c.read_byte_data(LIDAR_I2C_ADDRESS, LIDAR_DISTANCE_REGISTER)
        low_byte = i2c.read_byte_data(LIDAR_I2C_ADDRESS, LIDAR_DISTANCE_REGISTER + 1)
        return (high_byte << 8) + low_byte
    except Exception as e:
        print(f"Error reading LIDAR: {e}")
        return None

def on_connect(client, userdata, flags, rc):
    print("[RPI] Connected to MQTT broker with result code " + str(rc))

if __name__ == '__main__':
    # MQTT setup
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("test.mosquitto.org", 1883, 60)
    client.loop_start()

    # Wait until 9:00 PM before starting
    wait_until_9pm()

    while True:
        distance = read_lidar()
        if distance is not None:
            print(f"[RPI] Distance: {distance} cm")
            client.publish("drone/lidar", str(distance))
        time.sleep(0.1)  # adjust as needed
