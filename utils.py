import time

def get_timestamp():
    """Returns the current date and time formatted as a string."""
    # Micropython's time.localtime() returns:
    # (year, month, mday, hour, minute, second, weekday, yearday)
    # weekday: 0 for Monday, 6 for Sunday
    # yearday: 1 to 366

    # ntptime.settime() needs to be called somewhere to synchronize the RTC.
    # This is usually done after Wi-Fi connection.

    t = time.localtime()
    # Format: YYYY-MM-DD HH:MM:SS
    return f"{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

if __name__ == '__main__':
    # Quick test of the function
    print("Current formatted time:", get_timestamp())
    time.sleep(2)
    print("Current formatted time (after 2s):", get_timestamp())
