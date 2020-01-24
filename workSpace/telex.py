
#!python3
"""
Communication with historic teletype (TTY, german: Fernschreiber) on chip ESP8266 or ESP32

Default ESP8266 Pinout on Board 'Wemos D1 mini (pro)':
TX      D3  GPIO 0 (with pullup, boot, board Button)
RX      D2  GPIO 4
Relay   D1  GPIO 5 (high active)
LED     D4  GPIO 2 (low active, board LED to Vcc)
Free    D0, D5...D8, A0

Default ESP32 Pinout on Board 'NodeMCU-32S':
TX      GPIO 0 (with pullup, boot, board Button)
RX      GPIO 5
Relay   GPIO 4 (high active)
LED     GPIO 2 (high active, board LED to GND)
Free    GPIO (9...10), 12...19, 21...27, 32...35, (36, 39)
NotUse  GPIO 1, 3, 6..8, (9...10), 11, (36, 39)

Example:
import telex
t = telex.Telex(5, 2, 0, 4, 5)
if t.any():
  c = t.read()
t.write('RYRYRYRYRY')
"""
__author__ = "Jochen Krapf"
__email__ = "jk@nerd2nerd.org"
__copyright__ = "Copyright 2020, JK"
__license__ = "GPL3"
__version__ = "0.0.1"

try:  # try MicroPython
    import uos as os
    MICROPYTHON = True
except:  # CPython
    MICROPYTHON = False

if MICROPYTHON:
    #import ujson as json
    #from _thread import allocate_lock as RLock

    from machine import Pin
    from machine import PWM

else:  # CPython
    #import os
    #import json
    #from threading import RLock

    from debug_pc.machine import Pin
    from debug_pc.machine import PWM

    def const(x):
        return x

from tty import TTY
from bmcode import BaudotMurrayCode

#import sys
#import time

###############################################################################

class Telex():
    def __init__(_, baud:float=50, tx:int=4, rx:int=0, rly:int=5, led:int=2, sw:int=None, txInvert:bool=False, rxInvert:bool=False):
        _._rxCharBuffer = []
        _._escape = False

        #_.setDialMode(False)

        # coder from BaudotMurrayCode to ASCII
        
        _._bm = BaudotMurrayCode()

        # Pins
        
        _._pinRly = Pin(rly, Pin.OUT, value=0)
        pinLED = Pin(led, Pin.OUT, value=0)
        _._pwmLED = PWM(pinLED, freq=125, duty=512)
        if sw is not None:
            _._pinSw = Pin(sw, Pin.IN, Pin.PULL_UP)
            _._swState = 0
            _._swCounter = 0

        # TTY
        
        timer = 1   #TODO default timer dependent on baudrate
        if baud >= 70:
            timer = 1
        _._tty = TTY(baud, timer, tx, rx, txInvert, rxInvert)

        # public

        _.run = True

    # -----

    def __del__(_):
        del _._tty

    # -----

    def __enter__(_):
        return _

    # -----

    def __exit__(_, type, value, tb):
        if _._tty:
            #_._tty.deinit()
            del _._tty

    # =====

    def _syncCharBuffer(_) -> None:
        if not _._tty.any():
            return

        while _._tty.any():
            bs = _._tty.read()
            a = _._bm.decodeBM2A(bs)
            if a:
                _._rxCharBuffer.append(a)

    # -----

    def write(_, ascii:str) -> None:
        # convert the given ASCII text to baudot-murray-code and send to tty
        _._syncCharBuffer()

        for a in ascii:
            if a == '\x1B':   # escape char
                print('<ESC>', end='')
                _._escape = not _._escape
                continue
                
            if _._escape:
                _._escape = False
                _.cmd(a)
            else:
                print(a.lower(), end='')
                bs = _._bm.encodeA2BM(a)
                if bs:
                    _._tty.write(bs)

    # -----

    def any(_) -> int:
        # is any ASCII char or escape sequence available?
        _._syncCharBuffer()
        return len(_._rxCharBuffer)

    # -----

    def read(_) -> str:
        # get a single translated char or escape sequence as string
        _._syncCharBuffer()
        if _._rxCharBuffer:
            return _._rxCharBuffer.pop(0)
        else:
            return ''

    # =====

    def getCharMode(_) -> int:
        # return the current TTY mode - 0='A...' 1='1...'
        _._syncCharBuffer()
        return _._bm._ModeBM

    # -----

    def setDialMode(_, enable:bool) -> None:
        _.dial(enable)

    # -----

    def cmd(_, c:str) -> None:
        c = c.upper()

        if c == 'E':
            _.run = False
        elif c == 'A':
            _.power(True)
        elif c == 'Z':
            _.power(False)
        elif c == 'D':
            _.dial(True)
        elif c == 'T':
            _.dial(False)
        elif c == 'R':
            _.write('RYRYRYRYRY')
        elif c == 'Q':
            _.write('THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')
        else:
            c = '?'
        print('{' + c + '}', end='')

    # -----

    def power(_, enable:bool) -> None:
        _._pinRly.value(enable)

    # -----

    def dial(_, enable:bool) -> None:
        _._tty.dial(enable)

###############################################################################



