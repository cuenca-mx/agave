from __future__ import annotations

from types import UnionType
from typing import Any, Iterator, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel

ModelT = TypeVar('ModelT', bound=BaseModel)


def comma_separated_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(',') if part.strip()]


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
    query_mapping: Any, model_cls: type[BaseModel]
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for name in query_mapping:
        raw = query_mapping.get(name)
        if name in model_cls.model_fields:
            field = model_cls.model_fields[name]
            if _is_list_annotation(field.annotation):
                if raw is None:
                    continue
                if isinstance(raw, str):
                    params[name] = comma_separated_list(raw)
                else:
                    params[name] = list(raw)
            else:
                params[name] = raw
        else:
            params[name] = raw
    return params


def validate_query_params(
    query_mapping: Any, model_cls: type[ModelT]
) -> ModelT:
    return model_cls(**build_query_dict(query_mapping, model_cls))


def query_params_for_url(query: BaseModel) -> dict[str, Any]:
    params = query.model_dump()
    for name, field in type(query).model_fields.items():
        value = params.get(name)
        if _is_list_annotation(field.annotation) and isinstance(value, list):
            params[name] = ','.join(value)
    return params


class EmptyQueryMapping:
    def __contains__(self, key: str) -> bool:
        return False

    def __iter__(self) -> Iterator[str]:
        return iter(())

    def get(self, key: str, default: Any = None) -> Any:
        return default
