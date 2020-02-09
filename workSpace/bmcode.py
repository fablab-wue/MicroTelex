#!python3
"""
Telex Code Conversion
Baudot-Code = CCITT-1
Baudot-Murray-Code = CCITT-2

CCITT-2:
543.21      LTRS    FIGS
======      ==========================
000.00      undef   undef -> ~
000.01      E       3
000.10      <LF>    <LF>
000.11      A       -
001.00      <SPACE> <SPACE>
001.01      S       '
001.10      I       8
001.11      U       7
010.00      <CR>    <CR>
010.01      D       WRU? -> @
010.10      R       4
010.11      J       BELL <BEL> -> %
011.00      N       ,
011.01      F       undef, $, Ä, %
011.10      C       :
011.11      K       (
100.00      T       5
100.01      Z       +
100.10      L       )
100.11      W       2
101.00      H       undef, #, Ü, Pound
101.01      Y       6
101.10      P       0
101.11      Q       1
110.00      O       9
110.01      B       ?
110.10      G       undef, &, Ö, @
110.11      FIGS    FIGS -> ]
111.00      M       .
111.01      X       /
111.10      V       =
111.11      LTRS    LTRS -> [
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

###############################################################################


class BaudotMurrayCode:
    'Converter for Baudot-Murray-code'
    # Baudot-Murray-Code to ASCII table
    _LUT_BM2A_STD = [
        "~E\nA SIU\rDRJNFCKTZLWHYPQOBG]MXV[", 
        "~3\n- '87\r@4%,~:(5+)2~6019?~]./=["
    ]
    _LUT_BM2A_US = [
        "~E\nA SIU\rDRJNFCKTZLWHYPQOBG]MXV[", 
        "~3\n- %87\r$4',!:(5\")2@6019?&]./;["
    ]
    # Baudot-Murray-Code mode switch codes
    _LUT_BMsw = [0x1F, 0x1B]

    # Baudot-Murray-Code valid ASCII table
    # _valid_char = " ABCDEFGHIJKLMNOPQRSTUVWXYZ~3\n- '87\r@4%,~:(5+)2~6019?~]./=[#"
    _valid_convert_chars = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+=:/()?.,'\n\r"
    _LUT_convert_chars = {
        'Ä': 'AE',
        'Ö': 'OE',
        'Ü': 'UE',
        'ß': 'SS',
        '\a': '%',  # Bell
        '\f': '(FF)',  # Form Feed
        '\d': '(DEL)',  # Delete
        '\t': '(TAB)',  # Tab
        '\v': '(VT)',  # Vertical Tab
        '\x1B': '(ESC)',  # Escape
        '\b': '(BS)',  # Backspace
        '\x08': '(BS)',  # Backspace
        '&': '(AND)',
        '€': '(EUR)',
        '$': '(USD)',
        '<': '(LT)',
        '>': '(GT)',
        '|': '(PIPE)',
        '*': '(STAR)',
        '#': '(HASH)',
        '@': '(AT)',
        '"': "'",
        ';': ',.',
        '!': '(./)',
        '%': '(./.)',
        '[': '(',
        ']': ')',
        '{': '-(',
        '}': ')-',
        '\\': '/',
        '_': '--',
    }

    # =====
    
    @staticmethod
    def ascii_to_tty_text(text: str) -> str:
        ret = ''

        text = text.upper()

        for a in text:
            try:
                if a not in BaudotMurrayCode._valid_convert_chars:
                    if a in BaudotMurrayCode._LUT_convert_chars:
                        a = BaudotMurrayCode._LUT_convert_chars.get(a, '?')
                    else:
                        #nkfd_norm = unicodedata.normalize('NFKD', a)
                        #a =  u"".join([c for c in nkfd_norm if not unicodedata.combining(c)])
                        if a not in BaudotMurrayCode._valid_convert_chars:
                            a = '?'
                ret += a
            except:
                pass

        return ret

    # -----

    @staticmethod
    def do_flip_bits(val: int) -> int:
        ret = 0

        if val & 1:
            ret |= 16
        if val & 2:
            ret |= 8
        if val & 4:
            ret |= 4
        if val & 8:
            ret |= 2
        if val & 16:
            ret |= 1

        return ret

    # =====

    def __init__(self, coding=False, flip_bits=False):
        self._ModeBM = None  # 0=LTRS 1=FIGS
        self._flip_bits = flip_bits
        self._show_all_BuZi = True
        if coding == 'US':
            self._LUT_BM2A = self._LUT_BM2A_US
        else:
            self._LUT_BM2A = self._LUT_BM2A_STD

    # -----

    def reset(self):
        self._ModeBM = None  # 0=LTRS 1=FIGS

    # -----

    def encodeA2BM(self, ascii: str) -> list:
        'convert an ASCII string to a list of baudot-murray-coded bytes'
        ret = []

        ascii = ascii.upper()

        if self._ModeBM is None:
            self._ModeBM = 0  # letters
            ret.append(self._LUT_BMsw[self._ModeBM])

        for a in ascii:
            try:  # symbol in current layer?
                b = self._LUT_BM2A[self._ModeBM].index(a)
                if b in self._LUT_BMsw:  # explicit Bu or Zi
                    self._ModeBM = self._LUT_BMsw.index(b)
                ret.append(b)
            except:
                try:  # symbol in other layer?
                    b = self._LUT_BM2A[1 - self._ModeBM].index(a)
                    self._ModeBM = 1 - self._ModeBM
                    ret.append(self._LUT_BMsw[self._ModeBM])
                    ret.append(b)
                except:  # symbol not found -> ignore
                    pass

        if ret and self._flip_bits:
            for i, b in enumerate(ret):
                ret[i] = self.do_flip_bits(b)

        return ret

    # -----

    def decodeBM2A(self, code: list) -> str:
        'convert a list/bytearray of baudot-murray-coded bytes to an ASCII string'
        ret = ''

        for b in code:
            if self._flip_bits:
                b = self.do_flip_bits(b)

            try:
                if b in self._LUT_BMsw:
                    mode = self._LUT_BMsw.index(b)
                    if self._ModeBM != mode:
                        self._ModeBM = mode
                        if not self._show_all_BuZi:
                            continue

                if self._ModeBM is None:
                    self._ModeBM = 0  # letters

                if b >= 32:
                    a = '{' + hex(b)[2:] + '}'
                else:
                    a = self._LUT_BM2A[self._ModeBM][b]
                ret += a
            except:
                ret += '{!}'  # debug
                pass

        return ret

###############################################################################
