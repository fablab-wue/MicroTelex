#!python3
"""
...luminosity in 33 steps (0..32)

Usage:
import statusLED
s = statusLED.StatusLED(5)
s.attractor(24)
s.add(-8)
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

class StatusLED:
    MAX_PWM = 1023
    MAX_VAL = 32

    def __init__(_, led:int = 5, invert:bool=False):
        _._pin = Pin(led, Pin.OUT, value=0)
        _._pwm = PWM(_._pin, freq=125, duty=512)
        _._invert = invert
        _._val = 0
        _._val_last = -1
        _._atr = 16

        _._timer = Timer(2)
        _._timer.init(period=50, mode=Timer.PERIODIC, callback=_._timer_callback)

    def deinit(_):
        _._timer.deinit()

    # -----

    def __del__(_):
        _.deinit()
        del _._timer

    # -----

    def set(_, val:int):
        _._val = val

    # -----

    def add(_, val:int):
        _._val += val

    # -----

    def attractor(_, val:int):
        _._atr = val

    # -----

    def _timer_callback(_, dummy=0):

        # move to attractor
        if _._val > _._atr:
            _._val -= 1
        elif _._val < _._atr:
            _._val += 1
        #print('.', end='')

        # limits
        val = _._val
        if val < 0:
            val = 0
        elif val > _.MAX_VAL:
            val = _.MAX_VAL
        
        if val != _._val_last:
            # to PWM
            _._val_last = val
            val *= val   # gamma correction
            if val > _.MAX_PWM:
                val = _.MAX_PWM
            if _._invert:   # low active LEDs
                val = _.MAX_PWM - val
            _._pwm.duty(val)

###############################################################################
'''

from machine import Timer

tim = Timer(1)
tim.init(period=5000, mode=Timer.PERIODIC, callback=lambda t:print(5))
tim.init(period=2000, mode=Timer.PERIODIC, callback=lambda t:print(2))



from machine import Timer
tim1 = Timer(1)
tim2 = Timer(2)
print(tim1, tim2)
tim1.init(period=5000, mode=Timer.PERIODIC, callback=lambda t:print(5))
tim2.init(period=2000, mode=Timer.PERIODIC, callback=lambda t:print(2))

'''