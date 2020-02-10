from collections import abc
from dataclasses import dataclass, field, fields, MISSING
from typing import (
    Any,
    IO,
    Iterator,
    Tuple,
    Type,
    TypeVar
)

from .meta import MetaUnpacker, MetaNamespace, namespace

# https://stackoverflow.com/questions/44287623/a-way-to-subclass-namedtuple-for-purposes-of-typechecking
class Structure(abc.Sequence):
    # make a dataclass tuple-like by accessing fields by index
    def __getitem__(self, i):
        return getattr(self, fields(self)[i].name)

    def __len__(self) -> int:
        return len(fields(self))

    def __iter__(self):
        return (getattr(self, f.name) for f in fields(self))

NT = TypeVar('NT', bound=Structure)

@dataclass(frozen=True)
class SkipUnpacker(MetaUnpacker[Any]):
    field: Any

    def unpack(self, stream: IO[bytes]) -> Any:
        if self.field.default == MISSING:
            if self.field.default_factory == MISSING:
                raise TypeError(f'missing required argument: {repr(self.field.name)}')
            return self.field.default_factory()
        return self.field.default

    def pack(self, data: Any) -> bytes:
        return b''

@namespace
def sequence_unpacker(
        structure: Type[NT]
) -> MetaNamespace[NT]:

    _readers = tuple(
        v.metadata.get('unpacker', SkipUnpacker(v)) for v in fields(structure)
    )

    def unpack(stream: IO[bytes]) -> NT:
        return structure(*(reader.unpack(stream) for reader in _readers))

    def pack(inst: NT) -> bytes:
        data: Iterator[Tuple[Any, MetaUnpacker[Any]]] = zip(inst, _readers)
        return b''.join(reader.pack(value) for value, reader in data)

    return MetaNamespace(pack=pack, unpack=unpack)
