import time
import config
import utils

import machine # Import machine directly, as it's essential for hardware interaction.
# If machine is not available, the device is not MicroPython-based, and this code shouldn't run.

# Remove fallback logic for 'random' if 'urandom' is not available,
# as 'urandom' is standard in MicroPython. If it's missing, it's an environment issue.
import urandom

# --- Sensor Initialization ---
# Initialization now occurs regardless of PC_MODE,
# as PC_MODE has been removed. Hardware errors will be reported.
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
        print(f"[{utils.get_timestamp()}] DS18B20 sensor found: {roms}")
except ImportError:
    print(f"[{utils.get_timestamp()}] onewire/ds18x20 libraries not found. Temperature sensor disabled.")
    ds_sensor = None
except Exception as e:
    print(f"[{utils.get_timestamp()}] Error initializing DS18B20 sensor: {e}")
    ds_sensor = None

# HC-SR04 Distance Sensor
try:
    trigger_pin = machine.Pin(config.PIN_HCSR04_TRIGGER, machine.Pin.OUT)
    echo_pin = machine.Pin(config.PIN_HCSR04_ECHO, machine.Pin.IN)
    hcsr04_sensor_pins = {"trigger": trigger_pin, "echo": echo_pin}
    print(f"[{utils.get_timestamp()}] HC-SR04 sensor initialized (Trigger: {config.PIN_HCSR04_TRIGGER}, Echo: {config.PIN_HCSR04_ECHO}).")
except Exception as e:
    print(f"[{utils.get_timestamp()}] Error initializing HC-SR04 sensor: {e}")
    hcsr04_sensor_pins = None

# Turbidity Sensor (ADC)
try:
    adc_turbidez = machine.ADC(machine.Pin(config.PIN_TURBIDEZ_ADC))
    print(f"[{utils.get_timestamp()}] Turbidity ADC sensor initialized on pin {config.PIN_TURBIDEZ_ADC}.")
except Exception as e:
    print(f"[{utils.get_timestamp()}] Error initializing ADC for Turbidity: {e}")
    adc_turbidez = None

# TDS Sensor (ADC)
try:
    adc_tds = machine.ADC(machine.Pin(config.PIN_TDS_ADC))
    print(f"[{utils.get_timestamp()}] TDS ADC sensor initialized on pin {config.PIN_TDS_ADC}.")
except Exception as e:
    print(f"[{utils.get_timestamp()}] Error initializing ADC for TDS: {e}")
    adc_tds = None

# _simulate_reading function was removed as PC_MODE is abolished.
# --- Statistical Calculation Functions ---

def _calculate_mode(readings: list, round_to_decimal_places=None):
    """
    Calculates the mode of a list of readings.
    If there are multiple modes, returns the smallest one.
    If all readings are unique (and there's more than one), or the list is empty, returns None.
    'round_to_decimal_places': optionally rounds readings before calculating the mode
                                   to group close values.
    """
    if not readings:
        return None

    if round_to_decimal_places is not None:
        processed_readings = [round(l, round_to_decimal_places) for l in readings]
    else:
        processed_readings = list(readings) # Copy to avoid modifying the original if not rounding

    if not processed_readings: # Rare case, if all original readings were None and not filtered before
        return None

    counts = {}
    for value in processed_readings:
        counts[value] = counts.get(value, 0) + 1

    if not counts: # Should be impossible if processed_readings is not empty
        return None

    max_count = 0
    for value in counts:
        if counts[value] > max_count:
            max_count = counts[value]

    # If all counts are 1 (all values unique) and there's more than one value, no clear mode.
    # Or if max_count is 1 and there's more than one item, also no clear mode.
    if max_count == 1 and len(processed_readings) > 1:
         # If all values are unique, there's no clear mode.
         # We could return the mean as a fallback, or None.
         # print(f"[{utils.get_timestamp()}] [Mode] All values are unique, no clear mode. Returning mean as fallback.")
         # return sum(processed_readings) / len(processed_readings)
        return None


    modes = []
    for value, count in counts.items():
        if count == max_count:
            modes.append(value)

    if not modes: # Impossible if max_count > 0
        return None

    # Return the smallest of the modes if there's a tie, for consistency.
    # Or could be the first one found: return modes[0]
    return min(modes)


