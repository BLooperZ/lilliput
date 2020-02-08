from dataclasses import make_dataclass, field
from typing import (
    Any,
    Callable,
    Generic,
    IO,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union
)

T = TypeVar('T')

class MetaUnpacker(Generic[T]):
    # allow using __init__() from dataclass
    def __init__(self, *args, **kwargs): ...

    # signatures of pack/unpack methods

    # TODO: provide optional context parameter for conditional unpacking
    def unpack(self, stream: IO[bytes]) -> T: ...

    def pack(self, data: T) -> bytes: ...

def typedef(
        reader: Union[MetaUnpacker[T], Type[T]], *,
        metadata: Optional[Mapping[str, Any]] = None,
        **kwargs
) -> T:
    metadata = metadata or {}
    # NOTE: can use metadata for unpacker configuration (e.g. alignment, condition)
    return field(metadata=dict(metadata, unpacker=reader), **kwargs)

def make_unpacker(
        name: str,
        pack: Callable[[T], bytes],
        unpack: Callable[[IO[bytes]], T],
        namespace: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None
) -> MetaUnpacker[T]:
    data = data or {}
    namespace = namespace or {}

    return make_dataclass(
        name, bases=(MetaUnpacker,), 
        fields=tuple((key, type(value), value) for key, value in data.items()),
        namespace=dict(namespace, pack=staticmethod(pack), unpack=staticmethod(unpack)),
        frozen=True
    )(*data.values())
