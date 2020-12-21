from typing import Type, Union

import pytest

from agave.exc import ObjectDoesNotExist
from agave.models import mongo, redis

DbModel = Union[mongo.MongoModel, redis.RedisModel]


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