def read_temperature_ds18b20():
    """Reads the temperature from the DS18B20 sensor."""
    # PC_MODE simulation has been removed. This function now always tries to read from hardware.
    if not ds_sensor or not roms:
        print(f"[{utils.get_timestamp()}] DS18B20 sensor not initialized or not found.")
        return None
    try:
        ds_sensor.convert_temp()
        time.sleep_ms(750)
        temp = ds_sensor.read_temp(roms[0])
        return temp
    except Exception as e:
        print(f"[{utils.get_timestamp()}] Error reading DS18B20 temperature: {e}")
        return None

def read_distance_hcsr04():
    """Reads the distance from the HC-SR04 sensor."""
    # PC_MODE simulation has been removed.
    if not hcsr04_sensor_pins:
        print(f"[{utils.get_timestamp()}] HC-SR04 sensor not initialized.")
        return None
    trigger = hcsr04_sensor_pins["trigger"]
    echo = hcsr04_sensor_pins["echo"]
    try:
        trigger.value(0); time.sleep_us(2)
        trigger.value(1); time.sleep_us(10)
        trigger.value(0)
        duracao_pulso = machine.time_pulse_us(echo, 1, 30000)
        if duracao_pulso < 0: return None
        distancia_cm = (duracao_pulso / 2) / 29.1
        return distance_cm
    except OSError: # Usually a timeout
        return None
    except Exception as e:
        print(f"[{utils.get_timestamp()}] Unexpected error reading HC-SR04: {e}")
        return None

def read_turbidity_adc():
    """Reads the raw ADC value for turbidity."""
    # PC_MODE simulation has been removed.
    if not adc_turbidez:
        print(f"[{utils.get_timestamp()}] Turbidity sensor (ADC) not initialized.")
        return None
    try:
        return adc_turbidez.read_u16()
    except Exception as e:
        print(f"[{utils.get_timestamp()}] Error reading turbidity ADC: {e}")
        return None

def read_tds_adc():
    """Reads the raw ADC value for TDS."""
    # PC_MODE simulation has been removed.
    if not adc_tds:
        print(f"[{utils.get_timestamp()}] TDS sensor (ADC) not initialized.")
        return None
    try:
        return adc_tds.read_u16()
    except Exception as e:
        print(f"[{utils.get_timestamp()}] Error reading TDS ADC: {e}")
        return None

# --- Reading Processing and Filtering Function ---

