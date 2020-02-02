#!python3
"""
Communication with historic teletype (TTY, german: Fernschreiber) on chip ESP8266 or ESP32

Default ESP8266 Pinout on Board 'Wemos D1 mini (pro)':
TX      D1  GPIO 5
RX      D3  GPIO 0 (internal pullup, boot, (board Button))
RLY     D2  GPIO 4 (high active)
LED     D4  GPIO 2 (low active, board LED to Vcc)
ONS     D0  GPIO 16 (NO internal pulldown)
Free    D5...D8, A0

Default ESP32 Pinout on Board 'NodeMCU-32S':
TX      GPIO 4
RX      GPIO 0 (internal pullup, boot, board Button)
RLY     GPIO 12 (high active)
LED     GPIO 2 (high active, board LED to GND)
Free    GPIO 5, 13...19, 21...27, 32...33, (34, 35, 36, 39 readonly)
NotUse  GPIO 1, 3, 6...11

Example:
import telex
t = telex.Telex('myconfig.json')
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
import io

###############################################################################

HELP_TEXT = '''
Escape shortcuts:
<ESC> Q   Quit
<ESC> A   Power up
<ESC> Z   Power down
<ESC> D   Dial mode
<ESC> T   Text mode
<ESC> R   'ryry...'
<ESC> F   'quick brown fox...'
<ESC> K   'kaufen sie...'
<ESC> H   This help
'''

DEFAULT_CONFIG_FILE = 'telex.json'

MP_STREAM_POLL_RD = const(1)
MP_STREAM_POLL_WR = const(4)
MP_STREAM_POLL = const(3)
MP_STREAM_ERROR = const(-1)

###############################################################################

class Telex(io.IOBase):
    def __init__(_, cnfName:str=None):

        _._cnfName = cnfName
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
        _._modeBM = 0

        # Pins
        
        if 'RLY' in cnfPin:
            cp = cnfPin['RLY']
            _._pinRly = Pin(cp['GPIO'], Pin.OUT, value=0)
            _._invertRly = 1 if cp.get('INVERT', False) else 0
        if 'LED_GPIO' in cnfPin:
            cp = cnfPin['LED']
            pinLED = Pin(cp['GPIO'], Pin.OUT, value=0)
            _._pwmLED = PWM(pinLED, freq=125, duty=512)
            _._invertLED = 1 if cp.get('INVERT', False) else 0
        if 'ONS_GPIO' in cnfPin:
            cp = cnfPin['ONS']
            try:
                _._pinOnS = Pin(cp['GPIO'], Pin.IN, Pin.PULL_UP)
            except:   # pin 16 of ESP8266 has no pullup
                _._pinOnS = Pin(cp['GPIO'], Pin.IN)
            _._invertOnS = 1 if cp.get('INVERT', False) else 0
            _._swState = 0
            _._swCounter = 0

        # TTY
        
        assert('TXD' in cnfPin)
        cp = cnfPin['TXD']
        txdGPIO = cp['GPIO']
        txdInvert = cp.get('INVERT', False)
        
        assert('RXD' in cnfPin)
        cp = cnfPin['RXD']
        rxdGPIO = cp['GPIO']
        rxdInvert = cp.get('INVERT', False)
        
        baud = _.cnf.get('BAUD', 50)
        
        timer = 2   #TODO default timer dependent on baudrate
        if baud >= 70:
            timer = 1
        
        _._tty = TTY(baud, timer, txdGPIO, rxdGPIO, txdInvert, rxdInvert)

        if 'TN' in _.cnf and _.cnf['TN']:
            TN = '[\r\n' + _.cnf['TN'] + ']'
            codeTN = _._bm.encodeA2BM(TN)
            #_._tty.setTN(codeTN)
            _._TN = codeTN
            #print(_.cnf['TN'], codeTN)   #debug
            _._bm.reset()

        _._dialMode = _.cnf.get('DIAL_MODE', _._tty.DIAL_MODE_PULSE)
        _._tty.setDialMode(_._dialMode)

        # public

        _.run = True

    # -----

    def __del__(_):
        print('__del__')
        del _._tty

    # -----

    def __enter__(_):
        return _

    # -----

    def __exit__(_, type, value, tb):
        print('__exit__')
        if _._tty:
            del _._tty

    # -----

    def __iter__(_):
        return _

    # -----

    def __next__(_):
        _._syncCharBuffer()
        if _._rxCharBuffer:
            return _._rxCharBuffer.pop(0)
        else:
            raise StopIteration()

    # -----

    def __call__(_):
        print('Hello')
        
    # -----

    def __repr__(_):
        try:
            return "<Telex '{}', tx={}{}, rx={}{}, baud={}, tty={}>".format(
                _.cnf['NAME'],
                _.cnf['PIN']['TXD']['GPIO'],
                'i' if _.cnf['PIN']['TXD'].get('INVERT', False) else '',
                _.cnf['PIN']['RXD']['GPIO'],
                'i' if _.cnf['PIN']['RXD'].get('INVERT', False) else '',
                _.cnf['BAUD'],
                _._tty.getStateStr()
                )
        except:
            return '<Telex>'

    # =====

    def ioctl(_, req, arg):
        # control stream to be used with select
        ret = MP_STREAM_ERROR
        if req == MP_STREAM_POLL:
            ret = 0
            if arg & MP_STREAM_POLL_RD:
                if _._tty.any() or _._rxCharBuffer:
                    ret |= MP_STREAM_POLL_RD
            if arg & MP_STREAM_POLL_WR:
                if True:
                    ret |= MP_STREAM_POLL_WR
        return ret

    # =====

    def _syncCharBuffer(_) -> None:
        if not _._tty.any():
            return

        while _._tty.any():
            bs = _.readCode()
            a = _._bm.decodeBM2A(bs)
            if a:
                _._rxCharBuffer.append(a)

    # -----

    def write(_, ascii:str) -> None:
        # convert the given ASCII text to baudot-murray-code and send to tty
        _._syncCharBuffer()

        for a in ascii:
            if a == '\x1B':   # escape char
                _._rxCharBuffer.append('<ESC>')
                _._escape = not _._escape
                continue
                
            if _._escape:
                _._escape = False
                _.cmd(a)
            else:   # normal text
                #print(a.lower(), end='')   #debug
                bs = _._bm.encodeA2BM(a)
                if bs:
                    _.writeCode(bs)

    # -----

    def any(_) -> int:
        # is any ASCII char or escape sequence available?
        _._syncCharBuffer()
        return len(_._rxCharBuffer)

    # -----

    def read(_, count:int=1) -> str:
        # get a single translated char or escape sequence as string
        _._syncCharBuffer()
        ret = ''
        while _._rxCharBuffer and count > 0:
            ret += _._rxCharBuffer.pop(0)
            count -= 1
        return ret

    # -----

    def writeCode(_, codes: list) -> None:
        for code in codes:
            if code == 0x1F:   # LTRS
                _._modeBM = 0
            elif code == 0x1B:   # FIGS
                _._modeBM = 1
            elif code == 0x09 and _._modeBM == 1 and _._TN:   # WRU?, WerDa?
                _._tty.readAdd(_._TN)
                continue
            _._tty.write([code])

    # -----

    def anyCode(_) -> int:
        return _._tty.any()

    # -----

    def readCode(_, count:int=1) -> list:
        codes = _._tty.read(count)
        for code in codes:
            if code == 0x1F:   # LTRS
                _._modeBM = 0
            elif code == 0x1B:   # FIGS
                _._modeBM = 1
        return codes

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
            _.write('ry'*20)
        elif c == 'F':
            _.write('the quick brown fox jumps over the lazy dog')
        elif c == 'K':
            _.write('kaufen sie jede woche vier gute bequeme pelze xy 1234567890')
        elif c == 'H':
            _._rxCharBuffer.append(HELP_TEXT)
        else:
            c = '?'
        _._rxCharBuffer.append('{' + c + '}')

    # -----

    def power(_, enable:bool) -> None:
        if _._pinRly:
            #TODO ignore inputs for 1 sec
            _._pinRly.value(enable ^ _._invertRly)

    # -----

    def dial(_, enable:bool) -> None:
        _._tty.dial(enable)
        if enable and _._dialMode == _._tty.DIAL_MODE_KEY:
            _.power(True)


    # -----

    @property
    def char(_) -> str:
        ret = ''
        _._syncCharBuffer()
        while _._rxCharBuffer:
            ret += _._rxCharBuffer.pop(0)
        return ret

    @char.setter
    def char(_, ascii:str):
        _.write(ascii)

###############################################################################




