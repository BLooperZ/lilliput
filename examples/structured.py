import io
from dataclasses import field

from lilliput.meta import typedef
from lilliput.structure import Structure, unpacker
from lilliput.word import uint16le, ByteOrder
from lilliput.text import cstring
from lilliput.raw import RawBytes, consume

data = (
        b'\x00\x02\x00\x00\x00\x00'
        + b'\00' * (10)
        + b'lalalalaafdddddddd\x00'
    ) * 3 + b'blah'

# Dataclass API example

@unpacker
class ExampleData(Structure):
    version: int = typedef(uint16le)
    nframes: int = typedef(uint16le)
    dummy: int = typedef(uint16le)
    palette: bytes = typedef(RawBytes(10))
    custom: str = typedef(cstring)
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
Nested(data1=ExampleData(version=512, nframes=0, dummy=0, palette=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', custom='lalalalaafdddddddd', ignored_constant=8, ignored_factory=()), data2=ExampleData(version=512, nframes=0, dummy=0, palette=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', custom='lalalalaafdddddddd', ignored_constant=8, ignored_factory=()), rest=b'\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00lalalalaafdddddddd\x00blah')
"""
assert ex.data1.version == 512, ex.data1.version

dump = Nested.pack(ex)
assert dump == data, (dump, data)
