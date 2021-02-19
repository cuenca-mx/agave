# mypy: ignore-errors
from enum import Enum

from bson import DBRef
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
)

from .enum_field import EnumField


def mongo_to_dict(obj, exclude_fields: list = None) -> dict:
    """
    from: https://gist.github.com/jason-w/4969476
    """
    return_data = {}

    if obj is None:
        return return_data

    if isinstance(obj, Document):
        return_data['id'] = str(obj.id)

    if exclude_fields is None:
        exclude_fields = []

    for field_name in obj._fields:
        if field_name in exclude_fields:
            continue

        if field_name == 'id':
            continue
        data = obj._data[field_name]

        if isinstance(obj._fields[field_name], ListField):
            field_name = (
                f'{field_name}_uris'
                if isinstance(
                    obj._fields[field_name].field, LazyReferenceField
                )
                else field_name
            )
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
        elif field_name == 'funding_instrument':
            mapper = {
                'BA': '/accounts/',
                'CA': '/cards/',
                'SP': '/service_providers/',
            }
            return_data[f'{field_name}_uri'] = f'{mapper[data[:2]]}{data}'
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
        elif isinstance(item, DBRef):  # pragma: no cover
            return_data.append(f'/{item._DBRef__collection}/{item.id}')
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
    elif rv is FloatField:  # pragma: no cover
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
