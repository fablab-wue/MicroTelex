#!python3
"""
"""
__author__ = "Jochen Krapf"
__email__ = "jk@nerd2nerd.org"
__copyright__ = "Copyright 2020, JK"
__license__ = "GPL3"
__version__ = "0.0.1"


import uos
import select
import sys
import json

import tty
import telex


def run():
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

    with open('telex.json', 'r') as f:
        cnf = json.load(f)
    print('Config:          ', cnf)
    print('')

    with telex.Telex(
        cnf['BAUD'], 
        cnf['PIN']['TX'], cnf['PIN']['RX'], 
        cnf['PIN']['RLY'], 
        cnf['PIN']['LED']
        ) as t:
        # t = tty.TTY(2, 0, 4, 5)   # ESP8266
        # t = tty.TTY(2, 4, 16, 17)   # ESP32

        # polling from stdin
        poller = select.poll()
        poller.register(sys.stdin, select.POLLIN)

        while t.run:
            # wait till character from stdin or timeout
            events = poller.poll(50)
            #events, x, y = select.select([sys.stdin], [], [], 1.0)
            # print(events)

            for file in events:
                ch = file[0].read(1)
                #print('ch', ch)
                #print(ord(ch))
                t.write(ch)

            if t.any():
                ch = t.read()
                print(ch, end='')

        pass


if __name__ == "__main__":
    run()


