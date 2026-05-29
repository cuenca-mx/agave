from __future__ import annotations

from types import UnionType
from typing import Any, Iterator, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel

ModelT = TypeVar('ModelT', bound=BaseModel)


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


def validate_query_params(
    query_mapping: Any, model_cls: type[ModelT]
) -> ModelT:
    params: dict[str, Any] = {}
    for name in query_mapping:
        field = model_cls.model_fields.get(name)
        if field and _is_list_annotation(field.annotation):
            params[name] = query_mapping.getlist(name)
        else:
            params[name] = query_mapping.get(name)
    return model_cls(**params)


class EmptyQueryMapping:
    def __contains__(self, key: str) -> bool:
        return False

    def __iter__(self) -> Iterator[str]:
        return iter(())

    def get(self, key: str, default: Any = None) -> Any:
        return default

    def getlist(self, key: str) -> list[str]:
        return []
