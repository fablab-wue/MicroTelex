#!python3
"""
Communication with historic teletype (TTY, german Fernschreiber) on chip ESP8266 or ESP32

Example Pinout for ESP8266 on Board 'Wemos D1 mini (pro)':
TX      D4  GPIO2 (low active, board LED)
RX      D3  GPIO0 (with pullup, boot, (board Button))
Free    D0...D2, D5...D8, A0

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
    from machine import Pin
    from machine import PWM
    from machine import Timer

else:  # CPython
    from debug_pc.machine import Pin
    from debug_pc.machine import PWM
    from debug_pc.machine import Timer

    def const(x):
        return x

###############################################################################

STATE_MASK_LISTEN = const(0x10)
STATE_MASK_CAN_TX = const(0x20)
STATE_MASK_DIAL = const(0x40)
STATE_MASK_WAIT = const(0x80)

STATE_LISTEN = const(STATE_MASK_LISTEN)
STATE_LISTEN_CAN_TX = const(STATE_MASK_LISTEN | STATE_MASK_CAN_TX)

STATE_RX = const(0x1)
STATE_TX = const(0x2)
STATE_TX_LISTEN = const(0x2 | STATE_MASK_LISTEN)

STATE_OFF = const(0xF)

STATE_DIAL_WAIT = const(STATE_MASK_DIAL | 0x0)
STATE_DIAL_PULSE = const(STATE_MASK_DIAL | 0x1)
STATE_DIAL_PAUSE = const(STATE_MASK_DIAL | 0x2)

BMC_DIAL_DIGITS = (22, 23, 19, 1, 10, 16, 21, 7, 6, 24)

###############################################################################


class TTY:
    DIAL_MODE_PULSE = 0
    DIAL_MODE_KEY = 1

    def __init__(_, baud:float = 50, timer:int = 5, tx:int = 2, rx:int = 0, txInvert:bool=False, rxInvert:bool=False):

        # state machine

        _._tick = 0
        _._tickCounter = 0
        _._state = STATE_OFF
        _._modeBM = 0
        _._TN = None

        # Pins

        _._rxInvert = 1 if rxInvert else 0   # be sure that value is 0/1 not False/True for XOR
        _._txInvert = 1 if txInvert else 0
        _._pinRx = Pin(rx, Pin.IN, Pin.PULL_UP)
        _._pinTx = Pin(tx, Pin.OUT, value=1 ^ _._txInvert)
        _._setPinValueTX(1)

        # timer for cyclic handler call
        _._timer = Timer(-1)

        _.init(baud, timer)

    # -----

    def init(_, baud:float = 50, timer:int = 5):
        slice = (1000. / timer) / baud

        _._len1charT = int(slice*7.5 + 0.5)
        _._len1secT = 1000 // timer

        # rx

        _._rxDataTs = []
        t = slice * 0.5
        _._checkStartT = int(t + 0.5)
        for i in range(5):
            t += slice
            _._rxDataTs.append(int(t + 0.5))
        t += slice
        _._checkStopT = int(t + 0.5)
        t *= 3
        _._rxLineT = int(t + 0.5)
        _._rxData = 0
        _._rxMask = 1
        _._rxDataBuffer = []

        # tx

        _._txDataTs = []
        t = 0.
        for i in range(5):
            t += slice
            _._txDataTs.append(int(t + 0.5))
        t += slice
        _._txStopT = int(t + 0.5)
        t += slice * 1.5
        _._txEndT = int(t + 0.5)
        _._txData = 21
        #_._txDataBuffer = [21, 10, 0]   #debug
        _._txDataBuffer = []

        #  dial

        _._dialMode = _.DIAL_MODE_PULSE
        _._dialEndT = 200 // timer   # ticks for dial a digit end - 200ms
        _._dialActive = False
        _._dialCounter = 0

        # TIMER

        _._timer.init(period=timer, mode=Timer.PERIODIC, callback=_._timerHandler)

    # -----

    def deinit(_):
        _._timer.deinit()

    # -----

    def __del__(_):
        _.deinit()
        del _._timer
        del _._pinRx
        del _._pinTx
        _._rxDataBuffer = None
        _._txDataBuffer = None

    # -----

    def __repr__(_):
        return '<TTY, st={}>'.format(
            _.getStateStr()
            )

    # =====

    def _setState(_, stateNew: int, tickNew=0) -> None:
        _._state = stateNew
        _._tick = tickNew
        _._tickCounter = 0

    # -----

    def _getPinValueRX(_) -> int:
        return _._pinRx.value() ^ _._rxInvert

    # -----

    def _isStablePinValueRX(_, val:int, ticks:int) -> bool:
        if _._pinRx.value() ^ _._rxInvert == val:
            _._tickCounter += 1
            if _._tickCounter >= ticks:
                return True
        else:
            _._tickCounter = 0
        return

    # -----

    def _setPinValueTX(_, val:int) -> None:

        _._pinTx.value(val ^ _._txInvert)

    # =====

    def _timerHandler(_, x=None) -> None:
        _._tick += 1

        if _._state & STATE_MASK_WAIT:
            pass

        # DIAL

        elif _._state & STATE_MASK_DIAL:
            valRX = _._getPinValueRX()
            if _._state == STATE_DIAL_WAIT:
                if valRX:
                    _._tickCounter = 0
                    if not _._dialActive:
                        _._setState(STATE_LISTEN)
                else:
                    _._tickCounter += 1
                    if _._tickCounter >= 3:
                        _._dialCounter = 0
                        _._setState(STATE_DIAL_PULSE)
            elif _._state == STATE_DIAL_PULSE:
                if valRX:
                    _._tickCounter += 1
                    if _._tickCounter >= 3:
                        _._dialCounter += 1
                        _._setState(STATE_DIAL_PAUSE)
                else:
                    _._tickCounter = 0
                    if _._tick == _._len1secT:
                        _._rxDataBuffer.append(0xED)  # signal dial error
                        _._dialActive = False
                        _._setState(STATE_LISTEN)
            elif _._state == STATE_DIAL_PAUSE:
                if valRX:
                    _._tickCounter = 0
                    if _._tick >= _._dialEndT:
                        if _._dialCounter >= 10:  # dialing a '0' gets 10 pulses
                            _._dialCounter = 0
                        # signal dialed digit
                        _._rxDataBuffer.append(0xD0 + _._dialCounter)
                        _._setState(STATE_DIAL_WAIT)
                else:
                    _._tickCounter += 1
                    if _._tickCounter >= 3:
                        _._setState(STATE_DIAL_PULSE)

        # LISTEN

        elif _._state & STATE_MASK_LISTEN:
            valRX = _._getPinValueRX()
            if _._state == STATE_LISTEN:
                if valRX:
                    if _._tick == _._len1charT:
                        _._setState(STATE_LISTEN_CAN_TX)
                        if _._dialActive and _._dialMode == _.DIAL_MODE_PULSE:
                            _._setState(STATE_DIAL_WAIT)
                else:
                    _._setState(STATE_RX)
            elif _._state == STATE_LISTEN_CAN_TX:
                if valRX:
                    if _._dialActive and _._dialMode == _.DIAL_MODE_PULSE:
                        _._setState(STATE_DIAL_WAIT)
                else:
                    _._setState(STATE_RX)
            elif _._state == STATE_TX_LISTEN:
                # check for valid stop bit at TX end or incoming RX
                if valRX:
                    if _._tick == _._txEndT:
                        _._setState(STATE_LISTEN_CAN_TX)
                else:
                    if _._tick == _._checkStopT + 1:
                        #TODO send error code
                        _._setState(STATE_LISTEN)
                    else:
                        _._setState(STATE_RX)
            pass

        # TX

        elif _._state == STATE_TX:
            if _._tick in _._txDataTs:
                _._setPinValueTX(_._txData & 1)
                _._txData >>= 1
            elif _._tick == _._txStopT:
                _._setPinValueTX(1)
            elif _._tick == _._checkStopT:
                _._setState(STATE_TX_LISTEN, _._tick)

        # RX

        elif _._state == STATE_RX:
            valRX = _._getPinValueRX()
            if _._tick == 1:
                pass
                #  print('R', end='')   #debug
            elif _._tick == _._checkStartT:
                # check for valid start bit
                if valRX:
                    # only spike -> ignore
                    _._setState(STATE_LISTEN)
                else:
                    # correct start bit -> prepare rx data
                    _._rxData = 0
                    _._rxMask = 1
            elif _._tick in _._rxDataTs:
                # data bit received
                if valRX:
                    _._rxData |= _._rxMask
                _._rxMask <<= 1
            elif _._tick >= _._checkStopT:
                # check for valid stop bit
                if valRX:
                    # correct stop bit -> send rx data
                    if _._dialActive:
                        if _._rxData in BMC_DIAL_DIGITS:
                            n = BMC_DIAL_DIGITS.index(_._rxData)
                            _._rxDataBuffer.append(0xD0 + n)
                    else:
                        _._rxDataBuffer.append(_._rxData)
                    _._setState(STATE_LISTEN)
                else:
                    # line is down, may be off-mode
                    _._rxData |= _._rxMask
                    if _._tick == _._len1charT*2:
                        _._setState(STATE_OFF)

        # OFF

        elif _._state == STATE_OFF:
            valRX = _._getPinValueRX()
            if _._tick == 1:
                _._rxDataBuffer.append(0xA0)  # signal line low
            if valRX:
                _._tickCounter += 1
                if _._tickCounter >= _._len1charT:
                    _._rxDataBuffer.append(0xA1)  # signal line high
                    _._setState(STATE_LISTEN)
                    # send
            else:
                _._tickCounter = 0

        if _._state & STATE_MASK_CAN_TX:
            if _._txDataBuffer:
                _._txData = _._txDataBuffer.pop(0)
                if _._txData is bytes:
                    _._txData = int(_._txData)
                _._setPinValueTX(0)
                _._setState(STATE_TX)

        pass

    # =====

    def write(_, codes: list):
        for code in codes:
            if code == 0x1F:
                _._modeBM = 0
            elif code == 0x1B:
                _._modeBM = 1
            elif code == 0x09 and _._modeBM == 1 and _._TN:   # WRU?, WerDa?
                _._rxDataBuffer += _._TN
                continue
            _._txDataBuffer.append(code)

    # -----

    def any(_) -> int:
        return len(_._rxDataBuffer)

    # -----

    def read(_, len: int = -1) -> int:
        if _._rxDataBuffer:
            return [_._rxDataBuffer.pop(0)]
        else:
            return []

    # -----

    def dial(_, enable:bool) -> None:
        _._dialActive = enable

    # -----

    def getStateStr(_) -> str:
        return '{}{}:{}'.format(
            hex(_._state)[2:],
            '#' if _._dialActive else '',
            _._getPinValueRX()
            )

    # =====

    def setTN(_, TN:list) -> None:
        _._TN = TN

    # -----

    def getTN(_) -> list:
        return _._TN

    # =====

    def setDialMode(_, mode:int) -> None:
        _._dialMode = mode

    # -----

    def getDialMode(_) -> int:
        return _._dialMode

###############################################################################
