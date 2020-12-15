from mongoengine import Document, StringField

from agave.models.mongo import MongoModel


class TestModel(MongoModel, Document):
    id = StringField()
    secret_field = StringField()
    __test__ = False
    _hidden = ['secret_field']


def test_hide_field():
    model = TestModel(id='12345', secret_field='secret')
    model_dict = model.dict()
    assert model_dict['secret_field'] == '********'
    assert model_dict['id'] == '12345'
