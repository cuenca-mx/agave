import re
from datetime import datetime as dt
from decimal import Decimal
from enum import Enum
from typing import ClassVar

import pytest
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
from agave.models.base import BaseModel


class Reference(Document, BaseModel):
    meta: ClassVar = {
        'collection': 'references',
    }


class EnumType(Enum):
    member = 'name'


class Embedded(EmbeddedDocument, BaseModel):
    name = StringField()


class TestModel(Document, BaseModel):
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


@pytest.fixture
def model():
    reference = Reference()
    reference.save()
    model = TestModel(
        embedded_list_field=[Embedded(name='')],
        lazzy_field=reference,
        lazzy_list_field=[reference],
    )
    model.save()
    model.reload()
    return model


def test_mongo_to_dict(model):
    assert not mongo_to_dict(None)
    model_dict = mongo_to_dict(model, exclude_fields=['str_field'])

    assert 'id' in model_dict
    assert 'date_time_field' in model_dict
    assert 'complex_date_time_field' in model_dict
    assert model_dict['int_field'] == 1
    assert model_dict['float_field'] == '1.1'
    assert model_dict['decimal_field'] == Decimal('1.2')
    assert model_dict['dict_field']['one'] == 1
    assert model_dict['enum_field'] == 'name'
    assert model_dict['boolean_field'] is True
    assert model_dict['list_field'] == ['42']
    assert model_dict['enum_list_field'] == ['name']
    assert model_dict['embedded_list_field'] == [{'name': ''}]
    assert model_dict['embedded_field'] == {}
    reference_reg = re.compile(r'\/references\/.{24}')
    assert reference_reg.match(model_dict['lazzy_field_uri'])
    assert len(model_dict['lazzy_list_field_uris']) == 1
    assert all(
        reference_reg.match(field)
        for field in model_dict['lazzy_list_field_uris']
    )
    assert model_dict['generic_lazzy_field_uri'] is None