def _process_sensor_readings(reading_func, sensor_name, num_readings, reading_interval_s, outlier_limit_percent, mode_decimal_places=None):
    """
    Collects multiple readings from a sensor, filters outliers, and calculates the MODE.
    Returns the mode, or None if no valid readings or clear mode.
    'mode_decimal_places': number of decimal places to round to before calculating mode.
                           Sensors like temperature might benefit from this; ADC raw values usually don't.
    """
    if not callable(reading_func):
        print(f"[{utils.get_timestamp()}] {sensor_name}: Reading function is not callable.")
        return None

    collected_readings = []
    print(f"[{utils.get_timestamp()}] {sensor_name}: Starting {num_readings} readings with {reading_interval_s}s interval...")

    for i in range(num_readings):
        value = reading_func()
        if value is not None:
            collected_readings.append(value)
            print(f"[{utils.get_timestamp()}] {sensor_name} Reading {i+1}/{num_readings}: {value:.2f}" if isinstance(value, float) else f"{value}")
        else:
            print(f"[{utils.get_timestamp()}] {sensor_name} Reading {i+1}/{num_readings}: Failure")

        time.sleep(reading_interval_s)

    if not collected_readings:
        print(f"[{utils.get_timestamp()}] {sensor_name}: No successful readings.")
        return None

    # Outlier filtering (based on raw average, as before)
    raw_average = sum(collected_readings) / len(collected_readings)
    filtered_readings = []

    if outlier_limit_percent > 0:
        for v in collected_readings:
            # Outlier logic might need refinement, especially for zero values.
            # If raw_average is very small (close to zero), division can be unstable.
            is_outlier = False
            if abs(raw_average) > 1e-6: # Avoid division by zero or instability
                if abs(v - raw_average) / raw_average > outlier_limit_percent:
                    is_outlier = True
            elif v != 0 and abs(v) > outlier_limit_percent * 1: # Fallback if raw_average is zero, compare with a unit
                 # If raw_average is zero, a non-zero value might be an outlier if large enough.
                 # This part is more heuristic.
                 pass # Depends on what's expected when the average is zero.

            if is_outlier:
                print(f"[{utils.get_timestamp()}] {sensor_name}: value {v} discarded as outlier (raw average {raw_average:.2f}).")
            else:
                filtered_readings.append(v)
    else: # No outlier filtering
        filtered_readings = list(collected_readings)

    if not filtered_readings:
        print(f"[{utils.get_timestamp()}] {sensor_name}: All readings were discarded as outliers.")
        # Fallback: maybe return the raw average of original readings? Or None?
        # For now, None, indicating filtering removed everything.
        return None

    # Calculate MODE on filtered readings
    final_sensor_value = _calculate_mode(filtered_readings, round_to_decimal_places=mode_decimal_places)

    if final_sensor_value is None:
        print(f"[{utils.get_timestamp()}] {sensor_name}: No clear mode found in filtered readings. Using mean as fallback.")
        # Fallback to mean if mode is not clear
        if filtered_readings: # Ensure there's something to average
             final_sensor_value = sum(filtered_readings) / len(filtered_readings)
        else: # This shouldn't happen if the previous check for not filtered_readings worked
             return None

    print(f"[{utils.get_timestamp()}] {sensor_name}: Original readings ({len(collected_readings)}): {collected_readings}")
    print(f"[{utils.get_timestamp()}] {sensor_name}: Raw average: {raw_average:.2f}")
    print(f"[{utils.get_timestamp()}] {sensor_name}: Filtered readings ({len(filtered_readings)}): {filtered_readings}")
    if isinstance(final_sensor_value, float):
        print(f"[{utils.get_timestamp()}] {sensor_name}: Final value (Mode/Mean fallback): {final_sensor_value:.2f}")
    else:
        print(f"[{utils.get_timestamp()}] {sensor_name}: Final value (Mode/Mean fallback): {final_sensor_value}")

    return final_sensor_value

# --- Main Sensor Reading Function ---

