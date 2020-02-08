# lilliput
Declarative binary structure definitions for Python

## Usage

### Custom unpacker
``` python
import io
from dataclasses import dataclass
from typing import IO

from lilliput.meta import MetaUnpacker

@dataclass(frozen=True)
class SimpleRawBytes(MetaUnpacker[bytes]):
    size: int
    def pack(self, data: bytes) -> bytes:
        return data

    def unpack(self, stream: IO[bytes]) -> bytes:
        return stream.read(self.size)

"""
>>> SimpleRawBytes(5).unpack(io.BytesIO(b'\x00\x01\x02\x03\x04'))
b'\x00\x01\x02\x03\x04'
"""
```
[Another Example](lilliput/word.py)

### Dataclass Complex Stucture
``` python
import io

from lilliput.meta import typedef
from lilliput.structure import Structure, unpacker
from lilliput.word import uint8
from lilliput.text import cstring

@unpacker
class Example(Structure):
    word: int = typedef(uint8)

    # this commented out field will trigger mypy warning
    # mistyped_word: bytes = typedef(uint8)  # Incompatible types in assignment (expression has type "int", variable has type "bytes")

    name: str = typedef(cstring)

"""
>>> Example.unpack(io.BytesIO(b'\x01abc\x00'))
Example(word=1, name='abc')
"""
```
[Another Example](examples/structured.py)

### Functional API unpacker
``` python
import io
from dataclasses import dataclass
from typing import IO

from lilliput.meta import MetaUnpacker, make_unpacker

def simple_raw_bytes(size: int) -> MetaUnpacker[bytes]:
    def pack(data: bytes) -> bytes:
        return data
    def unpack(stream: IO[bytes]) -> bytes:
        return stream.read(size)
    return make_unpacker('SimpleRawBytes', pack=pack, unpack=unpack, data={'size': size})

"""
>>> simple_raw_bytes(5).unpack(io.BytesIO(b'\x00\x01\x02\x03\x04'))
b'\x00\x01\x02\x03\x04'
"""
```
[Another Example](examples/functional.py)
