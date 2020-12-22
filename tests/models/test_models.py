from typing import Type, Union

import pytest

from agave.exc import ObjectDoesNotExist
from agave.models import mongo, redis
from agave.models.mongo.filters import generic_mongo_query
from agave.models.redis.filters import generic_redis_query
from examples.chalicelib.validators import AccountQuery

from ..models.test_base import TestModel, TestModelRedis

DbModel = Union[mongo.MongoModel, redis.RedisModel]
ModelBase = Union[TestModel, TestModelRedis]


def test_retrieve(db_model: Type[DbModel], account: DbModel) -> None:
    obj = db_model.retrieve(account.id)
    assert obj.id == account.id


def test_retrieve_not_found(db_model: Type[DbModel]) -> None:
    with pytest.raises(ObjectDoesNotExist):
        db_model.retrieve('unknown-id')


def test_retrieve_with_user_id_filter(
    db_model: Type[DbModel], account: DbModel, user_id: str
) -> None:
    obj = db_model.retrieve(account.id, user_id)
    assert obj.id == account.id
    assert obj.user_id == user_id


def test_retrieve_not_found_with_user_id_filter(
    db_model: Type[DbModel],
) -> None:
    with pytest.raises(ObjectDoesNotExist):
        db_model.retrieve('unknown-id', 'unknown-user-id')


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
    items = db_model.filter_limit(filters, limit)
    items = list(items)
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
    items = db_model.filter_limit(filters, limit)
    has_more = db_model.has_more(items, limit)
    assert has_more is True


@pytest.mark.parametrize(
    'model_base',
    ['mongo', 'redis'],
    indirect=True,
)
def test_hide_field_redis(model_base: Type[ModelBase]):
    model = model_base(id='12345', secret_field='secret')
    model_dict = model.dict()
    assert model_dict['secret_field'] == '********'
    assert model_dict['id'] == '12345'
