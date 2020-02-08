from enum import Enum
from dataclasses import dataclass, field
from functools import partial
from typing import IO

from .meta import MetaUnpacker
from .raw import RawBytes

class ByteOrder(str, Enum):
    LE = 'little'
    BE = 'big'

@dataclass(frozen=True)
class FixedSizeWord(MetaUnpacker[int]):
    size: int
    byteorder: ByteOrder = ByteOrder.LE
    signed: bool = False
    _reader: MetaUnpacker[bytes] = field(init=False, repr=False)

    def __post_init__(self):
        super().__setattr__('_reader', RawBytes(self.size))

    def unpack(self, stream: IO[bytes]) -> int:
        return int.from_bytes(self._reader.unpack(stream), byteorder=self.byteorder, signed=self.signed)

    def pack(self, num: int) -> bytes:
        return num.to_bytes(self.size, byteorder=self.byteorder, signed=self.signed)

unsigned_le = partial(FixedSizeWord, byteorder=ByteOrder.LE, signed=False)
signed_le = partial(FixedSizeWord, byteorder=ByteOrder.LE, signed=True)

unsigned_be = partial(FixedSizeWord, byteorder=ByteOrder.BE, signed=False)
signed_be = partial(FixedSizeWord, byteorder=ByteOrder.BE, signed=True)

uint8 = unsigned_le(1)
int8 = signed_le(1)

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
