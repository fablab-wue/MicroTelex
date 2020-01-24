# MicroTelex

Control a historic teletype device (Telex) with a ESP8266 or ESP32 in MicroPython

This project is based on the Telex project <https://github.com/fablab-wue/piTelex>. Most hardware eamples also works with this software.
The software is rewritten in a simpler way to support the ESP MicroPython environment.

*STILL IN BETA PHASE*

### Features

* Software TTY for 50, 75, 100 and 45.45 baud
* Baudot Murray encoder and decoder
* Pulse dialing (number switch) decoder
* Line up/down detection (AT/ST)
* Full TW39 support
* Test programs for USB and Telnet communication
* (Preparation for CloudTelex)

### Installation

1) Download the MicroPython firmware from <http://micropython.org/download> dependent on ESP type

2) Flash firmware to ESP as descriped in the link above

3) Start a tool which supports download Python files to ESP like <https://github.com/DFRobot/uPyCraft> or <https://github.com/wendlers/mpfshell>

4) Download all Python (\*.py) and Json (\*.json) files from folder "workSpace" to ESP

5) Optional: Establish WLAN connection to use WebREPL and/or Telnet. Use e.g. <https://github.com/tzapu/WiFiManager>

6) To use the USB connection import module "usb" and start it with

        import usb
        usb.run()

    This exampe code gets inputs from stdin (keyboard), convert it to baudot-murray-code and send it to software TTY. All inputs to software TTY are converted to ASCII and put to stdout (screen).

### Modules

##### main

Example to start WIFI connection.

##### tty

Software TTY based on timer interrupt for low baud rates.
Support line observation and pulse dial decoding.

##### bmcode

Converter between Baudot-Murray-Code and ASCII.

##### telex

Handles TTY data and Baudot-Murray conversion.

##### usb

This exampe code gets inputs from stdin (keyboard), convert it to baudot-murray-code and send it to software TTY. All inputs to software TTY are converted to ASCII and put to stdout (screen).

##### telnet (at work)

This exampe code gets inputs from socket, convert it to baudot-murray-code and send it to software TTY. All inputs to software TTY are converted to ASCII and put back to socket.

##### debug_pc.machine / test_pc

Mock up to test and debug machine behavior on a PC with CPython

### Configuration

All configuration of the Telex state machine is placed in a Json file (telex.json).

Note that the rules for Json must be used strictly.

##### ESP Pins

The ESP pins can be assigned by their GPIO number (not board number):

        "PIN": {
            "TX": 2,
            "RX": 0,
            "RLY": 4,
            "LED": 5,
            "SW": 6
            },

Example ESP8266 Pinout on Board 'Wemos D1 mini (pro)':

    TX      D3  GPIO 0 (with pullup, boot, board Button)
    RX      D2  GPIO 4
    Relay   D1  GPIO 5 (high active)
    LED     D4  GPIO 2 (low active, board LED to Vcc)
    Free    D0, D5...D8, A0

Example ESP32 Pinout on Board 'NodeMCU-32S':

    TX      GPIO 0 (with pullup, boot, board Button)
    RX      GPIO 5
    Relay   GPIO 4 (high active)
    LED     GPIO 2 (high active, board LED to GND)
    Free    GPIO (9...10), 12...19, 21...27, 32...35, (36, 39)
    NotUse  GPIO 1, 3, 6..8, (9...10), 11, (36, 39)
    () = depends on board

##### Baud Rate

The baud rate for the software TTY (to Telex machine) can be set with:

        "BAUD": 50,

All baud rates below 100 can be used - also float value like 45.45 baud. The precision is limited by the timer raster of 1 ms. Typical values: 50, 75, 100 and 45.45 baud

##### ...


TODO more description...