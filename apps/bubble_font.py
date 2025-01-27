""" Bubble font
~~~~~~~~~~~~~

A font for monolith face

.. figure:: res/screenshots/BubbleFontApp.png
    :width: 179
"""
import wasp

BUBBLEFONT_DIGITS = (
    # 1-bit RLE, 45x45, generated from res/bubblefont/bubblefont_0.png, 101 bytes
    (
        45, 45,
        b'\x99\x0b \x0e\x1e\x11\x1b\x13\x19\x15\x17\x17\x15\x18\x15\x19'
        b'\x13\x1a\x13\x1b\x11\x1c\x11\x1c\x11\x1d\x0f\x0e\x01\x0f\x0f\r'
        b'\x04\r\x0f\r\x04\r\x0f\r\x04\r\x0f\r\x04\x0e\x0e\x0c'
        b'\x06\r\r\r\x06\r\r\r\x06\r\r\x0e\x04\x0e\r\x0e'
        b'\x04\r\x0e\x0f\x02\x0e\x0f\x1e\x0f\x1e\x0f\x1e\x0f\x1e\x10\x1c'
        b'\x11\x1c\x12\x1b\x12\x1a\x14\x19\x15\x17\x17\x16\x18\x14\x1a\x12'
        b'\x1c\x0f \x0b\x97'
    ),
    # 1-bit rle, 45x45, generated from res/bubblefont/bubblefont_1.png, 97 bytes
    (
        45, 45,
        b"\x17\x03'\t \x0e\x1c\x12\x19\x14\x17\x16\x15\x18\x14\x1a"
        b'\x12\x1b\x11\x1c\x11\x1b\x11\x1c\x11\x1c\x11\x1c\x12\x1b\x12\x1b'
        b'\x12\x1b\x13\n\x02\r\x15\x08\x03\r\x16\x06\x04\r\x17\x03'
        b'\x06\r \r \r \r \r \r \r \r'
        b' \r\x1f\x0e\x15"\t%\x07\'\x05(\x05)\x04)'
        b"\x04)\x04)\x04)\x04)\x04)\x05'\x08#\x0e\x1a"
        b'7'
    ),
    # 1-bit rle, 45x45, generated from res/bubblefont/bubblefont_2.png, 97 bytes
    (
        45, 45,
        b"m\x01'\r\x1d\x13\x18\x16\x16\x19\x12\x1b\x11\x1d\x10\x1e"
        b'\x0e\x1f\x0e \r \r \r \x0e\x1f\x0e\x1f\x0f\n'
        b'\x04\x10\x10\x08\x06\x0f\x11\x06\x07\x0e\x13\x04\x08\x0e\x1e\x0f'
        b'\x1d\x0f\x1c\x10\x1c\x10\x1c\x10\x1b\x11\x1b\x10\x1b\x10\x1c\x10'
        b'\t\x03\x10\x11\x05\t\r!\x0b"\x0b#\t$\t$'
        b'\t%\t$\t$\n"\r \x0f\x1d\x13\x17\x1c\x0c'
        b':'
    ),
    # 1-bit rle, 45x45, generated from res/bubblefont/bubblefont_3.png, 99 bytes
    (
        45, 45,
        b'p\x02&\x0b \x10\x1a\x14\x18\x16\x16\x18\x14\x1a\x13\x1a'
        b'\x12\x1c\x11\x1c\x11\x1c\x12\x1b\x12\x1b\x13\x0b\x04\x0b\x13\t'
        b'\x05\x0b\x15\x06\x05\x0c\x18\x02\x05\r\x1e\x0e\x1e\x10\x1d\x11'
        b'\x1b\x13\x1a\x14\x1a\x14\x1b\x13\x13\x04\x08\x0e\x11\x07\t\x0c'
        b'\x10\t\x08\x0c\x10\n\x07\x0c\x0f\x0c\x05\r\x0f\x1e\x0f\x1e'
        b'\x0f\x1e\x10\x1c\x11\x1c\x12\x1a\x13\x19\x16\x16\x18\x14\x1c\x0f'
        b'"\x08\x98'
    ),
    # 2-bit RLE, 45x45, generated from res/bubblefont/clock_4.png, 102 bytes
    (
        b'\x02'
        b'--'
        b'?\x02\xc6%\xcb \xce\x1e\xd0\x1c\xd2\x1a\xd3\x19\xd5\x17'
        b'\xd6\x17\xd6\x16\xd7\x16\xd7\x15\xd8\x14\xd9\x14\xd9\x13\xcd\x01'
        b'\xcc\x13\xcb\x04\xcb\x12\xcc\x04\xcb\x12\xcb\x05\xcb\x12\xcb\x04'
        b'\xcc\x11\xcc\x04\xd2\x0b\xe4\x08\xe5\x08\xe6\x07\xe6\x07\xe6\x07'
        b'\xe6\x07\xe6\x07\xe6\x07\xe5\t\xe4\n\xe2\r\xc5\x08\xcd '
        b'\xce\x1f\xce\x1f\xcf\x1d\xd0\x1d\xd0\x1d\xd0\x1e\xce \xcb$'
        b'\xc6?W'
    ),
    # 1-bit rle, 45x45, generated from res/bubblefont/bubblefont_5.png, 93 bytes
    (
        45, 45,
        b'\x13\x06"\x10\x1a\x17\x14\x1c\x10\x1e\x0e\x1f\x0e\x1f\r '
        b'\r \r \r\x1f\x0e\x1f\x0e\x1e\x0f\x1d\x10\x0e\t\x04'
        b'\x13\x13\x1a\x19\x14\x1b\x12\x1d\x10\x1e\x10\x1e\x0f\x1f\x0e\x1f'
        b'\x0f\x1e\x10\x1e\x10\x1d\x11\x07\x05\x10\x1e\x0f\x10\x03\x0c\x0e'
        b'\x0f\x06\n\x0e\x0e\t\x06\x0f\x0e\x1f\x0e\x1f\r\x1f\x0e\x1f'
        b'\x0e\x1e\x0f\x1d\x11\x1c\x12\x19\x15\x16\x1b\x0f\xc4'
    ),
    # 1-bit rle, 45x45, generated from res/bubblefont/bubblefont_6.png, 93 bytes
    (
        45, 45,
        b'r\x03%\x0e\x1c\x13\x18\x16\x16\x18\x14\x19\x13\x1a\x12\x1b'
        b'\x12\x1b\x11\x1b\x12\x1b\x11\x0e\x07\x06\x12\r\n\x02\x14\x0c'
        b'!\x0c!\x0c\x03\x08\x15\x1a\x13\x1c\x11\x1c\x11\x1d\x10\x1e'
        b'\x0f\x1e\x0f\x1e\x0f\x1f\x0e\x1f\x0f\x1e\x0f\r\x05\x0c\x0f\r'
        b'\x05\x0c\x0f\r\x04\r\x10\x1c\x11\x1c\x11\x1c\x12\x1a\x14\x19'
        b'\x14\x18\x16\x16\x18\x14\x1b\x11\x1e\r#\x06\x9a'
    ),
    # 1-bit rle, 45x45, generated from res/bubblefont/bubblefont_7.png, 95 bytes
    (
        45, 45,
        b'\x14\x06 \x12\x17\x18\x13\x1c\x10\x1e\x0e \r!\x0b#'
        b'\n#\n$\t$\t$\t$\n#\n\x0e\x04\x12'
        b'\n\n\x08\x11\x0b\x07\n\x11\x1c\x11\x1c\x10\x1d\x10\x1d\x10'
        b'\x1c\x11\x1c\x11\x1b\x11\x1b\x12\x1b\x12\x1a\x13\x19\x13\x1a\x13'
        b'\x19\x14\x18\x14\x19\x14\x18\x14\x19\x14\x18\x14\x19\x14\x19\x13'
        b'\x1a\x13\x1b\x11\x1c\x11\x1d\x0f\x1f\r"\n&\x05>'
    ),
    # 1-bit rle, 45x45, generated from res/bubblefont/clock_8.png, 101 bytes
    (
        45, 45,
        b'>\x0b\x1d\x15\x16\x19\x13\x1b\x11\x1e\x0f\x1e\x0e \r '
        b'\r \r\x0e\x03\x0f\r\r\x05\x0e\r\r\x06\r\r\r'
        b'\x05\x0e\r\x0e\x03\x0e\x0f\x1d\x11\x1b\x13\x19\x16\x15\x1a\x13'
        b'\x18\x18\x13\x1b\x10\x1f\r!\x0b#\n#\t$\t\x10'
        b'\x06\x0e\t\x0f\x07\x0f\x07\x10\x07\x0e\x08\x11\x05\x0f\x08%'
        b'\x08%\t#\n#\n"\x0c \x0e\x1e\x10\x1c\x13\x18'
        b'\x17\x14\x1e\x0b\x98'
    ),
    # 1-bit rle, 45x45, generated from res/bubblefont/bubblefont_9.png, 91 bytes
    (
        45, 45,
        b'o\x02&\x0c\x1f\x10\x1c\x13\x19\x15\x17\x17\x15\x19\x13\x1b'
        b'\x12\x1b\x11\x1d\x10\x1d\x10\r\x03\r\x10\x0c\x05\x0c\x10\x0c'
        b'\x05\x0c\x10\r\x03\r\x10\x1d\x10\x1d\x10\x1d\x10\x1d\x11\x1c'
        b'\x11\x1c\x12\x1b\x13\x1a\x14\x07\x05\r \x0c!\x0c \r'
        b'\x1f\r\x1d\x10\x14\x18\x14\x19\x13\x19\x14\x18\x15\x18\x15\x16'
        b'\x18\x14\x19\x13\x1b\x10\x1f\x0b$\x05\xa1'
    ),
    # 1-bit rle, 5x45, generated from res/bubblefont/bubblefont_colon.png, 31 bytes
    (
        5, 45,
        b'\x16\x02\x02\x03\x02,\x01\x03\x02\x03\x02\x03\x03\x011\x02'
        b'\x02\x03\x02\x03\x02,\x01\x03\x02\x03\x02\x03\x03\x01\x07'
    )
)