def read_all_sensors():
    """
    Reads all configured sensors, applying filtering and mode calculation.
    Returns a dictionary with sensor data.
    """
    # Try to import led_signals dynamically to avoid circular dependency or initialization error
    try:
        import led_signals
        if hasattr(led_signals, 'signal_sensor_reading_in_progress'): # Corrected function name
            led_signals.signal_sensor_reading_in_progress()
    except ImportError:
        pass # led_signals not available, continue without it

    print(f"[{utils.get_timestamp()}] Starting reading of all sensors...")
    data = {}

    # Temperature
    # 'or config.PC_MODE' condition removed.
    if ds_sensor:
        data["temperatura"] = _process_sensor_readings(
            reading_func=read_temperature_ds18b20,
            sensor_name="Temperatura",  # Keep "Temperatura" for key consistency if desired, or change to "temperature"
            num_readings=config.NUM_LEITURAS_TEMP,
            reading_interval_s=config.INTERVALO_LEITURA_TEMP_S,
            outlier_limit_percent=config.LIMITE_OUTLIER_TEMP,
            mode_decimal_places=1
        )
    else:
        data["temperatura"] = None
        print(f"[{utils.get_timestamp()}] Temperature reading skipped (sensor not initialized).")


    # Distance
    if hcsr04_sensor_pins:
        data["distancia"] = _process_sensor_readings( # Keep "distancia" for key consistency
            reading_func=read_distance_hcsr04,
            sensor_name="Distancia",
            num_readings=config.NUM_LEITURAS_DIST,
            reading_interval_s=config.INTERVALO_LEITURA_DIST_S,
            outlier_limit_percent=config.LIMITE_OUTLIER_DIST,
            mode_decimal_places=0
        )
    else:
        data["distancia"] = None
        print(f"[{utils.get_timestamp()}] Distance reading skipped (sensor not initialized).")

    # Turbidity
    if adc_turbidez:
        data["turbidez"] = _process_sensor_readings( # Keep "turbidez" for key consistency
            reading_func=read_turbidity_adc,
            sensor_name="Turbidez",
            num_readings=config.NUM_LEITURAS_TURB,
            reading_interval_s=config.INTERVALO_LEITURA_TURB_S,
            outlier_limit_percent=config.LIMITE_OUTLIER_TURB,
            mode_decimal_places=None
        )
    else:
        data["turbidez"] = None
        print(f"[{utils.get_timestamp()}] Turbidity reading skipped (sensor not initialized).")

    # TDS
    if adc_tds:
        data["tds"] = _process_sensor_readings(
            reading_func=read_tds_adc,
            sensor_name="TDS",
            num_readings=config.NUM_LEITURAS_TDS,
            reading_interval_s=config.INTERVALO_LEITURA_TDS_S,
            outlier_limit_percent=config.LIMITE_OUTLIER_TDS,
            mode_decimal_places=None
        )
    else:
        data["tds"] = None
        print(f"[{utils.get_timestamp()}] TDS reading skipped (sensor not initialized).")

    print(f"[{utils.get_timestamp()}] Final sensor data (Mode/Mean): {data}")
    return data

# --- New Function for Specific Sensor Reading ---
def read_specific_sensor(sensor_name_to_read: str):
    """
    Reads a specific sensor based on the provided name, using its dedicated settings.
    Returns a dictionary with the sensor data or None if the sensor is not found or fails.
    Ex: {"sensor": "temperatura", "valor": 25.5, "unidade": "C"}
    """
    # Try to import led_signals dynamically
    try:
        import led_signals
        if hasattr(led_signals, 'signal_sensor_reading_in_progress'): # Corrected function name
            led_signals.signal_sensor_reading_in_progress()
    except ImportError:
        pass

    print(f"[{utils.get_timestamp()}] Starting reading for sensor: {sensor_name_to_read}")
    sensor_value = None
    unit = None

    # Using original Portuguese names for keys for consistency with previous data structure,
    # but function names and variable names are in English.
    if sensor_name_to_read == "temperatura":
        if ds_sensor:
            sensor_value = _process_sensor_readings(
                reading_func=read_temperature_ds18b20,
                sensor_name="Temperatura",
                num_readings=config.NUM_LEITURAS_TEMP,
                reading_interval_s=config.INTERVALO_LEITURA_TEMP_S,
                outlier_limit_percent=config.LIMITE_OUTLIER_TEMP,
                mode_decimal_places=1
            )
            unit = "C"
        else: # Sensor not initialized
            print(f"[{utils.get_timestamp()}] Temperature reading skipped (sensor not initialized).")
    elif sensor_name_to_read == "distancia":
        if hcsr04_sensor_pins:
            sensor_value = _process_sensor_readings(
                reading_func=read_distance_hcsr04,
                sensor_name="Distancia",
                num_readings=config.NUM_LEITURAS_DIST,
                reading_interval_s=config.INTERVALO_LEITURA_DIST_S,
                outlier_limit_percent=config.LIMITE_OUTLIER_DIST,
                mode_decimal_places=0
            )
            unit = "cm"
        else: # Sensor not initialized
            print(f"[{utils.get_timestamp()}] Distance reading skipped (sensor not initialized).")
    elif sensor_name_to_read == "turbidez":
        if adc_turbidez:
            sensor_value = _process_sensor_readings(
                reading_func=read_turbidity_adc,
                sensor_name="Turbidez",
                num_readings=config.NUM_LEITURAS_TURB,
                reading_interval_s=config.INTERVALO_LEITURA_TURB_S,
                outlier_limit_percent=config.LIMITE_OUTLIER_TURB,
                mode_decimal_places=None # ADC raw
            )
            unit = "ADC"
        else: # Sensor not initialized
            print(f"[{utils.get_timestamp()}] Turbidity reading skipped (sensor not initialized).")
    elif sensor_name_to_read == "tds":
        if adc_tds:
            sensor_value = _process_sensor_readings(
                reading_func=read_tds_adc,
                sensor_name="TDS",
                num_readings=config.NUM_LEITURAS_TDS,
                reading_interval_s=config.INTERVALO_LEITURA_TDS_S,
                outlier_limit_percent=config.LIMITE_OUTLIER_TDS,
                mode_decimal_places=None # ADC raw
            )
            unit = "ADC"
        else: # Sensor not initialized
            print(f"[{utils.get_timestamp()}] TDS reading skipped (sensor not initialized).")
    else:
        print(f"[{utils.get_timestamp()}] Unknown sensor '{sensor_name_to_read}'.")
        return None

    if sensor_value is not None:
        print(f"[{utils.get_timestamp()}] Final reading for {sensor_name_to_read}: {sensor_value} {unit if unit else ''}")
        return {"sensor": sensor_name_to_read, "valor": sensor_value, "unidade": unit}
    else:
        print(f"[{utils.get_timestamp()}] Failed to read sensor {sensor_name_to_read}.")
        return None


