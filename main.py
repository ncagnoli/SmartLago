import time
import config
import utils
import wifi_manager
import http_server
import led_signals
import machine

if __name__ == "__main__":
    led_signals.signal_script_start()

    # 1. Initial Wi-Fi Connection Attempt (without watchdog)
    print(f"[{utils.get_timestamp()}] Attempting initial Wi-Fi connection to '{config.WIFI_SSID}'...")
    if wifi_manager.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD):
        led_signals.signal_wifi_status(True)
        print(f"[{utils.get_timestamp()}] Wi-Fi connected successfully.")
    else:
        led_signals.signal_wifi_status(False)
        print(f"[{utils.get_timestamp()}] Initial Wi-Fi connection failed. Entering recovery loop...")

    wdt = None

    # 2. Main Loop: Manages server operation and Wi-Fi reconnection
    while True:
        if wifi_manager.is_connected():
            # Initialize and feed the watchdog only when the connection is stable
            # and we are about to start the main server loop.
            if wdt is None:
                print(f"[{utils.get_timestamp()}] System operational. Initializing Watchdog Timer.")
                wdt = machine.WDT(timeout=8000) # 8-second timeout

            wdt.feed()
            print(f"[{utils.get_timestamp()}] Wi-Fi connected. Starting/checking HTTP server...")

            # The server loop will now feed the WDT internally.
            http_server.start_server(wdt)

            # If server loop exits, it's an unexpected error.
            print(f"[{utils.get_timestamp()}] HTTP server stopped unexpectedly. Rebooting via WDT timeout...")
            led_signals.signal_general_error()
            # Stop feeding the WDT to force a hardware reset.
            time.sleep(10) # Wait longer than the WDT timeout

        else: # Wi-Fi is not connected, enter reconnection loop
            # Deactivate the main WDT if it was active to avoid resets during reconnection attempts.
            wdt = None

            print(f"[{utils.get_timestamp()}] Wi-Fi disconnected. Attempting to reconnect...")
            led_signals.signal_wifi_status(False)

            # Try to reconnect for a defined period. A local WDT can be used here if needed,
            # but for simplicity, we'll just loop with delays.
            if wifi_manager.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD, attempts=2, connection_timeout=10):
                print(f"[{utils.get_timestamp()}] Wi-Fi reconnected successfully.")
                # The main loop will continue and re-initialize the WDT in the 'if' block.
            else:
                print(f"[{utils.get_timestamp()}] Failed to reconnect Wi-Fi. Retrying after {config.WIFI_RECONNECT_INTERVAL_S}s...")
                time.sleep(config.WIFI_RECONNECT_INTERVAL_S)

    # This part of the code should ideally not be reached.
    print(f"[{utils.get_timestamp()}] Fim inesperado do script principal (fora do loop de recuperação).")
    led_signals.signal_general_error()
    while True:
        time.sleep(60)
        print(f"[{utils.get_timestamp()}] Main script in final error state. Please check the device.")
