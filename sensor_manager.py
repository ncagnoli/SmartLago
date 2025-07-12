import time
import config
import utils
import machine
import urandom

# --- Sensor Initialization ---
ds_sensor = None
roms = []
hcsr04_sensor_pins = None
turbidity_adc = None
tds_adc = None

# DS18B20 Temperature Sensor
try:
    import onewire
    import ds18x20
    ow_pin = machine.Pin(config.DS18B20_PIN)
    ow_bus = onewire.OneWire(ow_pin)
    ds_sensor = ds18x20.DS18X20(ow_bus)
    roms = ds_sensor.scan()
    if not roms:
        print(f"[{utils.get_timestamp()}] No DS18B20 sensor found on pin {config.DS18B20_PIN}.")
        ds_sensor = None
    else:
        print(f"[{utils.get_timestamp()}] DS18B20 sensor initialized on pin {config.DS18B20_PIN}.")
except ImportError:
    print(f"[{utils.get_timestamp()}] onewire/ds18x20 libraries not found. Temperature sensor disabled.")
    ds_sensor = None
except Exception as e:
    print(f"[{utils.get_timestamp()}] Error initializing DS18B20 sensor: {e}")
    ds_sensor = None

# HC-SR04 Distance Sensor
try:
    trigger_pin = machine.Pin(config.HCSR04_TRIGGER_PIN, machine.Pin.OUT)
    echo_pin = machine.Pin(config.HCSR04_ECHO_PIN, machine.Pin.IN)
    hcsr04_sensor_pins = {"trigger": trigger_pin, "echo": echo_pin}
    print(f"[{utils.get_timestamp()}] HC-SR04 sensor initialized (Trigger: {config.HCSR04_TRIGGER_PIN}, Echo: {config.HCSR04_ECHO_PIN}).")
except Exception as e:
    print(f"[{utils.get_timestamp()}] Error initializing HC-SR04 sensor: {e}")
    hcsr04_sensor_pins = None

# Turbidity Sensor (ADC)
try:
    turbidity_adc = machine.ADC(machine.Pin(config.TURBIDITY_ADC_PIN))
    print(f"[{utils.get_timestamp()}] Turbidity ADC sensor initialized on pin {config.TURBIDITY_ADC_PIN}.")
except Exception as e:
    print(f"[{utils.get_timestamp()}] Error initializing ADC for Turbidity: {e}")
    turbidity_adc = None

# TDS Sensor (ADC)
try:
    tds_adc = machine.ADC(machine.Pin(config.TDS_ADC_PIN))
    print(f"[{utils.get_timestamp()}] TDS ADC sensor initialized on pin {config.TDS_ADC_PIN}.")
except Exception as e:
    print(f"[{utils.get_timestamp()}] Error initializing ADC for TDS: {e}")
    tds_adc = None

# --- Statistical Calculation Functions ---
def _calculate_central_value(readings: list):
    """
    Calculates the value with the minimum sum of absolute distances to all other values.
    This value is one of the actual readings and is more robust to outliers than the mean.
    """
    if not readings:
        return None

    min_sum_dist = float('inf')
    central_value = None

    for i in range(len(readings)):
        current_sum_dist = 0
        for j in range(len(readings)):
            if i == j:
                continue
            current_sum_dist += abs(readings[i] - readings[j])

        if current_sum_dist < min_sum_dist:
            min_sum_dist = current_sum_dist
            central_value = readings[i]

    return central_value

# --- Individual Sensor Reading Functions ---
def read_temperature_ds18b20():
    if not ds_sensor or not roms:
        print(f"[{utils.get_timestamp()}] DS18B20 sensor not initialized or not found.")
        return None
    try:
        ds_sensor.convert_temp()
        time.sleep_ms(750)
        return ds_sensor.read_temp(roms[0])
    except Exception as e:
        print(f"[{utils.get_timestamp()}] Error reading DS18B20 temperature: {e}")
        return None

