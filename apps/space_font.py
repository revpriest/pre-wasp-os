""" Space font
~~~~~~~~~~~~~

A font for monolith face

.. figure:: res/screenshots/SpaceFontApp.png
    :width: 179
"""
import wasp

#https://www.dafont.com/spaceport-one.font - 100% free

SPACEFONT_DIGITS = (
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_0.png, 137 bytes
(
    45, 45,
    b'\t\x1d\x0e!\x0c"\n$\t$\t$\t$\t$'
    b'\t$\t$\t$\x08\x0c\r\x0c\x08\x0c\x0e\x0b\x08\x0b'
    b'\x0e\x0b\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b'
    b'\x0e\x0b\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b'
    b'\x0e\x0b\t\x0b\x0e\x0b\t\x0b\x0e\x0b\x08\x0c\x0e\x0b\x08\x0b'
    b'\x0f\n\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b'
    b'\x0e\x0b\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b'
    b'\x0e\x0b\t$\x08%\x08%\x08%\x08$\t$\t$'
    b'\t$\n#\x0b!\r\x1f\x08'
),
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_1.png, 91 bytes
(
    45, 45,
    b'\x0f\x0c!\x0e\x1f\x0f\x1e\x10\x1d\x10\x1d\x10\x1d\x10\x1c\x11'
    b'\x1c\x10\x1d\x10\x1d\x10"\x0b"\x0b"\x0b"\x0b"\x0b'
    b'"\x0b"\x0b!\x0b"\x0b"\x0b"\x0b"\x0b"\x0b'
    b'"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b!\x0c!\x0b'
    b'"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b'
    b'!\x0c!\x0c!\x0b"\x0b"\x0b\x12'
),
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_2.png, 101 bytes
(
    45, 45,
    b'\n\x1d\x0e!\x0b#\t$\t%\x08%\x08%\x08%'
    b'\x08$\t$\t$\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b'
    b'\x0e\x0b\x08\x0b\r\r\x08\x0b\x0b\x0f\x1b\x12\x19\x13\x18\x15'
    b'\x16\x16\x15\x17\x14\x17\x14\x17\x14\x17\x14\x17\x14\x17\x15\x15'
    b'\x18\x13\x19\x12\x1b\x10\x1d\x0e\x1f\x0c!\x0b"\x0b"$'
    b'\t$\t$\x08%\x08%\x08%\x08%\x08%\x08%'
    b'\x08%\x08$\x06'
),
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_3.png, 115 bytes
(
    45, 45,
    b'\t\x1d\x0e!\x0b#\n#\t%\x08%\x08%\x08%'
    b'\x08%\x08$\t$\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t\x0b'
    b'\x0e\x0b\t\x0b\x0c\r\t\x0b\n\x0f\x1b\x12\x19\x13\x18\x15'
    b'\x18\x14\x19\x13\x1a\x11\x1c\x0f\x1e\x0e\x1f\x0f\x1e\x11\x1d\x12'
    b'\x0b\n\x08\x10\x0b\x0b\x08\x10\n\x0b\n\x0f\t\x0b\x0c\r'
    b'\t\x0b\r\x0c\t\x0b\x0e\x0b\t\x0b\x0e\x0b\t$\t$'
    b'\t$\t$\t#\n#\n#\n#\n#\x0b!'
    b'\x0e\x1e\x08'
),
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_4.png, 129 bytes
(
    45, 45,
    b'\x06\n\r\n\x0b\x0b\r\x0b\n\x0b\r\x0b\n\x0b\r\x0b'
    b'\n\x0b\x0c\x0c\n\x0b\x0c\x0c\n\x0b\x0c\x0b\x0b\x0b\x0c\x0b'
    b'\x0b\x0b\x0c\x0b\n\x0b\r\x0b\n\x0b\r\x0b\n\x0b\r\x0b'
    b'\n\x0b\r\x0b\n\x0b\r\x0b\n\x0b\r\x0b\n\x0b\r\x0b'
    b'\n\x0b\x0c\x0c\n\x0b\x0c\x0c\n\x0b\x0c\x0b\x0b&\x07&'
    b"\x07&\x06'\x06'\x06'\x06'\x06&\x08%\t$"
    b'\n#\x1e\x0c!\x0c!\x0b"\x0b"\x0b"\x0b"\x0b'
    b'"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"\n'
    b'\t'
),
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_5.png, 105 bytes
(
    45, 45,
    b'\x07#\t$\t$\t$\t$\t$\t$\t$'
    b'\t$\t$\x08%\x08\x0b"\x0b"\x0c!\r \x0f'
    b'\x1f\x10\x1d\x11\x1d\x12\x1c\x13\x1c\x12\x1c\x13\x1c\x13\x1c\x13'
    b'\x1c\x12\x1c\x13\x1c\x12\x0c\t\x08\x11\n\x0b\x08\x11\t\x0b'
    b'\n\x0f\t\x0b\x0c\r\t\x0b\r\x0c\t\x0b\x0e\x0b\t\x0b'
    b'\x0e\x0b\t$\t$\t$\t$\t$\t$\t$'
    b'\t#\n#\x0b!\x0e\x1e\x08'
),
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_6.png, 109 bytes
(
    45, 45,
    b'\t!\n#\n#\t$\t$\t$\t$\t$'
    b'\t$\t$\x08%\x08\x0c!\x0c!\x0c!\r \x0f'
    b'\x1e\x11\x1c\x12\x1b\x14\x19\x16\x17\x17\x16\x19\x14\x1b\x12\x1c'
    b'\x11\x1e\x0e\x0b\x03\x13\x0c\x0b\x05\x12\x0b\x0b\x07\x11\n\x0b'
    b'\x08\x10\n\x0b\n\x0f\t\x0b\x0c\r\t\x0b\r\x0c\t\x0b'
    b'\x0e\x0b\t\x0c\r\x0b\t$\t$\t$\t$\x08%'
    b'\x08%\x08%\t$\t#\x0b"\r\x1e\x08'
),
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_7.png, 91 bytes
(
    45, 45,
    b'\x06\x1d\x10\x1f\x0e \r!\x0c!\x0b"\x0b"\x0b"'
    b'\x0b!\x0c!\x0c!\x1f\r \r \x0c \r \x0c'
    b' \r \r \x0c \r \x0c \r \x0c \r'
    b' \r \x0c \r \x0c \r \r\x1f\r \r'
    b' \x0c \r \x0c \r \r \x0c \r \x0c'
    b' \r \x0c \r \r \x0c\x16'
),
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_8.png, 115 bytes
(
    45, 45,
    b'\t\x1e\r"\n#\n$\t$\t$\t$\t$'
    b'\t$\x08%\x08%\x08\x0b\x0f\x0b\x08\x0b\x0f\x0b\x08\x0c'
    b'\r\x0c\x08\r\n\x0e\x08\x0f\x06\x0f\n\x0f\x03\x11\n#'
    b'\x0b!\r \x0f\x1c\x13\x19\x14\x17\x14\x17\x13\x1c\x10\x1f'
    b'\r!\x0c"\n\x12\x01\x11\t\x10\x05\x0f\t\x0e\t\r'
    b'\t\x0c\x0c\x0c\t\n\x0f\x0b\t\n\x0f\x0b\x08%\x08%'
    b'\x08%\x08%\x08%\x08%\x08$\t$\n#\x0b!'
    b'\r\x1f\x08'
),
# 1-bit RLE, 45x45, generated from res/spaceportfont/spacefont_9.png, 123 bytes
(
    45, 45,
    b'\t\x1d\x0e!\x0b#\n#\n$\t$\x08%\x08$'
    b'\t$\t$\t$\t\x0c\r\x0b\t\x0b\x0e\x0b\t\x0c'
    b'\r\x0b\t\r\x0c\x0b\t\x0f\n\x0b\t\x10\t\x0b\n\x11'
    b'\x07\x0b\x0b\x12\x05\x0b\x0c\x12\x04\x0b\r\x13\x01\x0b\x10\x1d'
    b'\x12\x1b\x13\x1a\x15\x18\x17\x16\x18\x15\x1a\x13\t\n\t\x11'
    b'\t\x0b\t\x10\t\x0b\x0b\x0e\x08\x0c\r\x0c\x08\x0c\r\x0c'
    b'\x08\x0c\r\x0b\t$\t$\t$\t$\t$\t$'
    b'\t$\t$\n"\x0b"\r\x1e\t'
),
# 1-bit RLE, 5x45, generated from res/spaceportfont/spacefont_colon.png, 45 bytes
(
    5, 45,
    b'\x1f\x03\x02\x03\x02\x03\x02\x03\x02\x03\x02\x03\x02\x03\x02\x03'
    b'\x02\x03\x02\x03\x02\x03M\x03\x02\x03\x02\x03\x02\x03\x02\x03'
    b'\x02\x03\x02\x03\x02\x03\x02\x03\x02\x03\x02\x03\x0b'
)
)



class SpaceFontApp():
    NAME = "Space"
    ICON = SPACEFONT_DIGITS[2]

    def __init__(self):
        if(not hasattr(wasp,"fonts")): 
            wasp.fonts = {}
        wasp.fonts['Space'] = (1,SPACEFONT_DIGITS)   #ID:1. Please use random > 100 for user-fonts
        pass

    def unregister(self):
        del(wasp.fonts['Space'])

    def foreground(self):
        self._draw()


    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        draw.blit(SPACEFONT_DIGITS[0],    0,  60)
        draw.blit(SPACEFONT_DIGITS[1],   45,  60)
        draw.blit(SPACEFONT_DIGITS[2],   90,  60)
        draw.blit(SPACEFONT_DIGITS[3],  135,  60)
        draw.blit(SPACEFONT_DIGITS[4],  180,  60)
        draw.blit(SPACEFONT_DIGITS[5],    0, 125)
        draw.blit(SPACEFONT_DIGITS[6],   45, 125)
        draw.blit(SPACEFONT_DIGITS[7],   90, 125)
        draw.blit(SPACEFONT_DIGITS[8],  135, 125)
        draw.blit(SPACEFONT_DIGITS[9],  180, 125)

