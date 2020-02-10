import io
from dataclasses import dataclass, field
from typing import Sequence

from lilliput.meta import typedef
from lilliput.structure import Structure, sequence_unpacker
from lilliput.word import uint16le, uint8, ByteOrder
from lilliput.text import cstring
from lilliput.raw import RawBytes, consume
from lilliput.repeat import BoundRepeat

data = (
        b'\x00\x02\x00\x00\x00\x00'
        + b'\00' * (5)
        + b'cstring\x00'
    ) * 3 + b'blah'

# Dataclass API example

# @SequenceUnpacker
@dataclass(frozen=True, order=True)
class ExampleData(Structure):
    word1: int = typedef(uint16le)
    word2: int = typedef(uint16le)
    word3: Sequence[int] = typedef(BoundRepeat(uint8, 2))
    raw_data: bytes = typedef(RawBytes(5))
    name: str = typedef(cstring)
    ignored_constant: int = 8
    ignored_factory: tuple = field(default_factory=tuple)

# @SequenceUnpacker
@dataclass(frozen=True, order=True)
class Nested(Structure):
    data: Sequence[ExampleData] = typedef(BoundRepeat(sequence_unpacker(ExampleData), 2))
    rest: bytes = typedef(consume)

@dataclass(frozen=True, order=True)
class ExampleData2(Structure):
    word1: int = typedef(uint16le)

@dataclass(frozen=True, order=True)
class ExampleData3(ExampleData2):
    word2: int = typedef(uint16le)

word1, word2 = ExampleData3(word1=9, word2=10)
print(word1, word2)

ex = sequence_unpacker(Nested).unpack(io.BytesIO(data))

print(ex)
"""
Nested(data=(ExampleData(word1=512, word2=0, word3=(0, 0), raw_data=b'\x00\x00\x00\x00\x00', name='cstring', ignored_constant=8, ignored_factory=()), ExampleData(word1=512, word2=0, word3=(0, 0), raw_data=b'\x00\x00\x00\x00\x00', name='cstring', ignored_constant=8, ignored_factory=())), rest=b'\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00cstring\x00blah')
"""
assert ex.data[0].word1 == 512, ex.data[0].word1

dump = sequence_unpacker(Nested).pack(ex)
assert dump == data, (dump, data)
