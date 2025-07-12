# === General Settings ===
WIFI_SSID = "WIFI-SSID"  # Wi-Fi network name
WIFI_PASSWORD = "WIFI-PW"  # Wi-Fi network password

# === HTTP Server Settings ===
HTTP_PORT = 80 # Default HTTP port
HTTP_MAX_PENDING_CONN = 5 # Maximum number of pending connections on the server socket
HTTP_CLIENT_TIMEOUT_S = 10 # Timeout in seconds for client socket operations (recv, send)
HTTP_MAX_REQUEST_SIZE = 1024 # Maximum size in bytes of the HTTP request to be read

# === Intervals ===
# MAIN_LOOP_INTERVAL has been replaced by HTTP server logic and MAIN_HEARTBEAT_INTERVAL
MAIN_HEARTBEAT_INTERVAL_S = 5 # Interval for the maintenance loop in main.py (seconds) - Note: main.py loop structure changed
WIFI_RECONNECT_INTERVAL_S = 60 # Interval to try reconnecting to Wi-Fi if it drops (seconds)

# Sensor reading configurations (will be used by endpoints)
# Each sensor will have: NUM_READINGS_X, READING_INTERVAL_X_S
# Example for temperature:
TEMP_NUM_READINGS = 10
TEMP_READING_INTERVAL_S = 1 # Interval between individual readings to compose a final measurement

DIST_NUM_READINGS = 10
DIST_READING_INTERVAL_S = 1

TURB_NUM_READINGS = 10
TURB_READING_INTERVAL_S = 1

TDS_NUM_READINGS = 10
TDS_READING_INTERVAL_S = 1 # Interval between individual TDS readings

# ZABBIX_MAX_RESEND is no longer needed

# === Sensor Outlier Limits ===
# Values in percentage (e.g., 0.10 for 10%)
# These can be global or per sensor, if necessary.
TEMP_OUTLIER_LIMIT = 0.10
DIST_OUTLIER_LIMIT = 0.50
TURB_OUTLIER_LIMIT = 0.20
TDS_OUTLIER_LIMIT = 0.20 # Example, adjust as needed

# === Sensor Pins ===
# These will be used by the specific sensor modules
ONBOARD_LED_PIN = "LED" # Pico W onboard LED pin

# Pins for DS18B20 temperature sensor
DS18B20_PIN = 18

# Pins for HC-SR04 distance sensor
HCSR04_TRIGGER_PIN = 20
HCSR04_ECHO_PIN = 19

# Pin for turbidity sensor (ADC)
TURBIDITY_ADC_PIN = 26 # ADC0

# Pin for TDS sensor (ADC) - Example, verify correct pin
TDS_ADC_PIN = 27 # ADC1 - Example, adjust if necessary

# === Log/Cache Files ===
FAILURE_LOG_FILE = "failures.log" # Failure log file
# DATA_CACHE_FILE is no longer needed with the removal of Zabbix and its caching logic

# PC_MODE has been removed. The code now assumes it's running on MicroPython hardware.
# DEBUG_MODE has been removed. Debug logs are now always active.

print("Configurations loaded from config.py")
# Conditional logic for PC_MODE has been removed.
