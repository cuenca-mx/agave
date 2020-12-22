import datetime as dt
from typing import Generator, List, Type, Union

import pytest

from agave.models import mongo, redis
from examples.chalicelib.models import mongo_models, redis_models

from ..models.test_base import TestModel, TestModelRedis

DbModel = Union[mongo.MongoModel, redis.RedisModel]
ModelBase = Union[TestModel, TestModelRedis]


def pytest_generate_tests(metafunc):
    if "db_model" in metafunc.fixturenames:
        metafunc.parametrize(
            'db_model',
            [mongo_models.Account, redis_models.Account],
            indirect=['db_model'],
        )


@pytest.fixture
def db_model(request) -> Type[DbModel]:
    return request.param


@pytest.fixture
def model_base(request) -> Type[ModelBase]:
    if request.param == 'mongo':
        return TestModel
    else:
        return TestModelRedis


@pytest.fixture
def accounts(
    db_model: Type[DbModel], user_id: str, another_user_id: str
) -> Generator[List[DbModel], None, None]:
    accs = [
        db_model(
            name='Frida Kahlo',
            user_id=user_id,
            created_at=dt.datetime(2020, 1, 1),
        ),
        db_model(
            name='Sor Juana Inés',
            user_id=user_id,
            created_at=dt.datetime(2020, 2, 1),
        ),
        db_model(
            name='Leona Vicario',
            user_id=user_id,
            created_at=dt.datetime(2020, 3, 1),
        ),
        db_model(
            name='Remedios Varo',
            user_id=another_user_id,
            created_at=dt.datetime(2020, 4, 1),
        ),
    ]

    for acc in accs:
        acc.save()
    yield accs
    for acc in accs:
        acc.delete()


@pytest.fixture
def account(accounts: List[DbModel]) -> Generator[DbModel, None, None]:
    yield accounts[0]


@pytest.fixture
def another_account(
    accounts: List[DbModel],
) -> Generator[DbModel, None, None]:
    yield accounts[-1]
