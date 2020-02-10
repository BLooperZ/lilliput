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

from .meta import MetaUnpacker, namespace, fdata

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

@fdata('SkipField')
def skip_field(
        field: Any
) -> MetaUnpacker[Any]:

    _default = field.default
    _factory = field.default_factory

    def unpack(stream: IO[bytes]) -> Any:
        if _default != MISSING:
            return _default
        if _factory != MISSING:
            return _factory()
        raise TypeError(f'missing required argument: {repr(field.name)}')

    def pack(data: Any) -> bytes:
        return b''

    return namespace(pack=pack, unpack=unpack)

@fdata('SequenceUnpacker')
def sequence_unpacker(
        structure: Type[NT]
) -> MetaUnpacker[NT]:

    _readers = tuple(
        v.metadata.get('unpacker', skip_field(v)) for v in fields(structure)
    )

    def unpack(stream: IO[bytes]) -> NT:
        return structure(*(reader.unpack(stream) for reader in _readers))

    def pack(inst: NT) -> bytes:
        data: Iterator[Tuple[Any, MetaUnpacker[Any]]] = zip(inst, _readers)
        return b''.join(reader.pack(value) for value, reader in data)

    return namespace(pack=pack, unpack=unpack)
