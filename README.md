# MicroTelex

Control a historic teletype device (Telex) with a ESP8266 or ESP32 in MicroPython

This project is based on the Telex project <https://github.com/fablab-wue/piTelex>. Most hardware eamples also works with this software.
The software is rewritten in a simpler way to support the ESP MicroPython environment.

## Installation

1) Download the MicroPython firmware from <http://micropython.org/download> dependent on ESP type

2) Flash firmware to ESP as descriped in the link above

3) Start a tool which supports download Python files to ESP like <https://github.com/DFRobot/uPyCraft> or <https://github.com/wendlers/mpfshell>

4) Download all Python (\*.py) and Json (\*.json) files from folder "workSpace" to ESP

5) Optional: Establish WLAN connection to use WebREPL and/or Telnet. Use e.g. <https://github.com/tzapu/WiFiManager>

6) To use the USB connection import module "usb" and start it with

        import usb
        usb.run()

    This exampe code gets inputs from stdin (keyboard), convert it to baudot-murray-code and send it to software TTY. All inputs to software TTY are converted to ASCII and put to stdout (screen).
