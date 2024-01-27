import wasp

# https://www.dafont.com/neo-sci-fi-v2-0.font - 100% free
SCIFIFONT_DIGITS = (
(
    45, 45,
    b'`!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c\x0b'
    b'\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\xc0\x0b'
    b'\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b'
    b'\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c!\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'`'
),
# 1-bit RLE, 45x45, generated from res/scififont/scififont_1.png, 83 bytes
(
    45, 45,
    b'o\x13\x19\x14\x18\x15\x17\x16\x16\x17\x15\x18\x14\x19\x13\x1a'
    b'\x12\x1b\x11\x1c\x10\x1d\x0f\x1e\x0e\x1f\r \x0c!\x1e\x0f'
    b'\x1e\x0f\x1e\x0f\x1e\x0f\x1e\x0f\x1e\x0f\x1e\x0f\x1e\x0f\x1e\x0f'
    b'\x1e\x0f\x1e\x0f\x1e\x0f\x1e\x0f\x1e\x0f\x1e\x0f\x0b"\x0b"'
    b'\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"'
    b'\x0b"_'
),
# 1-bit RLE, 45x45, generated from res/scififont/scififont_2.png, 91 bytes
(
    45, 45,
    b'^%\x08%\x08%\x08%\x08%\x08%\x08%\x08%'
    b'\x08%\x08%\x08%\x08\x0b\x0b\x0f\x08\x0b\n\x10\x08\x0b'
    b'\t\x11\x08\x0b\x08\x12\x1a\x13\x19\x14\x18\x15\x17\x16\x16\x16'
    b'\x16\x16\x16\x16\x16\x16\x16\x16\x16\x16\x16\x16\x16\x16\x16\x16'
    b'\x16\x16\x16\x16\x16!\x0b"\n#\t$\t$\t$'
    b'\t$\t$\t$\t$\t$_'
),
# 1-bit RLE, 45x45, generated from res/scififont/scififont_3.png, 97 bytes
(
    45, 45,
    b'a!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x1c\x11\x1d\x10\x1e\x0f\x1e\x0f\x0e\n'
    b'\x06\x0f\r\r\x04\x0f\x0c\x0e\x03\x10\x0c\x0f\x01\x11\x0c!'
    b'\x0c!\x0c!\x0c!\x0c\x0e\x03\x10\x0c\x0e\x04\x0f\r\x0c'
    b'\x05\x0f\x1e\x0f\x1e\x0f\x1d\x10\x1c\x11\x0c!\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'_'
),
# 1-bit RLE, 45x45, generated from res/scififont/scififont_4.png, 113 bytes
(
    45, 45,
    b'`\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b'
    b'\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b'
    b'\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b'
    b'\x0c\x0b\x0b\x0b\x0c\x0c\n\x0b\x0c\r\x08\x0c\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\r '
    b'\x0e\x1f\x19\x14\x1a\x13\x1b\x12\x1b\x12\x1b\x12\x1b\x12\x1b\x12'
    b'\x1b\x12\x1b\x12\x1b\x12\x1b\x12\x1b\x12\x1b\x12\x1b\x12\x1b\x12'
    b'`'
),
# 1-bit RLE, 45x45, generated from res/scififont/scififont_5.png, 83 bytes
(
    45, 45,
    b'`!\x0c \r\x1f\x0e\x1e\x0f\x1d\x10\x1c\x11\x1b\x12\x1a'
    b'\x13\x19\x14\x18\x15\x17\x16\x16\x17\x15\x18\x14\x19\x13\x1a\x12'
    b'\x1b\x11\x1c\x10\x1d\x0f\x1e\x0f\x1e\x0f\x1e\x10\x1d!\x0c!'
    b'\x0c!\x0c!\x1a\x13\x1b\x12\x1b\x12\x1a\x13\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'\x0c!`'
),
# 1-bit RLE, 45x45, generated from res/scififont/scififont_6.png, 99 bytes
(
    45, 45,
    b'`!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c\x11\x1c\x10\x1d\x0f\x1e\x0f\x1e\x0f'
    b'\x1e\x0f\x1e\x10\x1d\x12\x1b!\x0c!\x0c!\x0c\x0e\x05\x0e'
    b'\x0c\x0c\t\x0c\x0c\x0c\n\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b'
    b'\x0c\x0b\x0b\x0b\x0c\x0c\n\x0b\x0c\r\x07\r\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'\x0c!`'
),
# 1-bit RLE, 45x45, generated from res/scififont/scififont_7.png, 83 bytes
(
    45, 45,
    b'a!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x1e\x0f'
    b'\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f'
    b'\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f\x1d\x0f'
    b'\x1d\x0f\x1d\x0f\x1e\x0e\x1f\r \x0c!\x0b"\n#\t'
    b'$\x08x'
),
# 1-bit RLE, 45x45, generated from res/scififont/scififont_8.png, 115 bytes
(
    45, 45,
    b'`!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c\r\x07\r\x0c\x0c\t\x0c\x0c\x0b'
    b'\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0c'
    b'\t\x0c\x0c\x0e\x05\x0e\x0c!\x0c!\x0c!\x0c\x0e\x05\x0e'
    b'\x0c\x0c\t\x0c\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b'
    b'\x0c\x0b\x0b\x0b\x0c\x0c\t\x0c\x0c\r\x07\r\x0c!\x0c!'
    b'\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!\x0c!'
    b'\x0c!`'
),
# 1-bit RLE, 45x45, generated from res/scififont/scififont_9.png, 99 bytes
(
    45, 45,
    b'`"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"'
    b'\x0b"\x0b"\x0b"\x0b\x0e\x06\x0e\x0b\x0c\n\x0c\x0b\x0c'
    b'\n\x0c\x0b\x0b\x0b\x0c\x0b\x0b\x0b\x0c\x0b\x0c\n\x0c\x0b\x0c'
    b'\t\r\x0b\x0e\x06\x0e\x0b"\x0b"\x0b"\x0b"\x0b"'
    b'\x0b"\x0b"!\x0c!\x0c!\x0c!\x0c\x0b"\x0b"'
    b'\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"\x0b"'
    b'\x0b"_'
),
# 1-bit RLE, 5x45, generated from res/scififont/scififont_colon.png, 13 bytes
(
    5, 45,
    b'B\x03\x01\x1e\x01\x03\x11\x03\x01\x1e\x01\x03B'
)
)


class ScifiFontApp():
    """Scififont"""
    NAME = "Scifi"
    ICON = SCIFIFONT_DIGITS[3]

    def __init__(self):
        if(not hasattr(wasp,"fonts")): 
            wasp.fonts = {}
        wasp.fonts['scifi'] = (3,SCIFIFONT_DIGITS)   #ID:3. Please use random > 100 for user-fonts
        pass

    def unregister(self):
        del(wasp.fonts['scifi'])

    def foreground(self):
        self._draw()


    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        draw.blit(SCIFIFONT_DIGITS[0],    0,  60)
        draw.blit(SCIFIFONT_DIGITS[1],   45,  60)
        draw.blit(SCIFIFONT_DIGITS[2],   90,  60)
        draw.blit(SCIFIFONT_DIGITS[3],  135,  60)
        draw.blit(SCIFIFONT_DIGITS[4],  180,  60)
        draw.blit(SCIFIFONT_DIGITS[5],    0, 125)
        draw.blit(SCIFIFONT_DIGITS[6],   45, 125)
        draw.blit(SCIFIFONT_DIGITS[7],   90, 125)
        draw.blit(SCIFIFONT_DIGITS[8],  135, 125)
        draw.blit(SCIFIFONT_DIGITS[9],  180, 125)

