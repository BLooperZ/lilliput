from dataclasses import dataclass, field, asdict
from typing import (
    Any,
    Callable,
    Generic,
    IO,
    Mapping,
    Optional,
    Type,
    TypeVar,
)

T = TypeVar('T')

class MetaUnpacker(Generic[T]):
    # allow using __init__() from dataclass
    def __init__(self, *args, **kwargs): ...

    # signatures of pack/unpack methods

    # TODO: provide optional context parameter for conditional unpacking
    def unpack(self, stream: IO[bytes]) -> T: ...

    def pack(self, data: T) -> bytes: ...

@dataclass(frozen=True)
class MetaNamespace(Generic[T]):
    unpack: Callable[[IO[bytes]], T] = field(repr=False)
    pack: Callable[[T], bytes] = field(repr=False)

@dataclass(frozen=True)
class NamespaceUnpack(MetaUnpacker[T]):
    namespace: MetaNamespace[T]

    def __post_init__(self):
        for key, value in asdict(self.namespace).items():
            super().__setattr__(key, value)

def namespace(func: Callable[..., MetaNamespace[T]]):
    def inner(*args, **kwargs) -> MetaUnpacker[T]:
        return NamespaceUnpack(func(*args, **kwargs))
    return inner

def typedef(
        reader: MetaUnpacker[T], *,
        metadata: Optional[Mapping[str, Any]] = None,
        **kwargs
) -> T:
    metadata = metadata or {}
    # NOTE: can use metadata for unpacker configuration (e.g. alignment, condition)
    return field(metadata=dict(metadata, unpacker=reader), **kwargs)
