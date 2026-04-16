from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar, cast

from .repository_base import RepositoryBase
from .repo_context import RepositoryContext
from .session_factory import SessionFactory
from .table_base import TableBase

T = TypeVar("T", bound=TableBase)


class EntityProxy(Generic[T]):
    """
    Lazy-loading proxy for an entity instance.

    Note: This base class delegates attribute access via `__getattr__`, so "special"
    methods (like `__len__`, operators, etc.) won't be proxied unless you use the
    `make_typed_entity_proxy()` factory below.
    """

    _obj: Optional[T]
    _id: int
    _cls: type[T]
    _context: Any
    _connection_string: str

    def __init__(self, id: int, cls: type[T], context: RepositoryContext, connection_string:str):
        object.__setattr__(self, "_obj", None)
        object.__setattr__(self, "_id", id)
        object.__setattr__(self, "_cls", cls)
        object.__setattr__(self, "_context", context)
        object.__setattr__(self, "_connection_string", connection_string)

    def _initialize(self) -> T:
        obj = object.__getattribute__(self, "_obj")
        if obj is None:
            context = object.__getattribute__(self, "_context")
            cls = object.__getattribute__(self, "_cls")
            id = object.__getattribute__(self, "_id")
            repo:RepositoryBase = context.get_repository(cls)
            with SessionFactory.connect(self._connection_string) as session:
                obj = repo._get_by_id(session, id)
                object.__setattr__(self, "_obj", obj)
        return cast(T, obj)

    def __getattr__(self, name: str) -> Any:
        obj = self._initialize()
        return getattr(obj, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        obj = self._initialize()
        setattr(obj, name, value)


def make_typed_entity_proxy(entity_cls: type[T]) -> type[T]:
    """
    Create a proxy *class* that has the same static type as `entity_cls`.

    Usage:
        UserProxy = make_typed_entity_proxy(User)
        user: User = UserProxy(id=..., context=...)

    Limitations:
    - Special methods invoked by syntax (operators) are looked up on the type, not
      the instance. Subclassing helps, but if you need perfect operator behavior
      you may still need explicit forwarding methods.
    """

    class _TypedEntityProxy(entity_cls):  # type: ignore[misc, valid-type]
        _proxy: EntityProxy[T]

        def __init__(self, id: int, context: RepositoryContext, connection_string:str):
            object.__setattr__(self, "_proxy", EntityProxy[T](id=id, cls=entity_cls, context=context, connection_string=connection_string))

        def __getattribute__(self, name: str) -> Any:
            if name in {"_proxy", "__class__", "__dict__", "__weakref__", "__repr__", "__str__", "__dir__"}:
                return object.__getattribute__(self, name)
            proxy = object.__getattribute__(self, "_proxy")
            obj = proxy._initialize()
            return getattr(obj, name)

        def __setattr__(self, name: str, value: Any) -> None:
            if name == "_proxy" or name.startswith("_TypedEntityProxy__"):
                object.__setattr__(self, name, value)
                return
            proxy = object.__getattribute__(self, "_proxy")
            obj = proxy._initialize()
            setattr(obj, name, value)

        def __dir__(self) -> list[str]:
            proxy = object.__getattribute__(self, "_proxy")
            try:
                obj = proxy._initialize()
                return sorted(set(dir(entity_cls) + dir(obj) + list(object.__getattribute__(self, "__dict__").keys())))
            except Exception:
                return sorted(set(dir(entity_cls) + list(object.__getattribute__(self, "__dict__").keys())))

        def __repr__(self) -> str:
            proxy = object.__getattribute__(self, "_proxy")
            obj = object.__getattribute__(proxy, "_obj")
            if obj is None:
                return f"<{entity_cls.__name__}Proxy (uninitialized) id={object.__getattribute__(proxy, '_id')!r}>"
            return repr(obj)

    _TypedEntityProxy.__name__ = f"{entity_cls.__name__}Proxy"
    return cast(type[T], _TypedEntityProxy)
