import network
import time
import config
import utils

wlan = None

def connect_wifi(ssid=None, password=None, attempts=3, connection_timeout=15):
    """
    Tries to connect to the specified Wi-Fi network.
    Returns True on success, False on failure.
    """
    global wlan

    _ssid = ssid if ssid else config.WIFI_SSID
    _password = password if password else config.WIFI_PASSWORD

    if not wlan:
        wlan = network.WLAN(network.STA_IF)

    if not wlan.active():
        print(f"[{utils.get_timestamp()}] Activating Wi-Fi interface...")
        wlan.active(True)
        time.sleep(2)

    if wlan.isconnected():
        print(f"[{utils.get_timestamp()}] Wi-Fi is already connected. IP: {wlan.ifconfig()[0]}")
        return True

    print(f"[{utils.get_timestamp()}] Trying to connect to Wi-Fi network: '{_ssid}'...")

    for attempt in range(attempts):
        print(f"[{utils.get_timestamp()}] Attempt {attempt + 1} of {attempts}...")
        try:
            wlan.connect(_ssid, _password)

            start_time = time.time()
            while not wlan.isconnected():
                if time.time() - start_time > connection_timeout:
                    print(f"[{utils.get_timestamp()}] Timeout ({connection_timeout}s) on attempt {attempt + 1}.")
                    break
                print(f"[{utils.get_timestamp()}] Waiting for connection... Status: {wlan.status()}")
                time.sleep(2)

            if wlan.isconnected():
                print(f"[{utils.get_timestamp()}] Wi-Fi connected successfully!")
                print(f"[{utils.get_timestamp()}] IP settings: {wlan.ifconfig()}")
                try:
                    import ntptime
                    ntptime.settime()
                    print(f"[{utils.get_timestamp()}] Time synchronized via NTP: {utils.get_timestamp()}")
                except Exception as e:
                    print(f"[{utils.get_timestamp()}] Failed to synchronize NTP time: {e}")
                return True
            else:
                wlan.disconnect()
                time.sleep(1)

        except OSError as e:
            print(f"[{utils.get_timestamp()}] OSError during connection attempt: {e}")
            wlan.active(False)
            time.sleep(1)
            wlan.active(True)
            time.sleep(1)

    print(f"[{utils.get_timestamp()}] Failed to connect to Wi-Fi '{_ssid}' after {attempts} attempts.")
    return False

def disconnect_wifi():
    """Disconnects from Wi-Fi and deactivates the interface."""
    global wlan
    if wlan and wlan.isconnected():
        print(f"[{utils.get_timestamp()}] Disconnecting from Wi-Fi...")
        wlan.disconnect()

    if wlan and wlan.active():
        print(f"[{utils.get_timestamp()}] Deactivating Wi-Fi interface.")
        wlan.active(False)

    print(f"[{utils.get_timestamp()}] Wi-Fi disconnected and interface deactivated.")
    return True

def is_connected():
    """Checks if Wi-Fi is currently connected."""
    global wlan
    return wlan and wlan.isconnected()

def get_ip():
    """Returns the current IP address if connected, otherwise None."""
    if is_connected():
        return wlan.ifconfig()[0]
    return None
