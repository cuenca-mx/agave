import datetime as dt

from cuenca_validations.types import QueryParams

from agave.collections.mongo.filters import generic_query


def test_generic_query() -> None:
    params = QueryParams(created_before=dt.datetime.utcnow().isoformat())
    query = generic_query(params)
    representation = repr(query)
    assert 'created_at__lt' in representation
    assert 'created_before' not in representation
    assert 'created_after' not in representation
    assert 'active' not in representation
    assert 'limit' not in representation
    assert 'page_size' not in representation
    assert 'key' not in representation
    assert 'user' not in representation


def test_generic_query_merge_delimiters() -> None:
    params = QueryParams(count=True)
    query = generic_query(params, **dict(user_id='US123'))
    representation = repr(query)
    assert 'count' not in representation
    assert 'user_id' in representation
