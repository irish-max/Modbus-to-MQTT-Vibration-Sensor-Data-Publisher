# Modbus-to-MQTT-(Vibration-Sensor-Data-Publisher)

This project reads sensor data from a Modbus TCP server and publishes the data to an MQTT broker. The data is fetched from Modbus registers, decoded, and sent as JSON formatted messages to the MQTT broker. The system also logs sensor data and errors to both the console and a log file for debugging and analysis.

## Features

- Reads data from a Modbus TCP server using `pymodbus`.
- Decodes Modbus register values into floating-point sensor data.
- Publishes the decoded data to an MQTT broker using `paho-mqtt`.
- Logs sensor data and critical events (such as connection status and errors) to the console and a log file (`sensor_data.log`).

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/modbus-to-mqtt.git
   cd modbus-to-mqtt

