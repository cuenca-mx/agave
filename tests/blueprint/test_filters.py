import datetime as dt

from cuenca_validations.types import QueryParams

from agave.filters import generic_query


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
