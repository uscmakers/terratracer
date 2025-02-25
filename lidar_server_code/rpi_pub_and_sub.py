
import smbus2
import time
import paho.mqtt.client as mqtt


LIDAR_I2C_ADDRESS = 0x62
LIDAR_COMMAND_REGISTER = 0x00
LIDAR_DISTANCE_REGISTER = 0x8f
VELOCITY_REGISTER = 0x09  # vel register

i2c = smbus2.SMBus(1)  

def read_lidar():
    """
    Reads distance from LIDAR-Lite v3 using I2C.
    """
    try:

        i2c.write_byte_data(LIDAR_I2C_ADDRESS, LIDAR_COMMAND_REGISTER, 0x04)
        time.sleep(0.02)  #this time for measurement

        # these are the lower and highwe  bytes (2 og them) from distance register
        high_byte = i2c.read_byte_data(LIDAR_I2C_ADDRESS, LIDAR_DISTANCE_REGISTER)
        low_byte = i2c.read_byte_data(LIDAR_I2C_ADDRESS, LIDAR_DISTANCE_REGISTER + 1)

       
        distance = (high_byte << 8) + low_byte
        return distance
          
    #for debugging
    except Exception as e:
        print(f"Error reading lidar: {e}")
        return None
    

def read_velocity():
   
    try:
        return i2c.read_byte_data(LIDAR_I2C_ADDRESS, VELOCITY_REGISTER)
    except Exception as e:
        print(f"Error reading velocity: {e}")
        return None

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code " + str(rc))

if __name__ == '__main__':
    # mqtt 
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(host="test.mosquitto.org", port=1883, keepalive=60)
    client.loop_start()

    prev_distance = read_lidar()
    time.sleep(0.1)  # wait before doing vel calc

    while True:
        current_distance = read_lidar()
        lidar_velocity = read_velocity()  # Direct from LIDAR

        if current_distance is not None and prev_distance is not None:
            # calc velocity  (cm/s)
            velocity = (current_distance - prev_distance) / 0.1  #  0.1s interval

            print(f"LIDAR Distance: {current_distance} cm, Velocity: {velocity:.2f} cm/s (calculated), {lidar_velocity} cm/s (from lidar)")

            # Publish distance and velocity 
            client.publish("drone/lidar", f"{current_distance},{velocity:.2f},{lidar_velocity}")

            prev_distance = current_distance  # update prev dist

        time.sleep(0.1)  # samplaing rate
