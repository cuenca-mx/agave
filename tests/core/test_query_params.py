from typing import Optional, cast

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError
from starlette.datastructures import QueryParams

from agave.core.query_params import (
    ParseQsQueryMapping,
    QueryParamMapping,
    build_query_dict,
    validate_query_params,
)


class SampleQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ids: Optional[list[str]] = None
    name: Optional[str] = None
    active: Optional[bool] = None


def test_build_query_dict_repeated_ids() -> None:
    query = cast(QueryParamMapping, QueryParams('ids=US1&ids=US2&active=true'))
    params = build_query_dict(query, SampleQuery)
    assert params == {'ids': ['US1', 'US2'], 'active': 'true'}


def test_build_query_dict_single_id() -> None:
    query = cast(QueryParamMapping, QueryParams('ids=US1'))
    params = build_query_dict(query, SampleQuery)
    assert params == {'ids': ['US1']}


def test_build_query_dict_unknown_param_for_extra_forbid() -> None:
    query = cast(QueryParamMapping, QueryParams('wrong_param=value'))
    params = build_query_dict(query, SampleQuery)
    assert params == {'wrong_param': 'value'}


def test_validate_query_params_list_fields() -> None:
    query = cast(QueryParamMapping, QueryParams('ids=a&ids=b&name=Frida'))
    validated = validate_query_params(query, SampleQuery)
    assert validated.ids == ['a', 'b']
    assert validated.name == 'Frida'


def test_validate_query_params_rejects_invalid_list() -> None:
    # Starlette last-value semantics without getlist would pass a string;
    # validate_query_params must still produce a list for list fields.
    query = cast(QueryParamMapping, QueryParams('ids=a&ids=b'))
    validated = validate_query_params(query, SampleQuery)
    assert validated.ids == ['a', 'b']


def test_parse_qs_query_mapping() -> None:
    mapping = ParseQsQueryMapping('ids=US1&ids=US2&name=test')
    assert mapping.getlist('ids') == ['US1', 'US2']
    assert mapping.get('name') == 'test'
    assert 'missing' not in mapping


def test_validate_query_params_parse_qs_mapping() -> None:
    mapping = ParseQsQueryMapping('ids=x&ids=y')
    validated = validate_query_params(mapping, SampleQuery)
    assert validated.ids == ['x', 'y']


def test_old_unpack_pattern_would_fail_validation() -> None:
    query = QueryParams('ids=US1&ids=US2')
    with pytest.raises(ValidationError):
        SampleQuery(**dict(query))  # type: ignore[arg-type]


def test_validate_query_params_rejects_unknown_fields() -> None:
    query = cast(QueryParamMapping, QueryParams('wrong_param=value'))
    with pytest.raises(ValidationError):
        validate_query_params(query, SampleQuery)
