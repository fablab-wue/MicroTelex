#!python3
"""
"""
__author__      = "Jochen Krapf"
__email__       = "jk@nerd2nerd.org"
__copyright__   = "Copyright 2020, JK"
__license__     = "GPL3"
__version__     = "0.0.1"

from tty import TTY

def main():
    tty = TTY()

    x = tty.read()

    for i in range(200):
        tty._timerHandler()

    print(tty._rxDataBuffer)

    while tty.anyChar():
        a = tty.getChar()
        print(a)

    return

    for i in range(4):
        tty._timerHandler()

    #self.sendData(5)
    #self.sendData(3)

    for i in range(80):
        tty._timerHandler()


main()

exit
from machine import Timer
from machine import Pin

pin = Pin(2, Pin.OUT)

tim = 0

def handler(timer):
    global tim, pin
    tim += 1
    if tim & 0xFF == 0:
        print(tim)
    pin.value(tim & 0x80)

t = Timer(-1)
t.init(period=5, mode=Timer.PERIODIC, callback=handler)
