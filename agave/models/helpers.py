# mypy: ignore-errors
import datetime as dt
import uuid
from base64 import urlsafe_b64encode
from enum import Enum
from typing import Dict, List, NamedTuple, Type

from blinker.base import NamedSignal
from bson import SON, DBRef
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
    signals,
)
from mongoengine.base import BaseField


def uuid_field(prefix: str = ''):
    def base64_uuid_func() -> str:
        return prefix + urlsafe_b64encode(uuid.uuid4().bytes).decode()[:-2]

    return base64_uuid_func


class EnumField(BaseField):
    """
    https://github.com/MongoEngine/extras-mongoengine/blob/master/
    extras_mongoengine/fields.py
    A class to register Enum type (from the package enum34) into mongo
    :param choices: must be of :class:`enum.Enum`: type
        and will be used as possible choices
    """

    def __init__(self, enum: Type[Enum], *args, **kwargs):
        self.enum = enum
        kwargs['choices'] = [choice for choice in enum]
        super(EnumField, self).__init__(*args, **kwargs)

    def __get_value(self, enum: Enum) -> str:
        return enum.value if hasattr(enum, 'value') else enum

    def to_python(self, value: Enum) -> Enum:
        return self.enum(super(EnumField, self).to_python(value))

    def to_mongo(self, value: Enum) -> str:
        return self.__get_value(value)

    def prepare_query_value(self, op, value: Enum) -> str:
        return super(EnumField, self).prepare_query_value(
            op, self.__get_value(value)
        )

    def validate(self, value: Enum) -> Enum:
        return super(EnumField, self).validate(self.__get_value(value))

    def _validate(self, value: Enum, **kwargs) -> Enum:
        return super(EnumField, self)._validate(
            self.enum(self.__get_value(value)), **kwargs
        )


class MapEntrie(NamedTuple):
    ids: List[str]
    models: List[str]


class DynamicLazyReferenceField(GenericLazyReferenceField):
    mapper: Dict
    models: Dict[str, Document]

    mapper_ids = (
        MapEntrie(ids=['TR', 'SP', 'LT'], models=['Deposit', 'Transfer']),
        MapEntrie(ids=['CD'], models=['Deposit']),
        MapEntrie(ids=['ST'], models=['BillPayment']),
        MapEntrie(ids=['CT'], models=['CardTransaction']),
        MapEntrie(ids=['SW'], models=['WhatsappTransfer']),
        MapEntrie(ids=['CO', 'PA'], models=['Commission']),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.models = {model._class_name: model for model in kwargs['choices']}
        self.mapper = kwargs['mapper'] if 'mapper' in kwargs else {}

    def __set__(self, instance, value):
        if not value or '_ref' in value:
            return super().__set__(instance, value)

        model_names = next(
            (data.models for data in self.mapper_ids if value[:2] in data.ids),
            [],
        )

        model = next(
            (
                self.models[model_name]
                for model_name, enums in self.mapper.items()
                if instance._data['type'] in enums and len(model_names) > 1
            ),
            self.models[model_names[0]] if model_names else None,
        )
        document = None
        if isinstance(value, str) and model:
            collection = model._get_collection_name()
            ref = DBRef(collection, value)
            document = SON((("_cls", model._class_name), ("_ref", ref)))

        return super().__set__(instance, document)


def mongo_to_dict(obj, exclude_fields: list = None) -> dict:
    """
    from: https://gist.github.com/jason-w/4969476
    """
    return_data = {}

    if obj is None:
        return return_data

    if isinstance(obj, Document):
        return_data['id'] = str(obj.id)

    for field_name in obj._fields:

        if field_name in exclude_fields:
            continue

        if field_name == 'id':
            continue

        data = obj._data[field_name]
        if isinstance(obj._fields[field_name], ListField):
            return_data[field_name] = list_field_to_dict(data)
        elif isinstance(obj._fields[field_name], EmbeddedDocumentField):
            return_data[field_name] = mongo_to_dict(data, [])
        elif isinstance(obj._fields[field_name], DictField):
            return_data[field_name] = data
        elif isinstance(obj._fields[field_name], EnumField):
            return_data[field_name] = data.value if data else None
        elif isinstance(obj._fields[field_name], LazyReferenceField):
            return_data[f'{field_name}_uri'] = (
                f'/{data._DBRef__collection}/{data.id}' if data else None
            )
        elif isinstance(obj._fields[field_name], GenericLazyReferenceField):
            return_data[f'{field_name}_uri'] = (
                f'/{data["_ref"]._DBRef__collection}/{data["_ref"].id}'
                if data
                else None
            )
        else:
            return_data[field_name] = mongo_to_python_type(
                obj._fields[field_name], data
            )

    return return_data


def list_field_to_dict(list_field: list) -> list:
    return_data = []

    for item in list_field:
        if isinstance(item, EmbeddedDocument):
            return_data.append(mongo_to_dict(item))
        elif isinstance(item, Enum):
            return_data.append(item.value)
        else:
            return_data.append(mongo_to_python_type(item, item))

    return return_data


def mongo_to_python_type(field, data):
    rv = None
    field_type = type(field)
    if data is None:
        rv = None
    elif field_type is DateTimeField:
        rv = data.isoformat()
    elif field_type is ComplexDateTimeField:
        rv = field.to_python(data).isoformat()
    elif rv is FloatField:
        rv = float(data)
    elif field_type is IntField:
        rv = int(data)
    elif field_type is BooleanField:
        rv = bool(data)
    elif field_type is DecimalField:
        rv = data
    else:
        rv = str(data)

    return rv


def handler(event: NamedSignal):
    """
    http://docs.mongoengine.org/guide/signals.html?highlight=update
    Signal decorator to allow use of callback functions as class
    decorators
    """

    def decorator(fn: ()):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls

        fn.apply = apply
        return fn

    return decorator


@handler(signals.pre_save)
def updated_at(_, document):
    document.updated_at = dt.datetime.utcnow()
