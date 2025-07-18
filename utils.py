import time
import machine

def get_timestamp():
    """Returns the current date and time formatted as a string."""
    t = time.localtime()
    return f"{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

def hard_reset():
    """
    Triggers a hard reset of the device.
    This is a function that will call the WTC to reset the device.
    """
    print(f"[{get_timestamp()}] [SYSTEM] Hard reset triggered. Resetting device...")
    time.sleep(1) # Delay to ensure the log message is sent
    machine.reset()


if __name__ == '__main__':
    print("Current formatted time:", get_timestamp())
    time.sleep(2)
    print("Current formatted time (after 2s):", get_timestamp())
