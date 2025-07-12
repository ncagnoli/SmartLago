import time
import config
import utils
import wifi_manager
import http_server
import led_signals

if __name__ == "__main__":
    led_signals.signal_script_start()

    print(f"[{utils.get_timestamp()}] Attempting initial Wi-Fi connection to '{config.WIFI_SSID}'...")
    if wifi_manager.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD):
        led_signals.signal_wifi_status(True)
        print(f"[{utils.get_timestamp()}] Wi-Fi connected successfully.")
    else:
        led_signals.signal_wifi_status(False)
        print(f"[{utils.get_timestamp()}] Initial Wi-Fi connection failed. Entering recovery loop...")

    while True:
        if wifi_manager.is_connected():
            print(f"[{utils.get_timestamp()}] Wi-Fi connected. Starting HTTP server...")

            # The server loop is blocking. If it exits, it's an unexpected error.
            http_server.start_server()

            # This part is reached only if the server loop breaks unexpectedly.
            print(f"[{utils.get_timestamp()}] HTTP server stopped unexpectedly. Restarting process...")
            led_signals.signal_general_error()
            time.sleep(10)

        else: # Wi-Fi is not connected, enter reconnection loop
            print(f"[{utils.get_timestamp()}] Wi-Fi disconnected. Attempting to reconnect...")
            led_signals.signal_wifi_status(False)

            if wifi_manager.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD, attempts=2, connection_timeout=10):
                print(f"[{utils.get_timestamp()}] Wi-Fi reconnected successfully.")
            else:
                print(f"[{utils.get_timestamp()}] Failed to reconnect Wi-Fi. Retrying after {config.WIFI_RECONNECT_INTERVAL_S}s...")
                time.sleep(config.WIFI_RECONNECT_INTERVAL_S)
