import io
from enum import Enum
from dataclasses import dataclass, field
from functools import partial
from typing import IO

from .meta import namespace, MetaUnpacker, fdata
from .raw import RawBytes

class ByteOrder(str, Enum):
    LE = 'little'
    BE = 'big'

@fdata('FixedSizeWord')
def fixed_size_word(
        size: int,
        byteorder: ByteOrder,
        signed: bool
) -> MetaUnpacker[int]:

    _reader = RawBytes(size)

    def unpack(stream: IO[bytes]) -> int:
        return int.from_bytes(_reader.unpack(stream), byteorder=byteorder, signed=signed)

    def pack(num: int) -> bytes:
        return num.to_bytes(size, byteorder=byteorder, signed=signed)

    return namespace(pack=pack, unpack=unpack)

unsigned_le = partial(fixed_size_word, byteorder=ByteOrder.LE, signed=False)
signed_le = partial(fixed_size_word, byteorder=ByteOrder.LE, signed=True)

unsigned_be = partial(fixed_size_word, byteorder=ByteOrder.BE, signed=False)
signed_be = partial(fixed_size_word, byteorder=ByteOrder.BE, signed=True)

uint8 = unsigned_le(1)
int8 = signed_le(1)

print(int8)

uint16le = unsigned_le(2)
uint24le = unsigned_le(3)
uint32le = unsigned_le(4)
uint64le = unsigned_le(8)

int16le = signed_le(2)
int24le = signed_le(3)
int32le = signed_le(4)
int64le = signed_le(8)

uint16be = unsigned_be(2)
uint24be = unsigned_be(3)
uint32be = unsigned_be(4)
uint64be = unsigned_be(8)

int16be = signed_be(2)
int24be = signed_be(3)
int32be = signed_be(4)
int64be = signed_be(8)
