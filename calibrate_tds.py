import time
import sensor_manager
import utils

# This script is intended to be run directly from the device to provide a reading
# for the TDS (Total Dissolved Solids) sensor. It helps verify that the sensor is working
# correctly and that the data processing logic (multiple readings, mode calculation) is sound.

def run_calibration():
    """
    Performs a calibration run for the TDS sensor.
    Reads the sensor multiple times, calculates the mode/mean, and prints the result.
    """
    print(f"[{utils.get_timestamp()}] Starting TDS sensor calibration...")

    print(f"[{utils.get_timestamp()}] Requesting TDS reading from sensor_manager...")
    result = sensor_manager.read_specific_sensor("tds")

    if result and result.get("valor") is not None:
        print("-" * 30)
        print(f"Sensor Calibration Result: TDS")
        print("-" * 30)
        print(f"Timestamp: {utils.get_timestamp()}")
        print(f"Sensor Name: {result.get('sensor')}")
        # TDS sensor returns raw ADC value (integer)
        print(f"Measured Value: {result.get('valor')} {result.get('unidade')}")
        print("-" * 30)
        print(f"[{utils.get_timestamp()}] TDS sensor calibration finished.")
    else:
        print(f"[{utils.get_timestamp()}] Failed to get TDS reading or sensor not initialized.")
        print("Please check sensor connections and sensor_manager.py initialization.")

if __name__ == "__main__":
    time.sleep(2) # Delay for board initialization/terminal connection
    run_calibration()
