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
gc.collect()

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

    with telex.Telex(cnfName) as tlx:
        #print('Config:          ', tlx.cnf)
        print('Config Name:     ', tlx.cnf['NAME'])
        print('')

        # polling from stdin
        #TEST poller = select.poll()
        #TEST poller.register(sys.stdin, select.POLLIN)

        while tlx.run:
            # wait till character from stdin or timeout
            #TEST events = poller.poll(50)
            #TEST print(events)
            readables, writables, exceptionals = select.select([sys.stdin, tlx], [], [], 0.5)

            for readable in readables:
                a = readable.read(1)
                if a:
                    #print('a', a, type(a))
                    #print(ord(a))
                    if readable == tlx:   # from teletype
                        print(a, end='')
                    else:   # from user
                        a = a.lower()
                        a = REPLACE.get(a, a)
                        print(a, end='')
                        tlx.write(a)

        print('EXIT')


if __name__ == "__main__":
    run()

run()
