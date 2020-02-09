#!python3
"""
Example and test program for module telex.
It can be used as a terminal (keyboard and screen) to control a teletype based on Baudot-Murray-code.
Usage:
    >>>import term
    >>>term.run('myconfig.json')
or simpler:
    >>>from term import *
    >>>utx
"""

try:  # try MicroPython
    import uos as os
    MICROPYTHON = True
except:  # CPython
    MICROPYTHON = False
    __author__ = "Jochen Krapf"
    __email__ = "jk@nerd2nerd.org"
    __copyright__ = "Copyright 2020, JK"
    __license__ = "GPL3"
    __version__ = "0.0.1"

# import system modules used in this module
import gc
import select
import sys
import time

# import telex module
import telex
print('Free Memory 1:', gc.mem_free())
gc.collect()
print('Free Memory 1:', gc.mem_free())
time.sleep(1)
gc.collect()
print('Free Memory 1:', gc.mem_free())

###############################################################################

REPLACE = {
  '\n': '\r\n',
  '<': '\r',
  '|': '\n',
}

###############################################################################

def run(cnfName:str=None):
    print('')
    #print('=== MicroTelex ===')
    print(r"   __  ____            ______    __       ")
    print(r"  /  |/  (_)__________/_  __/__ / /____ __")
    print(r" / /|_/ / / __/ __/ _ \/ / / -_) / -_) \ /")
    print(r"/_/  /_/_/\__/_/  \___/_/  \__/_/\__/_\_\ ")
    print('')

    with telex.Telex(cnfName) as tlx:
        if tlx.verbose:
            print('Platform:        ', sys.platform)
            print('Version:         ', sys.version)
            print('Implementation:  ', sys.implementation)
            print('Free Memory:     ', gc.mem_free())
            #print('Config:          ', tlx.cnf)
            print('Config Name:     ', tlx.cnf['NAME'])
            if 'FAKE_TN' in tlx.cnf and tlx.cnf['FAKE_TN']:
                print('Fake TN:         ', tlx.cnf['FAKE_TN'])
            print('Telex Object:    ', tlx)
            print('Type <ESC> H for Help')
            #print('')
        print('='*42)

        # polling from stdin
        #TEST poller = select.poll()
        #TEST poller.register(sys.stdin, select.POLLIN)

        try:
            while tlx.run:
                # wait till character from stdin or timeout
                #TEST events = poller.poll(50)
                #TEST print(events)
                readables, writables, exceptionals = select.select([sys.stdin, tlx], [], [], 0.5)

                for readable in readables:
                    a = readable.read(1)
                    if a:
                        #print('a', a, type(a))   #debug
                        #print(ord(a))   #debug
                        if readable == tlx:   # from teletype
                            print(a, end='')
                        else:   # from user
                            a = a.lower()
                            a = REPLACE.get(a, a)
                            print(a, end='')
                            tlx.write(a)

        except KeyboardInterrupt :
            pass

        tlx.power(False)

    print('\r\n<EXIT>')

###############################################################################

if __name__ == "__main__":
    run()

# helper class to use command "utx" in repl
# >>>from term import *
# >>>utx
# >>>utx('myconfig.json')
class UTX:
    def __repr__(self):
        return run()

    def __call__(self, cnfName:str=None):
        return run(cnfName)

utx = UTX()
