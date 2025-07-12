# Monitoring Project with Raspberry Pi Pico W and Micropython

This project uses a Raspberry Pi Pico W programmed in MicroPython to collect sensor data from an ornamental pond and send it to a monitoring system.

## Features

*   Reads data from the following sensors:
    *   Temperature (DS18B20)
    *   Distance (HC-SR04)
    *   Turbidity (Analog turbidity sensor)
    *   Total Dissolved Solids (TDS)
*   Connects to a Wi-Fi network for data transmission.
*   Signals status and operations via the onboard LED.
*   Embedded HTTP server to expose sensor data through JSON endpoints.

## HTTP Endpoints

The HTTP server exposes the following endpoints for querying sensor data. All endpoints use the `GET` method and do not require parameters in the request.

### `/temperature`

*   **Method:** `GET`
*   **Description:** Returns the current reading from the temperature sensor.
*   **Response (Success - 200 OK):**
    ```json
    {
      "temperature": 25.5
    }
    ```
*   **Response (Error - 500 Internal Server Error):** If reading the sensor fails.
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### `/distance`

*   **Method:** `GET`
*   **Description:** Returns the current reading from the distance sensor.
*   **Response (Success - 200 OK):**
    ```json
    {
      "distance": 10.2
    }
    ```
*   **Response (Error - 500 Internal Server Error):** If reading the sensor fails.
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### `/turbidity`

*   **Method:** `GET`
*   **Description:** Returns the current reading from the turbidity sensor (raw ADC value).
*   **Response (Success - 200 OK):**
    ```json
    {
      "turbidity": 3000
    }
    ```
*   **Response (Error - 500 Internal Server Error):** If reading the sensor fails.
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### `/tds`

*   **Method:** `GET`
*   **Description:** Returns the current reading from the TDS (Total Dissolved Solids) sensor (raw ADC value).
*   **Response (Success - 200 OK):**
    ```json
    {
      "tds": 1500
    }
    ```
*   **Response (Error - 500 Internal Server Error):** If reading the sensor fails.
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### `/all_sensors`

*   **Method:** `GET`
*   **Description:** Returns the current readings from all configured sensors.
*   **Response (Success - 200 OK):**
    ```json
    {
      "temperature": 25.5,
      "distance": 10.2,
      "turbidity": 3000,
      "tds": 1500
    }
    ```
    *Note: If reading a specific sensor fails, its value in the JSON will be `null`.*
*   **Response (Error - 500 Internal Server Error):** In case of a critical failure when trying to read sensors (rare, as individual failures are handled with `null`).
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### Other Common HTTP Responses

*   **`400 Bad Request`**: If the HTTP request is malformed.
    ```json
    {"error": "Bad Request", "detail": "Error description"}
    ```
*   **`404 Not Found`**: If the requested path does not exist.
    ```json
    {"error": "Not Found"}
    ```
*   **`405 Method Not Allowed`**: If an HTTP method other than `GET` is used.
    ```json
    {"error": "Method Not Allowed"}
    ```

## Code Structure

The code is modularized for better organization and maintenance, with the following main files:

*   `main.py`: Main script that initializes Wi-Fi and the HTTP server.
*   `config.py`: Stores all project configurations (Wi-Fi credentials, sensor pins, reading parameters, HTTP server settings, etc.).
*   `wifi_manager.py`: Manages the Wi-Fi connection.
*   `sensor_manager.py`: Responsible for interfacing with sensors, reading data, and processing (filtering, mode/mean).
*   `http_server.py`: Implements the HTTP server and routing to sensor handlers.
*   `led_signals.py`: Controls LED visual signals to indicate different system states.
*   `utils.py`: Contains utility functions (e.g., timestamp formatting).
*   `calibrate_temperature.py`, `calibrate_distance.py`, `calibrate_turbidity.py`, `calibrate_tds.py`: Individual scripts for testing and calibrating each sensor.

## Calibration Scripts

A set of calibration scripts are provided to help test individual sensors and their data processing logic. These scripts can be run directly on the device.

To run a calibration script, connect to the device's REPL (e.g., using Thonny or `mpremote`) and execute the desired script. For example:

Each script will:
1.  Perform multiple readings for the specific sensor.
2.  Calculate the mode/mean of these readings.
3.  Print the processed sensor value to the terminal.

This allows for verification of sensor functionality and the accuracy of the reading logic independently of the HTTP server.

## Hardware

*   Raspberry Pi Pico W
*   DS18B20 Temperature Sensor
*   HC-SR04 Ultrasonic Distance Sensor
*   Analog Turbidity Sensor
*   Total Dissolved Solids (TDS) Sensor
*   Resistors and jumpers as needed for connections.

