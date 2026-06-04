import datetime as dt

from cuenca_validations.types import QueryParams

from agave.core.filters import generic_query


def test_generic_query_before():
    params = QueryParams(created_before=dt.datetime.utcnow().isoformat())
    query = generic_query(params)
    assert "created_at__lt" in repr(query)
    assert "user" not in repr(query)


def test_generic_query_after():
    params = QueryParams(created_after=dt.datetime.utcnow().isoformat())
    query = generic_query(params)
    assert "created_at__gt" in repr(query)
    assert "user" not in repr(query)


def test_generic_query_filters_by_ids_comma_separated_string() -> None:
    params = QueryParams.model_construct(ids='US1,US2')
    query = generic_query(params)
    assert 'id__in' in repr(query)
    assert 'US1' in repr(query)
    assert 'US2' in repr(query)


def test_generic_query_empty_ids_string() -> None:
    params = QueryParams.model_construct(ids='')
    query = generic_query(params)
    assert 'id__in' not in repr(query)


def test_generic_query_excludes_count_field() -> None:
    params = QueryParams.model_construct(count=True)
    query = generic_query(params)
    assert 'count' not in repr(query)
