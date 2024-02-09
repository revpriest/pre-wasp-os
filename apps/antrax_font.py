""" Antrax font
~~~~~~~~~~~~~

A font for monolith face

.. figure:: res/screenshots/AntraxFontApp.png
    :width: 179
"""
import wasp

# https://www.dafont.com/antraxja-goth-1938.font

ANTRAXFONT_DIGITS = (
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_0.png, 143 bytes
(
    45, 45,
    b'm\x08#\x0c \x0e\x1e\x10\x1c\x12\x1a\x13\x19\x15\x18\x06'
    b'\x01\x0f\x16\x04\x07\x0c\x15\x04\n\x0b\x14\x03\x0c\x0b\x12\x04'
    b'\r\n\x12\x03\x0f\t\x12\x03\x0f\n\x10\x04\x10\t\x10\x04'
    b'\x11\x08\x10\x04\x11\x08\x0f\x05\x12\x08\x0e\x05\x12\x08\x0e\x05'
    b'\x12\x08\x0e\x06\x12\x07\x0e\x06\x12\x07\x0e\x06\x12\x07\x0e\x07'
    b'\x12\x06\x0e\x07\x12\x05\x0f\x08\x11\x05\x0f\x08\x11\x05\x10\x08'
    b'\x10\x05\x10\t\x0f\x04\x11\t\x0f\x04\x12\t\r\x05\x12\n'
    b'\x0c\x04\x13\x0b\n\x04\x15\x0b\t\x04\x16\x0b\x06\x05\x17\x16'
    b'\x18\x14\x1a\x12\x1c\x10\x1e\x0e \x0c#\t&\x05\x14'
),
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_1.png, 89 bytes
(
    45, 45,
    b'E\x01+\x03)\x04(\x06&\x07%\x08#\n"\x0b'
    b'"\x0b&\x07&\x07&\x07&\x07&\x07&\x07&\x07'
    b'&\x07&\x07&\x07&\x07&\x07&\x07&\x07&\x07'
    b'&\x07&\x07&\x07&\x07&\x07&\x07&\x07&\x07'
    b'&\x07&\x07&\x07&\x07&\x08%\x08%\x08%\x05'
    b"'\x04)\x03)\x03*\x02\x19"
),
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_2.png, 113 bytes
(
    45, 45,
    b"A\x03'\t#\x0b!\r\x1f\x0f\x1e\x10\x1c\x11\x1c\x12"
    b'\x1a\x13\x1a\x06\x05\x08\x1a\x05\x07\x08\x19\x04\t\x07\x19\x03'
    b"\x0b\x06\x18\x03\x0c\x06\x19\x01\r\x06'\x06'\x06'\x05"
    b'(\x05(\x05(\x04(\x05(\x04(\x05(\x04(\x04'
    b'(\x05(\x04(\x04(\x04)\x04(\x04\x0c\x01\x1b\x05'
    b'\x0b\x02\x1a\t\x07\x03\x1a\x0c\x03\x03\x1a\x13\x19\x14\x18\x14'
    b'\x19\x13\x19\x14\x19\x05\x04\n\x1a\x02\t\x07(\x04+\x01'
    b'\x10'
),
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_3.png, 121 bytes
(
    45, 45,
    b"C\x04'\t#\x0b!\r\x1f\x0f\x1d\x11\x1c\x11\x1b\x05"
    b"\x03\x0b\x1a\x03\x07\t\x1a\x02\t\x08\x1a\x02\n\x07'\x06"
    b"'\x05(\x05(\x04)\x04)\x04(\x06&\x08%\t"
    b'"\x0c \x0e\x1f\x0e\x1f\x0e%\t%\x08&\x07&\x07'
    b'\x11\x07\x0f\x06\x11\x07\x0f\x06\x11\x07\x0f\x05\x12\x07\x0f\x05'
    b'\x12\x07\x0f\x05\x12\x07\x0f\x05\x13\x06\x0e\x05\x14\x06\x0e\x04'
    b'\x15\x07\x0c\x05\x16\x07\n\x05\x18\x07\x08\x05\x19\t\x04\x06'
    b'\x1b\x11\x1d\x0e!\n%\x06\x14'
),
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_4.png, 133 bytes
(
    45, 45,
    b'p\x01\x07\x01#\x02\x05\x03!\x04\x04\x04 \x05\x03\x05'
    b'\x1f\x05\x03\x06\x1e\x06\x03\x06\x1e\x06\x03\x06\x1d\x07\x03\x06'
    b'\x1d\x06\x04\x06\x1d\x06\x04\x06\x1d\x06\x04\x06\x1d\x05\x05\x06'
    b'\x1d\x05\x05\x06\x1c\x06\x05\x06\x1c\x05\x06\x06\x1c\x05\x06\x06'
    b'\x1c\x04\x07\x06\x1b\x05\x07\x06\x1b\x04\x08\x06\x1b\x04\x08\x06'
    b'\x1a\x04\t\x06\x1a\x03\t\x07\x1a\x13\x01\x02\x16\x18\x15\x18'
    b"\x14\x18\x15\x18\x15\x18\x14\x18\x15\x18%\x06'\x06'\x06"
    b"'\x06'\x06'\x06'\x06&\x08%\x08$\x05(\x04"
    b'(\x04*\x01\x15'
),
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_5.png, 117 bytes
(
    45, 45,
    b'j\x03\x0b\x03\x1b\x05\x08\x05\x1b\x12\x1b\x11\x1c\x10\x1d\x0f'
    b'\x1e\r \x0b"\x07&\x04)\x04\x03\x06 \x10\x1d\x11'
    b'\x1c\x12\x1b\x13\x1a\x14\x19\x14\x19\x15\x18\x05\x06\n\x18\x03'
    b"\n\t%\x08&\x07'\x06'\x06(\x05(\x05(\x05"
    b'(\x05(\x05\x12\x02\x14\x05\x11\x08\x0f\x04\x12\x08\x0e\x05'
    b'\x12\x07\x0f\x04\x13\x07\x0e\x05\x13\x08\r\x04\x15\x07\x0c\x04'
    b'\x16\x08\n\x04\x18\x08\x08\x04\x1a\t\x03\x06\x1c\x0f\x1f\r'
    b'"\x08(\x03\x17'
),
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_6.png, 159 bytes
(
    45, 45,
    b'o\x08#\x0b!\x0e\x1e\x10\x1c\x10\x1c\x05\x05\x07\x1c\x04'
    b'\x08\x04\x1c\x04\n\x02\x1c\x04\x0c\x01\x1c\x04(\x04)\x04'
    b'\n\x01\x1e\x03\x08\x07\x1a\x04\x07\n\x18\x04\x06\x0c\x17\x04'
    b'\x05\r\x16\x05\x05\x0e\x15\x05\x04\x0f\x15\x05\x04\x10\x14\x05'
    b'\x04\x06\x02\x08\x14\x05\x03\x06\x06\x05\x14\x05\x03\x05\x08\x05'
    b'\x13\x05\x03\x05\x08\x05\x13\x05\x04\x03\n\x04\x13\x06\x03\x04'
    b'\n\x03\x13\x06\x04\x03\n\x03\x13\x06\x04\x04\t\x03\x13\x07'
    b'\x04\x02\n\x03\x13\x08\x0f\x03\x14\x07\x0e\x04\x14\x08\r\x03'
    b'\x15\t\x0b\x04\x15\n\t\x05\x16\x0b\x06\x05\x17\x16\x18\x14'
    b'\x19\x13\x1b\x12\x1c\x10\x1e\r!\x0b$\x07(\x03\x15'
),
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_7.png, 101 bytes
(
    45, 45,
    b'k\x06\r\x02\x17\t\t\x04\x16\x0c\x06\x05\x15\x18\x14\x18'
    b'\x15\x17\x15\x18\x15\x04\x02\x11\x16\x03\x05\x0f\x16\x02\x08\x0c'
    b'\x17\x01\x0b\t)\x04(\x04(\x04)\x04(\x04(\x05'
    b"'\x05(\x04(\x05'\x05(\x05'\x05(\x05'\x05"
    b"(\x05'\x06'\x05'\x06'\x06'\x06'\x05'\x06"
    b"'\x07&\x07&\x08%\n$\n#\n$\t$\x08"
    b"'\x05*\x01\x15"
),
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_8.png, 141 bytes
(
    45, 45,
    b'm\n"\x0c\x1f\x10\x1c\x12\x1b\x04\x05\n\x19\x04\x08\t'
    b'\x18\x04\n\x07\x17\x05\x0b\x07\x16\x05\x0c\x06\x16\x06\x0b\x06'
    b'\x16\x08\n\x05\x16\t\t\x04\x17\x0b\x07\x04\x17\r\x04\x04'
    b'\x19\x13\x1a\x12\x1c\x10\x1d\x11\x1b\x13\x19\x04\x02\x0f\x17\x04'
    b'\x05\x0e\x15\x04\x08\r\x14\x04\t\r\x12\x04\x0c\x0b\x12\x04'
    b'\r\x0b\x10\x06\x0e\t\x10\x06\x0f\x08\x10\x06\x0f\x08\x10\x07'
    b'\x0f\x07\x10\x08\x0f\x06\x10\x08\x0f\x06\x11\x08\x0e\x05\x12\t'
    b'\r\x05\x13\n\x0b\x04\x14\x0b\t\x05\x15\x0c\x06\x05\x17\x15'
    b'\x18\x14\x1a\x12\x1d\x0f\x1f\r"\x08\'\x03\x15'
),
# 1-bit RLE, 45x45, generated from res/antraxfont/antrax_9.png, 179 bytes
(
    45, 45,
    b'm\n!\r\x1f\x0f\x1d\x05\x06\x06\x1b\x05\x08\x06\x1a\x04'
    b'\n\x06\x18\x04\x0b\x06\x17\x05\x0c\x06\x16\x05\x0c\x07\x14\x06'
    b'\r\x06\x14\x06\r\x06\x14\x06\r\x07\x12\x07\r\x07\x12\x07'
    b'\r\x07\x12\x07\r\x08\x11\x07\x08\x01\x04\x08\x11\x07\x08\x02'
    b'\x03\x08\x11\x07\x08\x03\x02\x08\x11\x07\x08\x03\x02\x08\x11\x08'
    b'\x08\x03\x01\x08\x11\x08\x08\x03\x01\x08\x11\x08\x08\x03\x01\x08'
    b'\x12\x08\x07\x03\x01\x08\x12\t\x05\x04\x01\x08\x12\n\x03\x04'
    b'\x02\x08\x12\x11\x02\x07\x14\x10\x02\x07\x15\x0e\x03\x07\x15\r'
    b'\x04\x06\x17\x0b\x05\x06\x18\t\x06\x05\x1a\x07\x06\x06\x15\x04'
    b'\x0e\x05\x14\x07\r\x04\x15\x07\x0c\x05\x16\x07\n\x05\x17\x07'
    b'\n\x04\x19\x07\x08\x04\x1b\x07\x05\x05\x1d\x0f\x1f\r!\n'
    b'&\x05\x16'
),
# 1-bit RLE, 5x45, generated from res/antraxfont/antrax_colon.png, 17 bytes
(
    5, 45,
    b'G\x03\x01\x1d\x01\x04\x02\x02C\x04\x01\x18\x01\x03\x02\x03'
    b'\x07'
)

)


