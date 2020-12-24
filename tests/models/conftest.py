import datetime as dt
from typing import Generator, List, Type, Union

import pytest

from agave.models import mongo, redis

DbModel = Union[mongo.MongoModel, redis.RedisModel]


@pytest.fixture
def db_model(request) -> Type[DbModel]:
    return request.param


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
