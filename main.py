import time
import config
import utils
import wifi_manager
import http_server # Imported here as it's called directly in the main flow
import led_signals
import machine # Import machine for WDT
# sensor_manager is used by http_server, not directly by main.py in the main flow

if __name__ == "__main__":
    # Initialize the Watchdog Timer with an 8-second timeout.
    # If the WDT is not fed within 8 seconds, the device will reset.
    wdt = machine.WDT(timeout=8000)
    wdt.feed()

    led_signals.signal_script_start()

    # 1. Initial Wi-Fi Connection
    print(f"[{utils.get_timestamp()}] Attempting initial Wi-Fi connection to '{config.WIFI_SSID}'...")

    if wifi_manager.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD):
        led_signals.signal_wifi_status(True)
        print(f"[{utils.get_timestamp()}] Wi-Fi connected successfully.")
    else:
        led_signals.signal_wifi_status(False)
        print(f"[{utils.get_timestamp()}] Critical failure to connect to Wi-Fi on startup. Check credentials and network.")
        # The script will proceed to the server startup attempt loop.

    # 2. Main Loop: Try to start the HTTP server or reconnect Wi-Fi
    # This loop runs indefinitely, attempting to keep the server operational.
    while True:
        if wifi_manager.is_connected():
            wdt.feed() # Feed the watchdog before starting the server loop
            print(f"[{utils.get_timestamp()}] Wi-Fi connected. Attempting to start/check HTTP server...")

            # http_server.start_server() is blocking and contains its own listening loop.
            # It only returns False if it cannot start (e.g., socket error).
            # If it stops due to an unhandled internal exception, the script might exit start_server.
            server_started_successfully = http_server.start_server(wdt)

            if not server_started_successfully:
                print(f"[{utils.get_timestamp()}] HTTP server failed to start (e.g., bind error). Check port configuration.")
                led_signals.signal_general_error()
            else:
                # If start_server() returns True (or any non-False value),
                # it means it stopped for some reason after starting (which shouldn't happen).
                # This could indicate an unexpected error within the server loop.
                print(f"[{utils.get_timestamp()}] HTTP server stopped unexpectedly after starting.")
                led_signals.signal_general_error()

            # Pause before trying to restart the server or reconnect Wi-Fi.
            print(f"[{utils.get_timestamp()}] Waiting {config.WIFI_RECONNECT_INTERVAL_S}s before next attempt...")
            time.sleep(config.WIFI_RECONNECT_INTERVAL_S)

        else: # Wi-Fi is not connected
            print(f"[{utils.get_timestamp()}] Wi-Fi disconnected. Attempting to reconnect...")
            led_signals.signal_wifi_status(False)
            if wifi_manager.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD):
                led_signals.signal_wifi_status(True)
                print(f"[{utils.get_timestamp()}] Wi-Fi reconnected successfully.")
                # Immediately tries to (re)start the server in the next while True cycle
            else:
                print(f"[{utils.get_timestamp()}] Failed to reconnect Wi-Fi. Trying again in {config.WIFI_RECONNECT_INTERVAL_S}s.")
                time.sleep(config.WIFI_RECONNECT_INTERVAL_S)

    # The code below this while True loop should not be reached in normal operation.
    # If it gets here, it's an error state not caught by the loop.
    print(f"[{utils.get_timestamp()}] Unexpected end of main script (outside recovery loop).")
    led_signals.signal_general_error()
    # Keeps the device "alive" in a final loop for inspection, if necessary.
    while True:
        time.sleep(60)
        print(f"[{utils.get_timestamp()}] Main script in final error state. Please check the device.")