class AntraxFontApp():
    """ Antrax font """
    NAME = "Antrax"
    ICON = ANTRAXFONT_DIGITS[6]

    def __init__(self):
        if(not hasattr(wasp,"fonts")): 
            wasp.fonts = {}
        wasp.fonts['Antrax'] = (6,ANTRAXFONT_DIGITS)   #ID:5. Please use random > 100 for user-fonts
        pass

    def unregister(self):
        del(wasp.fonts['Antrax'])

    def foreground(self):
        self._draw()


    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        draw.blit(ANTRAXFONT_DIGITS[0],    0,  60)
        draw.blit(ANTRAXFONT_DIGITS[1],   45,  60)
        draw.blit(ANTRAXFONT_DIGITS[2],   90,  60)
        draw.blit(ANTRAXFONT_DIGITS[3],  135,  60)
        draw.blit(ANTRAXFONT_DIGITS[4],  180,  60)
        draw.blit(ANTRAXFONT_DIGITS[5],    0, 125)
        draw.blit(ANTRAXFONT_DIGITS[6],   45, 125)
        draw.blit(ANTRAXFONT_DIGITS[7],   90, 125)
        draw.blit(ANTRAXFONT_DIGITS[8],  135, 125)
        draw.blit(ANTRAXFONT_DIGITS[9],  180, 125)

