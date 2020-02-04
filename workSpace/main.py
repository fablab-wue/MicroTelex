import network
import time
import uasyncio as asyncio
import machine
import gc

from wifi_manager import WifiManager
WifiManager.setup_network()
#WifiManager.start_managing()

'''
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

'''

print("ESP READY")

import tty
import telex
from term import *
try:
    from upysh import *
except:
    pass

import ntptime
ntptime.settime()

rtc = machine.RTC()
print('Date Time:', rtc.datetime())

gc.collect()
print('Free MEM:', gc.mem_free())
