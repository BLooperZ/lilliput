from dataclasses import dataclass
from typing import IO, Optional, Sequence, Type, TypeVar

from .meta import MetaUnpacker

T = TypeVar('T')

@dataclass(frozen=True)
class BoundRepeat(MetaUnpacker[Sequence[T]]):
    entry: MetaUnpacker[T]
    bound: int

    def unpack(self, stream: IO[bytes]) -> Sequence[T]:
        return tuple(self.entry.unpack(stream) for _ in range(self.bound))

    def pack(self, data: Sequence[T]) -> bytes:
        return b''.join(self.entry.pack(d) for d in data)
