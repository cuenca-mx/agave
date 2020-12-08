from enum import Enum

from mongoengine import Document

from agave.lib.mongoengine.enum_field import EnumField


class EnumType(Enum):
    member = 'name'


class TestModel(Document):
    enum_field = EnumField(EnumType)
    __test__ = False


def test_prepare_query_value():
    model = TestModel(enum_field=EnumType.member)
    model.save()
    assert type(model.enum_field) is EnumType
