from dataclasses import dataclass
from typing import IO, Optional

from .meta import MetaUnpacker

class UnexpectedBufferSize(ValueError):
    def __init__(self, expected, given):
        super().__init__(f'Expected buffer of size {expected} but got size {given}')
        self.expected = expected
        self.given = given

def validate_buffer_size(data: bytes, size: Optional[int] = None):
    if size and len(data) != size:
        raise UnexpectedBufferSize(size, len(data))
    return data

@dataclass(frozen=True)
class RawBytes(MetaUnpacker[bytes]):
    size: Optional[int] = None

    def unpack(self, stream: IO[bytes]) -> bytes:
        # False alarm for type error, `read` method of IO accepts `None` as well.
        return validate_buffer_size(stream.read(self.size), self.size)  # type: ignore

    def pack(self, data: bytes) -> bytes:
        return validate_buffer_size(data, self.size)

consume = RawBytes()