if __name__ == '__main__':
    # To test this module, ensure config.py and utils.py are accessible
    # and that the pins in config.py match your hardware.
    print("Testing sensor_manager module...")

    # Optional: Import led_signals for visual testing if used
    try:
        import led_signals
        print("led_signals imported for visual test.")
    except ImportError:
        print("led_signals not found, test will be by print only.")
        led_signals = None # Ensure no error if it doesn't exist

    # Test reading all sensors
    results = read_all_sensors()

    print("\n--- Final Test Results ---")
    if results:
        for sensor, value in results.items():
            if value is not None:
                # Attempt to format as float, but handle non-float (e.g. ADC int) gracefully
                try:
                    print(f"Sensor {sensor}: {float(value):.2f}")
                except ValueError:
                    print(f"Sensor {sensor}: {value}")
                except TypeError: # Handles if value is None (already checked, but good practice)
                     print(f"Sensor {sensor}: {value}")
            else:
                print(f"Sensor {sensor}: Reading failed or not available")
    else:
        print("No sensor data was returned.")

    # Individual tests (uncomment to test specific functions)
    # print("\nTesting individual temperature reading...")
    # temp = read_temperature_ds18b20()
    # if temp is not None:
    #     print(f"Individual temperature: {temp:.2f} C")
    # else:
    #     print("Failed to read individual temperature or sensor not available.")

    # print("\nTesting individual distance reading...")
    # dist = read_distance_hcsr04()
    # if dist is not None:
    #     print(f"Individual distance: {dist:.2f} cm")
    # else:
    #     print("Failed to read individual distance or sensor not available.")

    # print("\nTesting individual turbidity reading (ADC raw)...")
    # turb = read_turbidity_adc()
    # if turb is not None:
    #     print(f"Individual turbidity (ADC): {turb}")
    # else:
    #     print("Failed to read individual turbidity or sensor not available.")

    # print("\nTesting individual TDS reading (ADC raw)...")
    # tds_val = read_tds_adc()
    # if tds_val is not None:
    #     print(f"Individual TDS (ADC): {tds_val}")
    # else:
    #     print("Failed to read individual TDS or sensor not available.")

    print("\nEnd of sensor_manager test.")
