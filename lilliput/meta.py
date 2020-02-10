import inspect
from dataclasses import dataclass, field, asdict, make_dataclass
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
    namespace: MetaNamespace[T] = field(repr=False)

    def __post_init__(self):
        for key, value in asdict(self.namespace).items():
            super().__setattr__(key, value)

def namespace(
        unpack: Callable[[IO[bytes]], T],
        pack: Callable[[T], bytes]
) -> MetaUnpacker[T]:
    return NamespaceUnpack(MetaNamespace(unpack=unpack, pack=pack))

def make_field(name, p):
    annotation = p.annotation != inspect._empty and p.annotation
    default = p.default != inspect._empty and field(default=p.default)
    return (name, annotation or Any, default or None)

def fdata(name: str):
    def decorator(func: Callable[..., MetaUnpacker[T]]):
        def inner(*args, **kwargs):
            namespace = func(*args, **kwargs).namespace
            sig = inspect.signature(func).parameters
            return make_dataclass(
                name, bases=(NamespaceUnpack,),
                fields=(make_field(name, p) for name, p in sig.items()),
                frozen=True
            )(namespace, *args, **kwargs)
        return inner
    return decorator

def typedef(
        reader: MetaUnpacker[T], *,
        metadata: Optional[Mapping[str, Any]] = None,
        **kwargs
) -> T:
    metadata = metadata or {}
    # NOTE: can use metadata for unpacker configuration (e.g. alignment, condition)
    return field(metadata=dict(metadata, unpacker=reader), **kwargs)
