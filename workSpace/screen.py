#!python3
"""
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

# import system modules used in this module
import gc
gc.collect()
import select
import sys

# preimport system modules to reduce memory usage in importing telex module
if MICROPYTHON:
    gc.collect()
    import machine
    gc.collect()
    import json
    gc.collect()
    import tty
    gc.collect()

# import telex module
import telex

REPLACE = {
  '\n': '\r\n',
  '<': '\r',
  '|': '\n',
}

def run(cnfName:str=None):
    print('')
    #print('=== MicroTelex ===')
    print(r"   __  ____            ______    __       ")
    print(r"  /  |/  (_)__________/_  __/__ / /____ __")
    print(r" / /|_/ / / __/ __/ _ \/ / / -_) / -_) \ /")
    print(r"/_/  /_/_/\__/_/  \___/_/  \__/_/\__/_\_\ ")
    print(r"                                          ")
    print('')
    print('Platform:        ', sys.platform)
    print('Version:         ', sys.version)
    print('Implementation:  ', sys.implementation)
    print('Free Memory:     ', gc.mem_free())

    with telex.Telex(cnfName) as t:
        print('Config:          ', t.cnf)
        print('')

        # polling from stdin
        poller = select.poll()
        poller.register(sys.stdin, select.POLLIN)

        while t.run:
            # wait till character from stdin or timeout
            events = poller.poll(50)
            #events, x, y = select.select([sys.stdin], [], [], 0.075)
            # print(events)

            for file in events:
                ch = file[0].read(1).lower()
                #print('ch', ch, type(ch))
                #print(ord(ch))
                ch = REPLACE.get(ch, ch)
                t.write(ch)
                print(ch, end='')

            if t.any():
                ch = t.read()
                print(ch, end='')

        pass


if __name__ == "__main__":
    run()



