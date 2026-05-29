from typing import Optional

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError
from starlette.datastructures import QueryParams

from agave.core.query_params import (
    EmptyQueryMapping,
    _is_list_annotation,
    validate_query_params,
)


class SampleQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ids: Optional[list[str]] = None
    name: Optional[str] = None
    active: Optional[bool] = None


def test_validate_query_params_list_fields() -> None:
    query = QueryParams('ids=a&ids=b&name=Frida')
    validated = validate_query_params(query, SampleQuery)
    assert validated.ids == ['a', 'b']
    assert validated.name == 'Frida'


def test_validate_query_params_single_list_value() -> None:
    query = QueryParams('ids=US1')
    validated = validate_query_params(query, SampleQuery)
    assert validated.ids == ['US1']


def test_validate_query_params_scalar_field() -> None:
    query = QueryParams('name=Frida')
    validated = validate_query_params(query, SampleQuery)
    assert validated.name == 'Frida'
    assert validated.ids is None


def test_old_unpack_pattern_would_fail_validation() -> None:
    query = QueryParams('ids=US1&ids=US2')
    with pytest.raises(ValidationError):
        SampleQuery(**dict(query))  # type: ignore[arg-type]


def test_validate_query_params_rejects_unknown_fields() -> None:
    query = QueryParams('wrong_param=value')
    with pytest.raises(ValidationError):
        validate_query_params(query, SampleQuery)


def test_empty_query_mapping() -> None:
    mapping = EmptyQueryMapping()
    assert 'x' not in mapping
    assert mapping.get('x') is None
    assert mapping.get('x', 'default') == 'default'
    assert mapping.getlist('x') == []
    assert list(mapping) == []


def test_validate_query_params_empty_mapping() -> None:
    validated = validate_query_params(EmptyQueryMapping(), SampleQuery)
    assert validated.ids is None
    assert validated.name is None


def test_is_list_annotation() -> None:
    assert _is_list_annotation(list[str]) is True
    assert _is_list_annotation(Optional[list[str]]) is True
    assert _is_list_annotation(str) is False
    assert _is_list_annotation(Optional[str]) is False
