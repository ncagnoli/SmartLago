import time
import sensor_manager
import utils

# This script is intended to be run directly from the device to provide a reading
# for the distance sensor (HC-SR04). It helps verify that the sensor is working correctly
# and that the data processing logic (multiple readings, mode calculation) is sound.

def run_calibration():
    """
    Performs a calibration run for the distance sensor.
    Reads the sensor multiple times, calculates the mode/mean, and prints the result.
    """
    print(f"[{utils.get_timestamp()}] Starting distance sensor calibration...")

    print(f"[{utils.get_timestamp()}] Requesting distance reading from sensor_manager...")
    result = sensor_manager.read_specific_sensor("distancia")

    if result and result.get("valor") is not None:
        print("-" * 30)
        print(f"Sensor Calibration Result: Distance")
        print("-" * 30)
        print(f"Timestamp: {utils.get_timestamp()}")
        print(f"Sensor Name: {result.get('sensor')}")
        # HC-SR04 might return float, ensure formatting handles it.
        try:
            print(f"Measured Value: {float(result.get('valor')):.2f} {result.get('unidade')}")
        except (ValueError, TypeError):
            print(f"Measured Value: {result.get('valor')} {result.get('unidade')}")
        print("-" * 30)
        print(f"[{utils.get_timestamp()}] Distance sensor calibration finished.")
    else:
        print(f"[{utils.get_timestamp()}] Failed to get distance reading or sensor not initialized.")
        print("Please check sensor connections and sensor_manager.py initialization.")

if __name__ == "__main__":
    time.sleep(2) # Delay for board initialization/terminal connection
    run_calibration()