def read_distance_hcsr04():
    if not hcsr04_sensor_pins:
        print(f"[{utils.get_timestamp()}] HC-SR04 sensor not initialized.")
        return None
    trigger = hcsr04_sensor_pins["trigger"]
    echo = hcsr04_sensor_pins["echo"]
    try:
        trigger.value(0)
        time.sleep_us(2)
        trigger.value(1)
        time.sleep_us(10)
        trigger.value(0)
        pulse_duration = machine.time_pulse_us(echo, 1, 30000)
        if pulse_duration < 0:
            return None
        distance_cm = (pulse_duration / 2) / 29.1
        return distance_cm
    except OSError:
        return None
    except Exception as e:
        print(f"[{utils.get_timestamp()}] Unexpected error reading HC-SR04: {e}")
        return None

def read_turbidity_adc():
    if not turbidity_adc:
        print(f"[{utils.get_timestamp()}] Turbidity sensor (ADC) not initialized.")
        return None
    try:
        return turbidity_adc.read_u16()
    except Exception as e:
        print(f"[{utils.get_timestamp()}] Error reading turbidity ADC: {e}")
        return None

def read_tds_adc():
    if not tds_adc:
        print(f"[{utils.get_timestamp()}] TDS sensor (ADC) not initialized.")
        return None
    try:
        return tds_adc.read_u16()
    except Exception as e:
        print(f"[{utils.get_timestamp()}] Error reading TDS ADC: {e}")
        return None

# --- Reading Processing and Filtering Function ---
def _process_sensor_readings(reading_func, sensor_name, num_readings, reading_interval_s):
    if not callable(reading_func):
        print(f"[{utils.get_timestamp()}] {sensor_name}: Reading function is not callable.")
        return None

    collected_readings = []
    print(f"[{utils.get_timestamp()}] {sensor_name}: Starting {num_readings} readings with {reading_interval_s}s interval...")

    for i in range(num_readings):
        value = reading_func()
        if value is not None:
            collected_readings.append(value)
            # Correctly format the value outside the f-string to avoid syntax errors
            formatted_value = f"{value:.2f}" if isinstance(value, float) else str(value)
            print(f"[{utils.get_timestamp()}] {sensor_name} Reading {i+1}/{num_readings}: {formatted_value}")
        else:
            print(f"[{utils.get_timestamp()}] {sensor_name} Reading {i+1}/{num_readings}: Failure")
        time.sleep(reading_interval_s)

    if not collected_readings:
        print(f"[{utils.get_timestamp()}] {sensor_name}: No successful readings.")
        return None

    # New method: Calculate the value with the minimum sum of absolute distances
    final_sensor_value = _calculate_central_value(collected_readings)

    if final_sensor_value is None:
        print(f"[{utils.get_timestamp()}] {sensor_name}: Could not determine a central value from readings: {collected_readings}")
        return None

    formatted_final_value = f"{final_sensor_value:.2f}" if isinstance(final_sensor_value, float) else final_sensor_value
    print(f"[{utils.get_timestamp()}] {sensor_name}: Original readings: {collected_readings}")
    print(f"[{utils.get_timestamp()}] {sensor_name}: Final value (Minimum Sum of Distances): {formatted_final_value}")

    return final_sensor_value

