import io
from typing import IO

from lilliput.meta import MetaUnpacker, make_unpacker
from lilliput.word import ByteOrder, uint16le
from lilliput.raw import RawBytes

# Functional API example

# example: using functional API to implement the same dataclass based `FixedSizeWord` unpacker available in `word.py`
def fixed_size_word(
        size: int,
        byteorder: ByteOrder = ByteOrder.LE,
        signed: bool = False
) -> MetaUnpacker[int]:

    reader = RawBytes(size)

    def unpack(stream: IO[bytes]) -> int:
        return int.from_bytes(reader.unpack(stream), byteorder=byteorder, signed=signed)

    def pack(num: int) -> bytes:
        return num.to_bytes(size, byteorder=byteorder, signed=signed)

    return make_unpacker(
        'FixedSizeWord',
        pack=pack,
        unpack=unpack,
        data={'size': size, 'byteorder': byteorder, 'signed': signed}
    )

fuint16le = fixed_size_word(2, ByteOrder.LE, False)

print(uint16le)
print(fuint16le)
"""
FixedSizeWord(size=2, byteorder=<ByteOrder.LE: 'little'>, signed=False)
FixedSizeWord(size=2, byteorder=<ByteOrder.LE: 'little'>, signed=False)
"""

assert uint16le.unpack(io.BytesIO(b'\00\01')) == fuint16le.unpack(io.BytesIO(b'\00\01'))
