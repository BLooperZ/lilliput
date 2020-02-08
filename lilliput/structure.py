from collections import abc
from dataclasses import dataclass, field, fields, _MISSING_TYPE
from typing import (
    Any,
    IO,
    Iterator,
    NamedTuple,
    Sequence,
    Tuple,
    Type,
    TypeVar
)

from .meta import MetaUnpacker

# https://stackoverflow.com/questions/44287623/a-way-to-subclass-namedtuple-for-purposes-of-typechecking
class Structure(abc.Sequence, MetaUnpacker):
    # make a dataclass tuple-like by accessing fields by index
    def __getitem__(self, i):
        return getattr(self, fields(self)[i].name)

    def __len__(self) -> int:
        return len(fields(self))

    def __iter__(self):
        return (getattr(self, f.name) for f in fields(self))

    # make type checkers aware of pack/unpack
    @classmethod
    def pack(cls, data) -> bytes: ...

    @classmethod
    def unpack(cls, stream: IO[bytes]): ...

NT = TypeVar('NT', bound=Structure)

@dataclass(frozen=True)
class SkipUnpacker(MetaUnpacker[Any]):
    field: Any

    def unpack(self, stream: IO[bytes]) -> Any:
        if isinstance(self.field.default, _MISSING_TYPE):
            if isinstance(self.field.default_factory, _MISSING_TYPE):
                raise TypeError(f'missing required argument: {repr(self.field.name)}')
            return self.field.default_factory()
        return self.field.default

    def pack(self, data: Any) -> bytes:
        return b''

@dataclass(frozen=True)
class SequenceUnpacker(MetaUnpacker[NT]):
    nt: Type[NT]
    _readers: Sequence[MetaUnpacker] = field(init=False, repr=False)

    def __post_init__(self):
        super().__setattr__('_readers', tuple(
            v.metadata.get('unpacker', SkipUnpacker(v))
            for v in fields(self.nt)
        ))

    def unpack(self, stream: IO[bytes]) -> NT:
        return self.nt(*(
            reader.unpack(stream) for reader in self._readers
        ))

    def pack(self, inst: NT) -> bytes:
        data: Iterator[Tuple[Any, MetaUnpacker[Any]]] = zip(inst, self._readers)
        return b''.join(reader.pack(value) for value, reader in data)

# allow using given class as unpacker and in type annotations
def unpacker(cls: Type[NT]):
    dcls = dataclass(frozen=True, order=True)(cls)
    inst = SequenceUnpacker(dcls)

    return type(
        dcls.__name__, (dcls, MetaUnpacker),
        {
            'pack': inst.pack,
            'unpack': inst.unpack
        }
    )