# --- Main Public Functions ---
def read_all_sensors():
    """Reads all configured sensors, applying the central value calculation."""
    try:
        import led_signals
        if hasattr(led_signals, 'signal_sensor_reading_in_progress'):
            led_signals.signal_sensor_reading_in_progress()
    except ImportError:
        pass

    print(f"[{utils.get_timestamp()}] Starting reading of all sensors...")
    data = {}

    if ds_sensor:
        data["temperature"] = _process_sensor_readings(
            reading_func=read_temperature_ds18b20,
            sensor_name="Temperature",
            num_readings=config.TEMP_NUM_READINGS,
            reading_interval_s=config.TEMP_READING_INTERVAL_S)
    else:
        data["temperature"] = None

    if hcsr04_sensor_pins:
        data["distance"] = _process_sensor_readings(
            reading_func=read_distance_hcsr04,
            sensor_name="Distance",
            num_readings=config.DIST_NUM_READINGS,
            reading_interval_s=config.DIST_READING_INTERVAL_S)
    else:
        data["distance"] = None

    if turbidity_adc:
        data["turbidity"] = _process_sensor_readings(
            reading_func=read_turbidity_adc,
            sensor_name="Turbidity",
            num_readings=config.TURB_NUM_READINGS,
            reading_interval_s=config.TURB_READING_INTERVAL_S)
    else:
        data["turbidity"] = None

    if tds_adc:
        data["tds"] = _process_sensor_readings(
            reading_func=read_tds_adc,
            sensor_name="TDS",
            num_readings=config.TDS_NUM_READINGS,
            reading_interval_s=config.TDS_READING_INTERVAL_S)
    else:
        data["tds"] = None

    print(f"[{utils.get_timestamp()}] Final sensor data: {data}")
    return data

def read_specific_sensor(sensor_name_to_read: str):
    """Reads a specific sensor based on the provided name."""
    try:
        import led_signals
        if hasattr(led_signals, 'signal_sensor_reading_in_progress'):
            led_signals.signal_sensor_reading_in_progress()
    except ImportError:
        pass

    print(f"[{utils.get_timestamp()}] Starting reading for sensor: {sensor_name_to_read}")
    sensor_value = None
    unit = None

    if sensor_name_to_read == "temperature":
        if ds_sensor:
            sensor_value = _process_sensor_readings(
                reading_func=read_temperature_ds18b20,
                sensor_name="Temperature",
                num_readings=config.TEMP_NUM_READINGS,
                reading_interval_s=config.TEMP_READING_INTERVAL_S)
            unit = "C"
    elif sensor_name_to_read == "distance":
        if hcsr04_sensor_pins:
            sensor_value = _process_sensor_readings(
                reading_func=read_distance_hcsr04,
                sensor_name="Distance",
                num_readings=config.DIST_NUM_READINGS,
                reading_interval_s=config.DIST_READING_INTERVAL_S)
            unit = "cm"
    elif sensor_name_to_read == "turbidity":
        if turbidity_adc:
            sensor_value = _process_sensor_readings(
                reading_func=read_turbidity_adc,
                sensor_name="Turbidity",
                num_readings=config.TURB_NUM_READINGS,
                reading_interval_s=config.TURB_READING_INTERVAL_S)
            unit = "ADC"
    elif sensor_name_to_read == "tds":
        if tds_adc:
            sensor_value = _process_sensor_readings(
                reading_func=read_tds_adc,
                sensor_name="TDS",
                num_readings=config.TDS_NUM_READINGS,
                reading_interval_s=config.TDS_READING_INTERVAL_S)
            unit = "ADC"
    else:
        print(f"[{utils.get_timestamp()}] Unknown sensor '{sensor_name_to_read}'.")
        return None

    if sensor_value is not None:
        return {"sensor": sensor_name_to_read, "value": sensor_value, "unit": unit}
    else:
        print(f"[{utils.get_timestamp()}] Failed to read sensor {sensor_name_to_read}.")
        return None

if __name__ == '__main__':
    print("Testing sensor_manager module...")
    results = read_all_sensors()
    print("\n--- Final Test Results ---")
    if results:
        for sensor, value in results.items():
            if value is not None:
                try:
                    print(f"Sensor {sensor}: {float(value):.2f}")
                except (ValueError, TypeError):
                    print(f"Sensor {sensor}: {value}")
            else:
                print(f"Sensor {sensor}: Reading failed or not available")
    else:
        print("No sensor data was returned.")
    print("\nEnd of sensor_manager test.")
