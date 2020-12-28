import datetime as dt
from typing import Callable, List, Type, Union

import pytest

from agave.exc import DoesNotExist
from agave.models import mongo, redis
from examples.chalicelib.models import mongo_models, redis_models
from examples.chalicelib.validators import AccountQuery

DbModel = Union[mongo.MongoModel, redis.RedisModel]
models = [mongo_models.Account, redis_models.Account]
generic_query_funcs = [
    mongo.filters.generic_mongo_query,
    redis.filters.generic_redis_query,
]


@pytest.mark.parametrize('db_model', models, indirect=['db_model'])
def test_retrieve(db_model: Type[DbModel], account: DbModel) -> None:
    obj = db_model.retrieve(account.id)
    assert obj.id == account.id


@pytest.mark.parametrize('db_model', models, indirect=['db_model'])
def test_retrieve_not_found(db_model: Type[DbModel]) -> None:
    with pytest.raises(DoesNotExist):
        db_model.retrieve('unknown-id')


@pytest.mark.parametrize('db_model', models, indirect=['db_model'])
def test_retrieve_with_user_id_filter(
    db_model: Type[DbModel], account: DbModel, user_id: str
) -> None:
    obj = db_model.retrieve(account.id, user_id=user_id)
    assert obj.id == account.id
    assert obj.user_id == user_id


@pytest.mark.parametrize('db_model', models, indirect=['db_model'])
def test_retrieve_not_found_with_user_id_filter(
    db_model: Type[DbModel], account: DbModel, another_user_id
) -> None:
    with pytest.raises(DoesNotExist):
        db_model.retrieve(account.id, user_id=another_user_id)


@pytest.mark.parametrize(
    'db_model,generic_query_func',
    zip(models, generic_query_funcs),
    indirect=['db_model'],
)
def test_query_count(
    db_model: Type[DbModel],
    generic_query_func: Callable,
    accounts: List[DbModel],
    user_id: str,
) -> None:
    query_params = AccountQuery(count=1, name='Frida Kahlo')
    assert db_model.count(generic_query_func(query_params)) == 1

    query_params = AccountQuery(count=1)
    assert db_model.count(generic_query_func(query_params)) == len(accounts)

    query_params = AccountQuery(count=1, user_id=user_id)
    assert db_model.count(generic_query_func(query_params)) == len(
        [acc for acc in accounts if acc.user_id == user_id]
    )


@pytest.mark.parametrize(
    'db_model,generic_query_func',
    zip(models, generic_query_funcs),
    indirect=['db_model'],
)
@pytest.mark.usefixtures('accounts')
def test_query_all_with_limit(
    db_model: Type[DbModel], generic_query_func: Callable
) -> None:
    limit = 2
    query_params = AccountQuery(limit=limit)
    items, has_more = db_model.all(
        generic_query_func(query_params), limit=limit, wants_more=False
    )
    assert not has_more
    assert len(items) == limit


@pytest.mark.parametrize(
    'db_model,generic_query_func',
    zip(models, generic_query_funcs),
    indirect=['db_model'],
)
@pytest.mark.usefixtures('accounts')
def test_query_all_resource(
    db_model: Type[DbModel], generic_query_func: Callable
) -> None:
    limit = 3
    query_params = AccountQuery(page_size=limit)
    items, has_more = db_model.all(
        generic_query_func(query_params), limit=limit, wants_more=True
    )
    assert has_more
    assert len(items) == limit

    query_params = AccountQuery(
        page_size=limit, created_before=items[-1].created_at
    )
    items, has_more = db_model.all(
        generic_query_func(query_params), limit=limit, wants_more=True
    )
    assert not has_more
    assert len(items) == 1


@pytest.mark.parametrize('db_model', models, indirect=['db_model'])
def test_to_dict(db_model: Type[DbModel]) -> None:
    now = dt.datetime.utcnow()
    expected = dict(
        id='12345',
        name='frida',
        user_id='w72638',
        secret_field='********',
    )
    model = db_model(
        id='12345',
        name='frida',
        user_id='w72638',
        secret_field='secret',
        created_at=now,
    )
    model.save()
    model_dict = model.dict()
    assert all(model_dict[key] == val for key, val in expected.items())
