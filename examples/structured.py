import io
from dataclasses import field

from lilliput.meta import typedef
from lilliput.structure import Structure, unpacker
from lilliput.word import uint16le, ByteOrder
from lilliput.text import cstring
from lilliput.raw import RawBytes, consume

data = (
        b'\x00\x02\x00\x00\x00\x00'
        + b'\00' * (5)
        + b'cstring\x00'
    ) * 3 + b'blah'

# Dataclass API example

@unpacker
class ExampleData(Structure):
    word1: int = typedef(uint16le)
    word2: int = typedef(uint16le)
    word3: int = typedef(uint16le)
    raw_data: bytes = typedef(RawBytes(5))
    name: str = typedef(cstring)
    ignored_constant: int = 8
    ignored_factory: tuple = field(default_factory=tuple)

@unpacker
class Nested(Structure):
    data1: ExampleData = typedef(ExampleData)
    data2: ExampleData = typedef(ExampleData)
    rest: bytes = typedef(consume)

ex = Nested.unpack(io.BytesIO(data))

print(ex)
"""
Nested(data1=ExampleData(word1=512, word2=0, word3=0, raw_data=b'\x00\x00\x00\x00\x00', name='cstring', ignored_constant=8, ignored_factory=()), data2=ExampleData(word1=512, word2=0, word3=0, raw_data=b'\x00\x00\x00\x00\x00', name='cstring', ignored_constant=8, ignored_factory=()), rest=b'\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00cstring\x00blah')
"""
assert ex.data1.word1 == 512, ex.data1.word1

dump = Nested.pack(ex)
assert dump == data, (dump, data)
