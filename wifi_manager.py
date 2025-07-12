import network
import time
import config # To access SSID and PASSWORD if not passed as arguments
import utils # For logging with timestamp

# Global reference for the WLAN interface
wlan = None

def connect_wifi(ssid=None, password=None, attempts=3, connection_timeout=15):
    """
    Tries to connect to the specified Wi-Fi network.
    Returns True on success, False on failure.
    """
    global wlan

    # Use SSID and PASSWORD from config.py if not provided
    _ssid = ssid if ssid else config.WIFI_SSID
    _password = password if password else config.WIFI_PASSWORD

    if not wlan:
        wlan = network.WLAN(network.STA_IF)

    if not wlan.active():
        print(f"[{utils.get_timestamp()}] Activating Wi-Fi interface...")
        wlan.active(True)
        time.sleep(1) # Short pause for the interface to activate

    if wlan.isconnected():
        print(f"[{utils.get_timestamp()}] Wi-Fi is already connected. IP: {wlan.ifconfig()[0]}")
        return True

    print(f"[{utils.get_timestamp()}] Trying to connect to Wi-Fi network: '{_ssid}'...")

    for attempt in range(attempts):
        print(f"[{utils.get_timestamp()}] Attempt {attempt + 1} of {attempts}...")
        try:
            wlan.connect(_ssid, _password)

            # Wait for connection
            start_time = time.time()
            while not wlan.isconnected():
                if time.time() - start_time > connection_timeout:
                    print(f"[{utils.get_timestamp()}] Timeout ({connection_timeout}s) on attempt {attempt + 1}.")
                    break # Exit wait loop, go to next attempt
                print(f"[{utils.get_timestamp()}] Waiting for connection... Status: {wlan.status()}")
                time.sleep(1)

            if wlan.isconnected():
                print(f"[{utils.get_timestamp()}] Wi-Fi connected successfully!")
                print(f"[{utils.get_timestamp()}] IP settings: {wlan.ifconfig()}")
                # Synchronize NTP after Wi-Fi connection
                try:
                    import ntptime
                    ntptime.settime()
                    print(f"[{utils.get_timestamp()}] Time synchronized via NTP: {utils.get_timestamp()}")
                except Exception as e:
                    print(f"[{utils.get_timestamp()}] Failed to synchronize NTP time: {e}")
                return True
            else:
                # If timeout occurred and not connected, end the current attempt.
                wlan.disconnect() # Ensure it's not left in a pending connection state
                time.sleep(1) # Pause before trying again

        except OSError as e:
            print(f"[{utils.get_timestamp()}] OSError during connection attempt: {e}")
            # Deactivating and reactivating the interface might help in some persistent error cases
            wlan.active(False)
            time.sleep(1)
            wlan.active(True)
            time.sleep(1)

    print(f"[{utils.get_timestamp()}] Failed to connect to Wi-Fi '{_ssid}' after {attempts} attempts.")
    return False

def disconnect_wifi():
    """Disconnects from Wi-Fi and deactivates the interface to save power."""
    global wlan
    if wlan and wlan.isconnected():
        print(f"[{utils.get_timestamp()}] Disconnecting from Wi-Fi...")
        wlan.disconnect()

    if wlan and wlan.active():
        print(f"[{utils.get_timestamp()}] Deactivating Wi-Fi interface.")
        wlan.active(False)
        # wlan = None # Optional: reset the global variable if not used again until next connection

    print(f"[{utils.get_timestamp()}] Wi-Fi disconnected and interface deactivated.")
    return True

def is_connected():
    """Checks if Wi-Fi is currently connected."""
    global wlan
    if wlan and wlan.isconnected():
        return True
    return False

def get_ip():
    """Returns the current IP address if connected, otherwise None."""
    if is_connected():
        return wlan.ifconfig()[0]
    return None

if __name__ == '__main__':
    # To test, you would need a config.py in the same directory
    # or pass SSID and PASSWORD directly.
    print("Testing wifi_manager module...")

    if connect_wifi(): # Tries to use SSID/PASSWORD from config.py
        print("Connection status:", "Connected" if is_connected() else "Disconnected")
        print("IP:", wlan.ifconfig()[0] if is_connected() else "N/A")

        print("\nWaiting 5 seconds before disconnecting...")
        time.sleep(5)
        disconnect_wifi()
        print("Connection status after disconnecting:", "Connected" if is_connected() else "Disconnected")
    else:
        print("Could not connect to Wi-Fi.")

    print("\nReconnection test (manually activating and deactivating):")
    # Simulate a state where wlan might not be active
    if wlan and wlan.active():
        wlan.active(False)
        time.sleep(1)

    # Test with invalid SSID and Password (or valid ones, to test success)
    # print("\nTesting connection with invalid credentials (failure expected):")
    # if connect_wifi("invalid_ssid", "invalid_password", attempts=2, connection_timeout=5):
    #     print("Unexpected connection with invalid credentials!")
    #     disconnect_wifi()
    # else:
    #     print("Failed to connect with invalid credentials (expected).")

    print("End of wifi_manager test.")
