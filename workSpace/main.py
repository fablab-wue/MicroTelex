import network
import time

SSID = "<your-SSID>"
PWD = "<your-password>"

print('Connecting to WiFi "{}"'.format(SSID))

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(SSID, PWD) # Connect to an AP

while not sta_if.isconnected():  # Check for successful connection
    print(".", end='')
    time.sleep(1)

print("")
print(sta_if.ifconfig())

print("ESP READY")

import tty
import telex
from term import *
from upysh import *
