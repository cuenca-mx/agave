from typing import Optional

import pytest
from cuenca_validations.types import QueryParams as CuencaQueryParams
from pydantic import BaseModel, ConfigDict, ValidationError
from starlette.datastructures import QueryParams

from agave.core.query_params import (
    EmptyQueryMapping,
    build_query_dict,
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


def test_query_params_for_url_skips_none_list_fields() -> None:
    query = SampleQuery(name='Frida')
    params = query_params_for_url(query)
    assert params['name'] == 'Frida'
    assert params.get('ids') is None


class _ListQueryMapping:
    def __init__(self, values: dict[str, object]) -> None:
        self._values = values

    def __iter__(self):
        return iter(self._values)

    def get(self, key: str, default: object = None) -> object:
        return self._values.get(key, default)


def test_build_query_dict_list_from_non_string_value() -> None:
    mapping = _ListQueryMapping({'ids': ['a', 'b']})
    params = build_query_dict(mapping, SampleQuery)
    assert params['ids'] == ['a', 'b']


def test_build_query_dict_ids_stays_string() -> None:
    class StrIdsQuery(BaseModel):
        ids: Optional[str] = None

    mapping = _ListQueryMapping({'ids': 'US1,US2'})
    params = build_query_dict(mapping, StrIdsQuery)
    assert params['ids'] == 'US1,US2'


def test_build_query_dict_skips_none_str_ids_value() -> None:
    class StrIdsQuery(BaseModel):
        ids: Optional[str] = None

    mapping = _ListQueryMapping({'ids': None})
    params = build_query_dict(mapping, StrIdsQuery)
    assert 'ids' not in params


def test_build_query_dict_skips_none_list_value() -> None:
    mapping = _ListQueryMapping({'ids': None})
    params = build_query_dict(mapping, SampleQuery)
    assert 'ids' not in params


class _ExtraFieldQuery(BaseModel):
    model_config = ConfigDict(extra='allow')

    name: Optional[str] = None


def test_build_query_dict_unknown_field() -> None:
    mapping = _ListQueryMapping({'unknown': 'value', 'name': 'Frida'})
    params = build_query_dict(mapping, _ExtraFieldQuery)
    assert params['unknown'] == 'value'
    assert params['name'] == 'Frida'


def test_validate_query_params_cuenca_ids_stays_string() -> None:
    validated = validate_query_params(
        QueryParams('ids=US1,US2'), CuencaQueryParams
    )
    assert validated.ids == 'US1,US2'
