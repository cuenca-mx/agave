from mongoengine import Document, StringField

from agave.models import BaseModel


class TestModel(BaseModel, Document):
    id = StringField()
    secret_field = StringField()

    _hidden = ['secret_field']


def test_hide_field():
    model = TestModel(id='12345', secret_field='secret')
    model_dict = model.to_dict()
    assert model_dict['secret_field'] == '********'
    assert model_dict['id'] == '12345'
