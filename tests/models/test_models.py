from typing import Type, Union

import pytest

from agave.exc import DoesNotExist
from agave.models import mongo, redis
from agave.models.mongo.filters import generic_mongo_query
from agave.models.redis.filters import generic_redis_query
from examples.chalicelib.validators import AccountQuery

DbModel = Union[mongo.MongoModel, redis.RedisModel]


def test_retrieve(db_model: Type[DbModel], account: DbModel) -> None:
    obj = db_model.retrieve(account.id)
    assert obj.id == account.id


def test_retrieve_not_found(db_model: Type[DbModel]) -> None:
    with pytest.raises(DoesNotExist):
        db_model.retrieve('unknown-id')


def test_retrieve_with_user_id_filter(
    db_model: Type[DbModel], account: DbModel, user_id: str
) -> None:
    obj = db_model.retrieve(account.id, user_id=user_id)
    assert obj.id == account.id
    assert obj.user_id == user_id


def test_retrieve_not_found_with_user_id_filter(
    db_model: Type[DbModel],
) -> None:
    with pytest.raises(DoesNotExist):
        db_model.retrieve('unknown-id', user_id='unknown-user-id')


@pytest.mark.usefixtures('accounts')
def test_query_count(db_model: Type[DbModel]):
    params = dict(count=1, name='Frida Kahlo')
    query_params = AccountQuery(**params)
    if issubclass(db_model, mongo.MongoModel):
        filters = generic_mongo_query(query_params)
    else:
        filters = generic_redis_query(query_params)
    count = db_model.count(filters)
    assert count == 1


@pytest.mark.usefixtures('accounts')
def test_query_all_with_limit(db_model: Type[DbModel]):
    limit = 2
    params = dict(limit=limit)
    query_params = AccountQuery(**params)
    if issubclass(db_model, mongo.MongoModel):
        filters = generic_mongo_query(query_params)
    else:
        filters = generic_redis_query(query_params)
    items = db_model.all(filters, limit=limit)
    assert len(items) == 2


@pytest.mark.usefixtures('accounts')
def test_query_all_resource(db_model: Type[DbModel]):
    params = dict(page_size=2)
    limit = 2
    query_params = AccountQuery(**params)
    if issubclass(db_model, mongo.MongoModel):
        filters = generic_mongo_query(query_params)
    else:
        filters = generic_redis_query(query_params)
    items, has_more = db_model.all(filters, limit=limit)
    assert has_more is True


def test_hide_field_redis(db_model: Type[DbModel]):
    model = db_model(
        id='12345', secret_field='secret', name='frida', user_id='w72638'
    )
    model_dict = model.dict()
    assert model_dict['secret_field'] == '********'
    assert model_dict['id'] == '12345'
