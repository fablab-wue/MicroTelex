#!python3

__author__      = "Jochen Krapf"
__email__       = "jk@nerd2nerd.org"
__copyright__   = "Copyright 2020, JK"
__license__     = "GPL3"
__version__     = "0.0.1"

###############################################################################

class Pin:
    IN = 0
    OUT = 1
    OPEN_DRAIN = 2
    PULL_UP = 10
    PULL_DOWN = 11

    def __init__(self, pin:int=2, mode:int=-1, pull:int=-1, *, value:int=0) -> None:
        #self.rxDebug = '1'
        #self.rxDebug = '1111101111001111111000011110000111100010111111000011111111000011111111111111110111111110000111111111111111111111'
        self.rxDebug = '111110000111100001111000000001111110000111111110000000000001111111111111111111111111'
        #self.rxDebug = '1111101111111111111111111111111'
        #self.rxDebug = '11111000000000000000000000000000000000001111111111111111111111111'
        #self.rxDebug = '11111000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001111111111111111111111111'

    def init(self, mode=-1, pull=-1, *, value:int, drive, alt) -> None:
        pass

    def value(self, v:int=None) -> int:
        if v == None:
            rxPinValue = 1
            if self.rxDebug:
                c = self.rxDebug[0]
                self.rxDebug = self.rxDebug[1:]
                if c != '1':
                    rxPinValue = 0
            return rxPinValue
        else:
            pass
            #print(v, end='')

###############################################################################

class PWM:
    def __init__(self, pin:Pin, freq:int=200, duty:int=512) -> None:
        pass

    def freq(self, freq=None) -> int:
        pass

    def duty(self, freq=None) -> int:
        pass

    def deinit(self) -> None:
        pass    

###############################################################################

class Timer:
    PERIODIC = 0
    ONE_SHOT = 1

    def __init__(self, id:int) -> None:
        pass

    def init(self, period:int=5, mode:int=PERIODIC, callback=None) -> None:
        pass

    def deinit(self) -> None:
        pass    

###############################################################################

