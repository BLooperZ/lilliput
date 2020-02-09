import operator
from dataclasses import dataclass, field
from functools import partial
from itertools import chain, takewhile
from typing import IO, Type

from .meta import MetaUnpacker, make_unpacker
from .raw import RawBytes
from .word import uint8

def safe_readcstr(stream: IO[bytes], sentinel: bytes = b'\xab') -> str:
    try:
        bound_read = chain(iter(partial(stream.read, 1), b''), [sentinel])
        res = b''.join(takewhile(partial(operator.ne, b'\00'), bound_read))
        return res.decode()
    except UnicodeDecodeError:
        raise ValueError('reached EOF before null-termination')

@dataclass(frozen=True)
class NullTerminatedString(MetaUnpacker[str]):
    encoding: str = 'utf-8'

    def unpack(self, stream: IO[bytes]) -> str:
        return safe_readcstr(stream).encode('utf-8').decode(self.encoding)

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
