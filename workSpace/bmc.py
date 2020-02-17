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


class BMC:
    'Converter for Baudot-Murray-code'
    # Baudot-Murray-Code to ASCII table
    _LUT_BM2A_ITA2 = (
        "~E\nA SIU\rDRJNFCKTZLWHYPQOBG]MXV[", 
        "~3\n- '87\r@4%,~:(5+)2~6019?~]./=["
    )
    _LUT_BM2A_US = (
        "~E\nA SIU\rDRJNFCKTZLWHYPQOBG]MXV[", 
        "~3\n- %87\r$4',!:(5\")2@6019?&]./;["
    )
    _LUT_BM2A_MKT2 = (
        "~E\nA SIU\rDRJNFCKTZLWHYPQOBG]MXV[", 
        "~3\n- '87\r@4Ю,Э:(5+)2Щ6019?Ш]./=[",
        "~Е\nА СИУ\rДРЙНФЦКТЗЛВХЫПЯОБГ]МЬЖ["
    )
    # Baudot-Murray-Code mode switch codes
    _LUT_BMsw_ITA2 = (0x1F, 0x1B)
    _LUT_BMsw_US = (0x1F, 0x1B)
    _LUT_BMsw_MKT2 = (0x1F, 0x1B, 0x00)

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
        '\t': '(TAB)',  # Tab
        '\v': '(VT)',  # Vertical Tab
        '\x1B': '(ESC)',  # Escape
        '\b': '(BS)',  # Backspace
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

    CODING_ITA2 = 0
    CODING_US = 1
    CODING_MKT2 = 2

    # =====
    
    @staticmethod
    def ascii_to_tty_text(text: str) -> str:
        ret = ''

        text = text.upper()

        for a in text:
            try:
                if a not in BMC._valid_convert_chars:
                    if a in BMC._LUT_convert_chars:
                        a = BMC._LUT_convert_chars.get(a, '?')
                    else:
                        #nkfd_norm = unicodedata.normalize('NFKD', a)
                        #a =  u"".join([c for c in nkfd_norm if not unicodedata.combining(c)])
                        if a not in BMC._valid_convert_chars:
                            a = '?'
                ret += a
            except:
                pass

        return ret

    # -----

    @staticmethod
    def do_flip_bits(code: bytes) -> bytes:
        ret = bytearray()

        for b in code:
            rb = 0
            if b & 1:
                rb |= 16
            if b & 2:
                rb |= 8
            if b & 4:
                rb |= 4
            if b & 8:
                rb |= 2
            if b & 16:
                rb |= 1
            ret.append(rb)

        return ret

    # =====

    def __init__(_, coding:int=0, flip_bits:bool=False, show_all_BuZi:bool=True):
        _._mode = None  # 0=LTRS 1=FIGS
        _._flip_bits = flip_bits
        _._show_all_BuZi = show_all_BuZi
        if coding == _.CODING_US:
            _._LUT_BM2A = _._LUT_BM2A_US
            _._LUT_BMsw = _._LUT_BMsw_US
        elif coding == _.CODING_MKT2:
            _._LUT_BM2A = _._LUT_BM2A_MKT2
            _._LUT_BMsw = _._LUT_BMsw_MKT2
        else:
            _._LUT_BM2A = _._LUT_BM2A_ITA2
            _._LUT_BMsw = _._LUT_BMsw_ITA2

    # -----

    def reset(_):
        _._mode = None  # 0=LTRS 1=FIGS

    # -----

    def encodeA2BM(_, ascii:str) -> bytes:
        'convert an ASCII string to a list of Baudot-Murray-coded bytearray'
        ret = bytearray()

        if not isinstance(ascii, str):
            ascii = str(ascii)

        ascii = ascii.upper()

        if _._mode is None:
            _._mode = 0  # letters
            ret.append(_._LUT_BMsw[_._mode])

        for a in ascii:
            try:  # symbol in current layer?
                b = _._LUT_BM2A[_._mode].index(a)
                ret.append(b)
                if b in _._LUT_BMsw:  # explicit Bu or Zi
                    _._mode = _._LUT_BMsw.index(b)
            except ValueError:
                try:  # symbol in other layer?
                    nm = _._mode + 1
                    if nm >= len(_._LUT_BM2A):
                        nm = 0
                    b = _._LUT_BM2A[nm].index(a)
                    ret.append(_._LUT_BMsw[nm])
                    ret.append(b)
                    _._mode = nm
                except ValueError:
                    try:  # symbol in other layer?
                        nm += 1
                        if nm >= len(_._LUT_BM2A):
                            nm = 0
                        b = _._LUT_BM2A[nm].index(a)
                        ret.append(_._LUT_BMsw[nm])
                        ret.append(b)
                        _._mode = nm
                    except:  # symbol not found -> ignore
                        pass
            except:  # unknown -> ignore
                pass

        if ret and _._flip_bits:
            ret = _.do_flip_bits(ret)

        return ret

    # -----

    def decodeBM2A(_, code:bytes) -> str:
        'convert a list/bytearray of Baudot-Murray-coded bytes to an ASCII string'
        ret = ''

        if _._flip_bits:
            code = _.do_flip_bits(code)

        for b in code:
            try:
                if b in _._LUT_BMsw:
                    mode = _._LUT_BMsw.index(b)
                    if _._mode != mode:
                        _._mode = mode
                    if not _._show_all_BuZi:
                        continue

                if _._mode is None:
                    _._mode = 0  # letters

                if b >= 0x20:
                    ret += '{' + hex(b)[2:] + '}'
                else:
                    ret += _._LUT_BM2A[_._mode][b]
            except:
                ret += '{!}'  # debug

        return ret

###############################################################################
