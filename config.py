# === General Settings ===
SSID = "Suryland"  # Wi-Fi network name
SENHA = "AvengersAssemble2020@@"  # Wi-Fi network password

# === HTTP Server Settings ===
HTTP_PORT = 80 # Default HTTP port
HTTP_MAX_PENDING_CONN = 5 # Maximum number of pending connections on the server socket
HTTP_CLIENT_TIMEOUT_S = 10 # Timeout in seconds for client socket operations (recv, send)
HTTP_MAX_REQUEST_SIZE = 1024 # Maximum size in bytes of the HTTP request to be read

# === Intervals ===
# MAIN_LOOP_INTERVAL has been replaced by HTTP server logic and MAIN_HEARTBEAT_INTERVAL
INTERVALO_HEARTBEAT_MAIN = 5 # Interval for the maintenance loop in main.py (seconds) - Note: main.py loop structure changed
INTERVALO_RECONEXAO_WIFI = 60 # Interval to try reconnecting to Wi-Fi if it drops (seconds)

# Sensor reading configurations (will be used by endpoints)
# Each sensor will have: NUM_READINGS_X, READING_INTERVAL_X_S
# Example for temperature:
NUM_LEITURAS_TEMP = 10
INTERVALO_LEITURA_TEMP_S = 1 # Interval between individual readings to compose a final measurement

NUM_LEITURAS_DIST = 10
INTERVALO_LEITURA_DIST_S = 1

NUM_LEITURAS_TURB = 10
INTERVALO_LEITURA_TURB_S = 1

NUM_LEITURAS_TDS = 10
INTERVALO_LEITURA_TDS_S = 1 # Interval between individual TDS readings

# ZABBIX_MAX_RESEND is no longer needed

# === Sensor Outlier Limits ===
# Values in percentage (e.g., 0.10 for 10%)
# These can be global or per sensor, if necessary.
LIMITE_OUTLIER_TEMP = 0.10
LIMITE_OUTLIER_DIST = 0.50
LIMITE_OUTLIER_TURB = 0.20
LIMITE_OUTLIER_TDS = 0.20 # Example, adjust as needed

# === Sensor Pins ===
# These will be used by the specific sensor modules
PIN_LED_ONBOARD = "LED" # Pico W onboard LED pin

# Pins for DS18B20 temperature sensor
PIN_DS18B20 = 18

# Pins for HC-SR04 distance sensor
PIN_HCSR04_TRIGGER = 20
PIN_HCSR04_ECHO = 19

# Pin for turbidity sensor (ADC)
PIN_TURBIDEZ_ADC = 26 # ADC0

# Pin for TDS sensor (ADC) - Example, verify correct pin
PIN_TDS_ADC = 27 # ADC1 - Example, adjust if necessary

# === Log/Cache Files ===
ARQUIVO_FALHAS_LOG = "falhas.log" # Failure log file
# DATA_CACHE_FILE is no longer needed with the removal of Zabbix and its caching logic

# PC_MODE has been removed. The code now assumes it's running on MicroPython hardware.
# DEBUG_MODE has been removed. Debug logs are now always active.

print("Configurations loaded from config.py")
# Conditional logic for PC_MODE has been removed.
