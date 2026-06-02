from typing import Optional

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError
from starlette.datastructures import QueryParams

from agave.core.query_params import (
    EmptyQueryMapping,
    comma_separated_list,
    query_params_for_url,
    validate_query_params,
)


class SampleQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ids: Optional[list[str]] = None
    name: Optional[str] = None
    active: Optional[bool] = None


def test_comma_separated_list() -> None:
    assert comma_separated_list('a,b') == ['a', 'b']
    assert comma_separated_list('a, b ,c') == ['a', 'b', 'c']
    assert comma_separated_list('US1') == ['US1']
    assert comma_separated_list('') == []
    assert comma_separated_list(None) == []


def test_validate_query_params_comma_separated_ids() -> None:
    query = QueryParams('ids=a,b&name=Frida')
    validated = validate_query_params(query, SampleQuery)
    assert validated.ids == ['a', 'b']
    assert validated.name == 'Frida'


def test_validate_query_params_scalar_field() -> None:
    query = QueryParams('name=Frida')
    validated = validate_query_params(query, SampleQuery)
    assert validated.name == 'Frida'
    assert validated.ids is None


def test_validate_query_params_rejects_unknown_fields() -> None:
    query = QueryParams('wrong_param=value')
    with pytest.raises(ValidationError):
        validate_query_params(query, SampleQuery)


def test_empty_query_mapping() -> None:
    mapping = EmptyQueryMapping()
    assert 'x' not in mapping
    assert mapping.get('x') is None
    assert mapping.get('x', 'default') == 'default'
    assert list(mapping) == []


def test_validate_query_params_empty_mapping() -> None:
    validated = validate_query_params(EmptyQueryMapping(), SampleQuery)
    assert validated.ids is None
    assert validated.name is None


def test_query_params_for_url_serializes_list_as_comma_separated() -> None:
    query = SampleQuery(ids=['a', 'b'], name='Frida')
    assert query_params_for_url(query)['ids'] == 'a,b'
