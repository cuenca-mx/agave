import datetime as dt

import pytest
from mongoengine import Document

from agave.lib.mongoengine.event_handlers import updated_at


@updated_at.apply
class TestModel(Document):
    ...


@pytest.mark.freeze_time('2020-10-10')
def test_attach_updated_at_field():
    model = TestModel()
    with pytest.raises(AttributeError):
        getattr(model, 'updated_at')

    model.save()
    assert type(model.updated_at) is dt.datetime
    assert model.updated_at == dt.datetime(2020, 10, 10)
