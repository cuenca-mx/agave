from __future__ import annotations

from types import UnionType
from typing import (
    Any,
    Iterator,
    Protocol,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel

ModelT = TypeVar('ModelT', bound=BaseModel)


class QueryParamMapping(Protocol):
    def __contains__(self, key: str) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def get(self, key: str, default: Any = None) -> Any: ...

    def getlist(self, key: str) -> list[str]: ...


def _is_list_annotation(annotation: Any) -> bool:
    origin = get_origin(annotation)
    if origin is list:
        return True
    if origin in (Union, UnionType):
        return any(
            _is_list_annotation(arg)
            for arg in get_args(annotation)
            if arg is not type(None)
        )
    return False


def build_query_dict(
    query_mapping: QueryParamMapping, model_cls: type[BaseModel]
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for name in query_mapping:
        if name in model_cls.model_fields:
            field = model_cls.model_fields[name]
            if _is_list_annotation(field.annotation):
                params[name] = query_mapping.getlist(name)
            else:
                params[name] = query_mapping.get(name)
        else:
            params[name] = query_mapping.get(name)
    return params


def validate_query_params(
    query_mapping: QueryParamMapping, model_cls: type[ModelT]
) -> ModelT:
    return model_cls(**build_query_dict(query_mapping, model_cls))


class EmptyQueryMapping:
    def __contains__(self, key: str) -> bool:
        return False

    def get(self, key: str, default: Any = None) -> Any:
        return default

    def getlist(self, key: str) -> list[str]:
        return []


class ParseQsQueryMapping:
    """Query mapping built from a raw query string (e.g. Chalice)."""

    def __init__(self, query_string: str | bytes | None) -> None:
        from urllib.parse import parse_qsl

        if not query_string:
            self._items: list[tuple[str, str]] = []
            return
        if isinstance(query_string, bytes):
            query_string = query_string.decode('latin-1')
        self._items = parse_qsl(query_string, keep_blank_values=True)

    def __iter__(self) -> Iterator[str]:
        seen: set[str] = set()
        for key, _ in self._items:
            if key not in seen:
                seen.add(key)
                yield key

    def __contains__(self, key: str) -> bool:
        return any(k == key for k, _ in self._items)

    def get(self, key: str, default: Any = None) -> Any:
        values = self.getlist(key)
        if not values:
            return default
        return values[-1]

    def getlist(self, key: str) -> list[str]:
        return [v for k, v in self._items if k == key]
