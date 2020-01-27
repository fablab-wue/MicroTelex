
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

    import gc
    gc.collect()
    from machine import Pin
    from machine import PWM
    gc.collect()

else:  # CPython
    #import os
    #import json
    #from threading import RLock

    import gc
    from debug_pc.machine import Pin
    from debug_pc.machine import PWM

    def const(x):
        return x

gc.collect()
from tty import TTY
gc.collect()
from bmcode import BaudotMurrayCode
gc.collect()
import json
gc.collect()

###############################################################################

HELP_TEXT = '''
Option HELP not licensed!
Upgrade to PRO version...
'''

DEFAULT_CONFIG_FILE = 'telex.json'

###############################################################################

class Telex():
    def __init__(_, cnfName:str=None):

        _._rxCharBuffer = []
        _._escape = False

        # config file

        if cnfName is None:
            cnfName = DEFAULT_CONFIG_FILE
        with open(cnfName, 'r') as f:
            _.cnf = json.load(f)
        assert _.cnf

        if 'PIN' not in _.cnf:
            raise Exception('Missing PIN section in json file')

        cnfPin = _.cnf['PIN']

        # coder from BaudotMurrayCode to ASCII
        
        _._bm = BaudotMurrayCode()

        # Pins
        
        if 'RLY_GPIO' in cnfPin:
            _._pinRly = Pin(cnfPin['RLY_GPIO'], Pin.OUT, value=0)
        if 'LED_GPIO' in cnfPin:
            pinLED = Pin(cnfPin['LED_GPIO'], Pin.OUT, value=0)
            _._pwmLED = PWM(pinLED, freq=125, duty=512)
        if 'ONS_GPIO' in cnfPin:
            _._pinOnS = Pin(cnfPin['ONS_GPIO'], Pin.IN, Pin.PULL_UP)
            _._swState = 0
            _._swCounter = 0

        # TTY
        
        txdInvert = cnfPin.get('TXD_INVERT', False)
        rxdInvert = cnfPin.get('RXD_INVERT', False)
        baud = _.cnf.get('BAUD', 50)
        timer = 2   #TODO default timer dependent on baudrate
        if baud >= 70:
            timer = 1
        _._tty = TTY(baud, timer, cnfPin['TXD_GPIO'], cnfPin['RXD_GPIO'], txdInvert, rxdInvert)

        if 'TN' in _.cnf and _.cnf['TN']:
            TN = '[\r\n' + _.cnf['TN'] + ']'
            codeTN = _._bm.encodeA2BM(TN)
            _._tty.setTN(codeTN)
            print(_.cnf['TN'], codeTN)   #debug
            _._bm.reset()

        # public

        _.run = True
        _.keyDial = False

    # -----

    def __del__(_):
        del _._tty

    # -----

    def __enter__(_):
        return _

    # -----

    def __exit__(_, type, value, tb):
        if _._tty:
            del _._tty

    # -----

    def __repr__(_):
        return "<Telex class '{}', tx={}{}, rx={}{}, baud={}, tty={}>".format(
            _.cnf['NAME'],
            _.cnf['PIN']['TXD_GPIO'],
            'i' if _.cnf['PIN'].get('TXD_INVERT', False) else '',
            _.cnf['PIN']['RXD_GPIO'],
            'i' if _.cnf['PIN'].get('RXD_INVERT', False) else '',
            _.cnf['BAUD'],
            _._tty.getStateStr()
            )

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
                #print(a.lower(), end='')   #debug
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

    def cmd(_, c:str) -> None:
        c = c.upper()

        if c == 'Q':
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
        elif c == 'F':
            _.write('THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')
        elif c == 'H':
            print(HELP_TEXT)
        else:
            c = '?'
        print('{' + c + '}', end='')

    # -----

    def power(_, enable:bool) -> None:
        if _._pinRly:
            #TODO ignore inputs for 1 sec
            _._pinRly.value(enable)

    # -----

    def dial(_, enable:bool) -> None:
        pulseDial = _.cnf.get('PULSE_DIAL', False)
        if pulseDial:
            _._tty.dial(enable)
        else:
            _.keyDial = enable
            if _.keyDial:
                _.power(True)

    # -----

    @property
    def t(_) -> str:
        ret = ''
        _._syncCharBuffer()
        while _._rxCharBuffer:
            ret += _._rxCharBuffer.pop(0)
        return ret

    @t.setter
    def t(_, ascii:str):
        _.write(ascii)

###############################################################################



