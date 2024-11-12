import time
import struct
import logging
import paho.mqtt.client as mqtt
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

# Configure logging to log both to the console and a file
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler("sensor_data.log")])

# MQTT Configuration
mqtt_broker = "mqtt_broker_ip"
mqtt_port = 1883
mqtt_topic = "sensor_data"

# Create an MQTT client instance
client = mqtt.Client()

# Connect to MQTT Broker
def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT broker with result code " + str(rc))
client.on_connect = on_connect
client.connect(mqtt_broker, mqtt_port, 60)

# Modbus TCP client setup
modbus_client = ModbusClient('modbus_server_ip', port=502)

# Function to read Modbus registers
def read_modbus():
    # Connecting to the Modbus server
    if not modbus_client.connect():
        logging.error("Unable to connect to Modbus server")
        return None

    # Reading 10 registers (adjust as needed)
    response = modbus_client.read_holding_registers(0, 10)
    if response.isError():
        logging.error("Modbus read error: %s", response)
        return None

    modbus_data = response.registers
    modbus_client.close()
    return modbus_data

# Function to decode Modbus data
def decode_modbus_data(data):
    # Assuming each value in data is a 16-bit register, combine them if necessary (e.g., 2 registers per value)
    if len(data) >= 10:
        decoder101 = struct.unpack('>f', struct.pack('>HH', data[0], data[1]))[0]  # Example for float value decoding
        decoder102 = struct.unpack('>f', struct.pack('>HH', data[2], data[3]))[0]
        decoder103 = struct.unpack('>f', struct.pack('>HH', data[4], data[5]))[0]
        decoder104 = struct.unpack('>f', struct.pack('>HH', data[6], data[7]))[0]
        decoder105 = struct.unpack('>f', struct.pack('>HH', data[8], data[9]))[0]
        return decoder101, decoder102, decoder103, decoder104, decoder105
    else:
        logging.error("Insufficient Modbus data received.")
        return None

# Main function
def main():
    while True:
        # Read Modbus data
        modbus_data = read_modbus()
        if modbus_data is None:
            logging.error("Failed to read Modbus data.")
            time.sleep(5)
            continue

        # Decode Modbus data
        decoded_data = decode_modbus_data(modbus_data)
        if decoded_data is None:
            logging.error("Failed to decode Modbus data.")
            time.sleep(5)
            continue

        # Extract sensor values from decoded data
        decoder101, decoder102, decoder103, decoder104, decoder105 = decoded_data
        
        # Log the data for debugging
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logging.info(f"Time                    :------> {now}")
        logging.info(f"vibit x rms accl        :------> {decoder101:.2f}")
        logging.info(f"vibit y rms accl        :------> {decoder102:.2f}")
        logging.info(f"vibit z rms accl        :------> {decoder103:.2f}")
        logging.info(f"vibit x rms vel         :------> {decoder104:.2f}")
        logging.info(f"vibit y rms vel         :------> {decoder105:.2f}")

        # Publish the data to MQTT broker
        try:
            mqtt_data = {
                "time": now,
                "vibit_x_rms_accl": decoder101,
                "vibit_y_rms_accl": decoder102,
                "vibit_z_rms_accl": decoder103,
                "vibit_x_rms_vel": decoder104,
                "vibit_y_rms_vel": decoder105
            }
            client.publish(mqtt_topic, str(mqtt_data), qos=1)
            logging.info(f"Data sent to MQTT broker: {mqtt_data}")
        except Exception as e:
            logging.error(f"Failed to send data to MQTT broker: {e}")
        
        # Wait before reading again
        time.sleep(10)

if __name__ == "__main__":
    client.loop_start()  # Start MQTT client loop in background
    main()
