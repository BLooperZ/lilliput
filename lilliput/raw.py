from dataclasses import dataclass
from typing import IO, Optional

from .meta import MetaUnpacker

class UnexpectedBufferSize(ValueError):
    def __init__(self, expected, given):
        super().__init__(f'Expected buffer of size {expected} but got size {given}')
        self.expected = expected
        self.given = given

@dataclass(frozen=True)
class RawBytes(MetaUnpacker[bytes]):
    size: Optional[int] = None

    def unpack(self, stream: IO[bytes]) -> bytes:
        # False alarm for type error, `read` method of IO accepts `None` as well.
        data = stream.read(self.size)  # type: ignore
        if self.size and len(data) != self.size:
            raise UnexpectedBufferSize(self.size, len(data))
        return data

    def pack(self, data: bytes) -> bytes:
        if self.size and len(data) != self.size:
            raise UnexpectedBufferSize(self.size, len(data))
        return data

consume = RawBytes()
