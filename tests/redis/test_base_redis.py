import pytest
from rom import util

from agave.models.helpers import uuid_field
from agave.repositories import BaseModel, String


class TestModel(BaseModel):
    id = String(
        default=uuid_field('US'),
        required=True,
        unique=True,
        index=True,
        keygen=util.IDENTITY,
    )
    secret_field = String()

    _hidden = ['secret_field']


@pytest.mark.usefixtures('client')
def test_hide_field():
    model = TestModel(id='12345', secret_field='secret')
    model_dict = model.dict()
    assert model_dict['secret_field'] == '********'
    assert model_dict['id'] == '12345'