class BubbleFontApp():
    """ Bubble font """
    NAME = "Bubble"
    ICON = BUBBLEFONT_DIGITS[1]

    def __init__(self):
        if(not hasattr(wasp,"fonts")): 
            wasp.fonts = {}
        wasp.fonts['Bubble'] = (2,BUBBLEFONT_DIGITS)   #ID:2. Please use random > 100 for user-fonts
        pass

    def unregister(self):
        del(wasp.fonts['Bubble'])

    def foreground(self):
        self._draw()


    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        draw.blit(BUBBLEFONT_DIGITS[0],    0,  60)
        draw.blit(BUBBLEFONT_DIGITS[1],   45,  60)
        draw.blit(BUBBLEFONT_DIGITS[2],   90,  60)
        draw.blit(BUBBLEFONT_DIGITS[3],  135,  60)
        draw.blit(BUBBLEFONT_DIGITS[4],  180,  60)
        draw.blit(BUBBLEFONT_DIGITS[5],    0, 125)
        draw.blit(BUBBLEFONT_DIGITS[6],   45, 125)
        draw.blit(BUBBLEFONT_DIGITS[7],   90, 125)
        draw.blit(BUBBLEFONT_DIGITS[8],  135, 125)
        draw.blit(BUBBLEFONT_DIGITS[9],  180, 125)


