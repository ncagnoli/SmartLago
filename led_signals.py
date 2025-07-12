import machine
import time
import config

# Onboard LED Initialization
# The "LED" pin is a common alias on Pico W for the onboard LED.
try:
    led_onboard = machine.Pin(config.PIN_LED_ONBOARD, machine.Pin.OUT)
except TypeError:
    # Fallback in case config.PIN_LED_ONBOARD is an integer pin number
    # This might happen if the user changes the config for, e.g., an external LED
    led_onboard = machine.Pin(int(config.PIN_LED_ONBOARD), machine.Pin.OUT)


def _blink_led(count=1, on_duration=0.1, off_duration=0.1):
    """Helper function to blink the LED."""
    for _ in range(count):
        led_onboard.on()
        time.sleep(on_duration)
        led_onboard.off()
        time.sleep(off_duration)

def signal_script_start():
    """Signals that the main script has started running."""
    print("[LED] Signal: Script start")
    _blink_led(count=3, on_duration=0.05, off_duration=0.05)
    time.sleep(0.5) # Short pause after the signal

def signal_wifi_status(connected: bool):
    """Signals the Wi-Fi connection status."""
    if connected:
        print("[LED] Signal: Wi-Fi Connected")
        # Blink 2 times quickly for success
        _blink_led(count=2, on_duration=0.1, off_duration=0.1)
    else:
        print("[LED] Signal: Wi-Fi connection failed")
        # Blink 1 long time for failure
        _blink_led(count=1, on_duration=0.5, off_duration=0.1)

def signal_data_send(success: bool):
    """Signals the data sending status."""
    if success:
        print("[LED] Signal: Data sent successfully")
        # Blink green (if available) or a specific sequence.
        # Since it's just one LED, we'll blink rapidly 3 times.
        _blink_led(count=3, on_duration=0.05, off_duration=0.05)
    else:
        print("[LED] Signal: Data sending failed")
        # Blink red (if available) or a long sequence.
        # Blink slowly 2 times.
        _blink_led(count=2, on_duration=0.3, off_duration=0.2)

def signal_general_error():
    """Signals a general/fatal error before a reset, for example."""
    print("[LED] Signal: General Error")
    # Quick and continuous sequence (SOS-like)
    for _ in range(3): # Repeat SOS sequence 3x
        _blink_led(count=3, on_duration=0.05, off_duration=0.05) # S
        time.sleep(0.1)
        _blink_led(count=3, on_duration=0.15, off_duration=0.05) # O
        time.sleep(0.1)
        _blink_led(count=3, on_duration=0.05, off_duration=0.05) # S
        time.sleep(0.3)

def signal_sensor_reading_in_progress():
    """Signals that sensor reading is in progress (optional)."""
    print("[LED] Signal: Reading sensors...")
    # Short pulse to indicate activity
    led_onboard.on()
    time.sleep(0.05)
    led_onboard.off()

if __name__ == '__main__':
    print("Testing LED signals...")
    signal_script_start()
    time.sleep(1)

    print("Testing Wi-Fi connected signal...")
    signal_wifi_status(True)
    time.sleep(1)

    print("Testing Wi-Fi failure signal...")
    signal_wifi_status(False)
    time.sleep(1)

    print("Testing data send success signal...")
    signal_data_send(True)
    time.sleep(1)

    print("Testing data send failure signal...")
    signal_data_send(False)
    time.sleep(1)

    print("Testing sensor reading signal...")
    signal_sensor_reading_in_progress()
    time.sleep(1)

    print("Testing general error signal (long)...")
    signal_general_error()
    print("LED test completed.")
