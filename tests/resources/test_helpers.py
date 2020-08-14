import datetime as dt

from cuenca_validations.types import QueryParams, TransactionQuery

from mezcal.resource.helpers import generic_query, transaction_query


def test_transaction_query():
    params = TransactionQuery(user_id='user', status='pending')
    query = transaction_query(params)
    assert "{'user_id': 'user'}" in repr(query)
    assert "{'status': 'pending'}" in repr(query)


def test_generic_query():
    params = QueryParams(created_before=dt.datetime.utcnow().isoformat())
    query = generic_query(params)
    assert "created_at__lt" in repr(query)
    assert "user" not in repr(query)
