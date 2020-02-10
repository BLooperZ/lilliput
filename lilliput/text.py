import operator
from dataclasses import dataclass, field
from functools import partial
from itertools import chain, takewhile
from typing import IO, Optional, Type

from .meta import MetaUnpacker, make_unpacker
from .raw import RawBytes
from .word import uint8

def safe_readcstr(stream: IO[bytes]) -> bytes:
    bound_read = iter(partial(RawBytes(1).unpack, stream), b'')
    return b''.join(takewhile(partial(operator.ne, b'\00'), bound_read))

@dataclass(frozen=True)
class NullTerminatedString(MetaUnpacker[str]):
    encoding: str = 'utf-8'

    def unpack(self, stream: IO[bytes]) -> str:
        return safe_readcstr(stream).decode(self.encoding)

    def pack(self, data: str) -> bytes:
        return data.encode(self.encoding) + b'\0'

cstring = NullTerminatedString('utf-8')

@dataclass(frozen=True)
class FixedSizeString(MetaUnpacker[str]):
    size: int
    encoding: str = 'utf-8'
    _reader: MetaUnpacker[bytes] = field(init=False, repr=False)

    def __post_init__(self):
        super().__setattr__('_reader', RawBytes(self.size))

    def unpack(self, stream: IO[bytes]) -> str:
        return self._reader.unpack(stream).decode(self.encoding)

    def pack(self, data: str) -> bytes:
        return self._reader.pack(data.encode(self.encoding))

@dataclass(frozen=True)
class LengthPrefixedString(MetaUnpacker[str]):
    prefixer: MetaUnpacker[int] = uint8
    encoding: str = 'utf-8'

    def unpack(self, stream: IO[bytes]) -> str:
        return FixedSizeString(self.prefixer.unpack(stream), self.encoding).unpack(stream)

    def pack(self, data: str) -> bytes:
        return self.prefixer.pack(len(data)) + data.encode(self.encoding)

pstring = LengthPrefixedString(uint8, encoding='utf-8')
