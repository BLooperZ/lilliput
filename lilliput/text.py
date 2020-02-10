import operator
from dataclasses import dataclass, field
from functools import partial
from itertools import chain, takewhile
from typing import IO, Optional, Type

from .meta import MetaUnpacker, MetaNamespace, namespace
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

@namespace
def fixed_size_string(
        size: int,
        encoding: str = 'utf-8'
) -> MetaNamespace[str]:

    _reader = RawBytes(size)

    def unpack(stream: IO[bytes]) -> str:
        return _reader.unpack(stream).decode(encoding)

    def pack(data: str) -> bytes:
        return _reader.pack(data.encode(encoding))

    return MetaNamespace(pack=pack, unpack=unpack)

@dataclass(frozen=True)
class LengthPrefixedString(MetaUnpacker[str]):
    prefixer: MetaUnpacker[int] = uint8
    encoding: str = 'utf-8'

    def unpack(self, stream: IO[bytes]) -> str:
        return fixed_size_string(self.prefixer.unpack(stream), self.encoding).unpack(stream)

    def pack(self, data: str) -> bytes:
        return self.prefixer.pack(len(data)) + data.encode(self.encoding)

pstring = LengthPrefixedString(uint8, encoding='utf-8')
