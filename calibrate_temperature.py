import time
import sensor_manager
import utils

# This script is intended to be run directly from the device an provide a reading
# for the temperature sensor. It helps verify that the sensor is working correctly
# and that the data processing logic (multiple readings, mode calculation) is sound.

def run_calibration():
    """
    Performs a calibration run for the temperature sensor.
    Reads the sensor multiple times, calculates the mode/mean, and prints the result.
    """
    print(f"[{utils.get_timestamp()}] Starting temperature sensor calibration...")

    print(f"[{utils.get_timestamp()}] Requesting temperature reading from sensor_manager...")
    # The read_specific_sensor function already handles multiple readings and mode calculation.
    result = sensor_manager.read_specific_sensor("temperature") # Changed to English

    if result and result.get("value") is not None: # Changed to 'value'
        print("-" * 30)
        print(f"Sensor Calibration Result: Temperature")
        print("-" * 30)
        print(f"Timestamp: {utils.get_timestamp()}")
        print(f"Sensor Name: {result.get('sensor')}")
        print(f"Measured Value: {result.get('value'):.2f} {result.get('unit')}") # Changed to 'value' and 'unit'
        print("-" * 30)
        print(f"[{utils.get_timestamp()}] Temperature sensor calibration finished.")
    else:
        print(f"[{utils.get_timestamp()}] Failed to get temperature reading or sensor not initialized.")
        print("Please check sensor connections and sensor_manager.py initialization.")

if __name__ == "__main__":
    # A short delay to allow board initialization or for the user to connect a terminal.
    time.sleep(2)
    run_calibration()
