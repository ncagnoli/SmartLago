import time

def get_timestamp():
    """Returns the current date and time formatted as a string."""
    t = time.localtime()
    return f"{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

if __name__ == '__main__':
    print("Current formatted time:", get_timestamp())
    time.sleep(2)
    print("Current formatted time (after 2s):", get_timestamp())
