import machine
import time
import config

try:
    led_onboard = machine.Pin(config.ONBOARD_LED_PIN, machine.Pin.OUT)
except TypeError:
    led_onboard = machine.Pin(int(config.ONBOARD_LED_PIN), machine.Pin.OUT)

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
    time.sleep(0.5)

def signal_wifi_status(connected: bool):
    """Signals the Wi-Fi connection status."""
    if connected:
        print("[LED] Signal: Wi-Fi Connected")
        _blink_led(count=2, on_duration=0.1, off_duration=0.1)
    else:
        print("[LED] Signal: Wi-Fi connection failed")
        _blink_led(count=1, on_duration=0.5, off_duration=0.1)

def signal_data_send(success: bool):
    """Signals the data sending status."""
    if success:
        print("[LED] Signal: Data sent successfully")
        _blink_led(count=3, on_duration=0.05, off_duration=0.05)
    else:
        print("[LED] Signal: Data sending failed")
        _blink_led(count=2, on_duration=0.3, off_duration=0.2)

def signal_general_error():
    """Signals a general/fatal error."""
    print("[LED] Signal: General Error")
    # SOS-like sequence
    for _ in range(3):
        _blink_led(count=3, on_duration=0.05, off_duration=0.05) # S
        time.sleep(0.1)
        _blink_led(count=3, on_duration=0.15, off_duration=0.05) # O
        time.sleep(0.1)
        _blink_led(count=3, on_duration=0.05, off_duration=0.05) # S
        time.sleep(0.3)

def signal_sensor_reading_in_progress():
    """Signals that sensor reading is in progress."""
    print("[LED] Signal: Reading sensors...")
    led_onboard.on()
    time.sleep(0.05)
    led_onboard.off()
