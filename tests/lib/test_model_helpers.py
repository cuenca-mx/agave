from datetime import datetime as dt
from enum import Enum

from mongoengine import (
    BooleanField,
    ComplexDateTimeField,
    DateTimeField,
    DecimalField,
    DictField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    GenericLazyReferenceField,
    IntField,
    LazyReferenceField,
    ListField,
    StringField,
)

from agave.lib.mongoengine.enum_field import EnumField
from agave.lib.mongoengine.model_helpers import mongo_to_dict


class Reference(Document):
    pass


class EnumType(Enum):
    member = 'name'


class Embedded(EmbeddedDocument):
    name = StringField()


class TestModel(Document):
    str_field = StringField()
    int_field = IntField(default=1)
    float_field = FloatField(default=1.1)
    decimal_field = DecimalField(default=1.2)
    boolean_field = BooleanField(default=True)
    dict_field = DictField(default=dict(one=1, two=2))
    date_time_field = DateTimeField(default=dt.now)
    complex_date_time_field = ComplexDateTimeField(default=dt.now)
    enum_field = EnumField(EnumType, default=EnumType.member)
    list_field = ListField(IntField(), default=lambda: [42])
    enum_list_field = ListField(EnumField(EnumType), default=[EnumType.member])
    embedded_list_field = ListField(EmbeddedDocumentField(Embedded))
    embedded_field = EmbeddedDocumentField(Embedded)
    lazzy_field = LazyReferenceField(Reference)
    lazzy_list_field = ListField(LazyReferenceField(Reference))
    generic_lazzy_field = GenericLazyReferenceField()

    __test__ = False


def test_mongo_to_dict():
    assert not mongo_to_dict(None)
    reference = Reference()
    reference.save()
    model = TestModel(embedded_list_field=[Embedded(name='')],
                      lazzy_list_field=[reference])
    model.save()

    model_dict = mongo_to_dict(model, exclude_fields=['str_field'])
    assert 'id' in model_dict
    assert model_dict['enum_field'] == 'name'
