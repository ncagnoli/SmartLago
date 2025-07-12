import time
import config
import utils
import wifi_manager
import http_server # Imported here as it's called directly in the main flow
import led_signals
# sensor_manager is used by http_server, not directly by main.py in the main flow

if __name__ == "__main__":
    led_signals.signal_script_start() # Corrected function name

    # 1. Initial Wi-Fi Connection
    print(f"[{utils.agora()}] Attempting initial Wi-Fi connection to '{config.SSID}'...")

    if wifi_manager.connect_wifi(config.SSID, config.SENHA): # Corrected function name
        led_signals.signal_wifi_status(True) # Corrected function name
        print(f"[{utils.agora()}] Wi-Fi connected successfully. IP: {wifi_manager.get_ip()}")
    else:
        led_signals.signal_wifi_status(False) # Corrected function name
        print(f"[{utils.agora()}] Critical failure to connect to Wi-Fi on startup. Check credentials and network.")
        # The script will proceed to the server startup attempt loop.

    # 2. Main Loop: Try to start the HTTP server or reconnect Wi-Fi
    # This loop runs indefinitely, attempting to keep the server operational.
    while True:
        if wifi_manager.is_connected(): # Corrected function name
            print(f"[{utils.agora()}] Wi-Fi connected. Attempting to start/check HTTP server...")

            # http_server.start_server() is blocking and contains its own listening loop.
            # It only returns False if it cannot start (e.g., socket error).
            # If it stops due to an unhandled internal exception, the script might exit start_server.
            server_started_successfully = http_server.start_server()

            if not server_started_successfully:
                print(f"[{utils.agora()}] HTTP server failed to start (e.g., bind error). Check port configuration.")
                led_signals.signal_general_error() # Corrected function name
            else:
                # If start_server() returns True (or any non-False value),
                # it means it stopped for some reason after starting (which shouldn't happen).
                # This could indicate an unexpected error within the server loop.
                print(f"[{utils.agora()}] HTTP server stopped unexpectedly after starting.")
                led_signals.signal_general_error() # Corrected function name

            # Pause before trying to restart the server or reconnect Wi-Fi.
            print(f"[{utils.agora()}] Waiting {config.INTERVALO_RECONEXAO_WIFI}s before next attempt...")
            time.sleep(config.INTERVALO_RECONEXAO_WIFI)

        else: # Wi-Fi is not connected
            print(f"[{utils.agora()}] Wi-Fi disconnected. Attempting to reconnect...")
            led_signals.signal_wifi_status(False) # Corrected function name
            if wifi_manager.connect_wifi(config.SSID, config.SENHA): # Corrected function name
                led_signals.signal_wifi_status(True) # Corrected function name
                print(f"[{utils.agora()}] Wi-Fi reconnected successfully. IP: {wifi_manager.get_ip()}")
                # Immediately tries to (re)start the server in the next while True cycle
            else:
                print(f"[{utils.agora()}] Failed to reconnect Wi-Fi. Trying again in {config.INTERVALO_RECONEXAO_WIFI}s.")
                time.sleep(config.INTERVALO_RECONEXAO_WIFI)

    # The code below this while True loop should not be reached in normal operation.
    # If it gets here, it's an error state not caught by the loop.
    print(f"[{utils.agora()}] Unexpected end of main script (outside recovery loop).")
    led_signals.signal_general_error() # Corrected function name
    # Keeps the device "alive" in a final loop for inspection, if necessary.
    while True:
        time.sleep(60)
        print(f"[{utils.agora()}] Main script in final error state. Please check the device.")
