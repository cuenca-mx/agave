from cuenca_validations.types import QueryParams, TransactionQuery
from mongoengine import Q


def generic_query(query: QueryParams) -> Q:
    filters = Q()
    if query.user_id:
        filters = filters & Q(user_id=query.user_id)
    if query.created_before:
        filters = filters & Q(created_at__lt=query.created_before)
    if query.created_after:
        filters = filters & Q(created_at__gt=query.created_after)
    return filters


def transaction_query(query: TransactionQuery) -> Q:
    filters = generic_query(query)
    if query.status:
        filters = filters & Q(status=query.status)
    return filters
