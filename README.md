<img src="https://raw.githubusercontent.com/wiki/fablab-wue/piTelex/img/Header.JPG" width="1024px">

<img src="https://raw.githubusercontent.com/wiki/fablab-wue/MicroTelex/img/MicroTelexLogo80.png" width="80px" align="right">

# ➎➍➌•➋➊ *MicroTelex*

Control a historic teletype device (Telex) with a ESP8266 or __ESP32__ in __MicroPython__

Most hardware examples from project [piTelex](https://github.com/fablab-wue/piTelex) also works with this software on an ESP board.
The software is rewritten in a simpler way to support the ESP MicroPython environment.

> _*STATUS: STILL IN BETA PHASE WITH WORKING PROTOTYPES*_

### Features

* ESP8266 and __ESP32__ in __MicroPython__
* Software UART for __50__, 75, 100 and 45.45 __baud__ and 5 data-bits
* Baudot-Murray-Code (__CCITT-2__ = ITA2, TTY-US, MKT2) encoder and decoder
* Handles __pulse dialing__ (number switch) and key dialing
* Current-Loop up/down detection (AT/ST) given by __FSG__
* Full __TW39__ support
* Example programs for __USB-serial__ and __Telnet__ (at work now) communication
* (Preparation for CloudTelex)

### For detaileddescription see the [wiki pages](https://github.com/fablab-wue/MicroTelex/wiki)
