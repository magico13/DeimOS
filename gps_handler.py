import time
import datetime
import serial
from threading import Thread

import adafruit_gps

uart = None
gps = None
last_print = time.monotonic()

def initialize():
    global uart
    global gps
    uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=3000)
    gps = adafruit_gps.GPS(uart, debug=False)
    # Turn on the basic GGA and RMC info (what you typically want)
    gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    # Set update rate to once a second (1hz) which is what you typically want.
    gps.send_command(b'PMTK220,1000')

def has_fix():
    return gps.has_fix

def get_time():
    if not has_fix():
        return datetime.datetime.utcnow()
    return datetime.datetime(gps.timestamp_utc.tm_year, gps.timestamp_utc.tm_mon, gps.timestamp_utc.tm_mday,
        gps.timestamp_utc.tm_hour, gps.timestamp_utc.tm_min, gps.timestamp_utc.tm_sec)

def get_location():
    if not has_fix():
        return (0, 0)
    return (gps.latitude, gps.longitude)

def get_speed():
    if not has_fix(): return -1
    if not gps.speed_knots: return -1
    return gps.speed_knots * 1.15078 #1.15078 mph per knot

def start_loop_thread():
    thread =  Thread(target=loop)
    thread.start()

def loop():
    # https://github.com/adafruit/Adafruit_CircuitPython_GPS/blob/master/examples/gps_simpletest.py
    global last_print
    while True:
        # Make sure to call gps.update() every loop iteration and at least twice
        # as fast as data comes from the GPS unit (usually every second).
        # This returns a bool that's true if it parsed new data (you can ignore it
        # though if you don't care and instead look at the has_fix property).
        gps.update()
        # Every second print out current location details if there's a fix.
        current = time.monotonic()
        if current - last_print >= 1.0:
            last_print = current
            if not gps.has_fix:
                # Try again if we don't have a fix yet.
                continue
