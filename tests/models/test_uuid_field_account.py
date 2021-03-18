import uuid
from base64 import urlsafe_b64encode

from agave.models.helpers import uuid_field_generic


def test_uuid_field_generic():
    values_asc = dict(
        account_number='123456789', bank_code='90464', user_id='US01'
    )
    generic_asc = uuid_field_generic('AC', **values_asc)

    uuid5 = uuid.uuid5(uuid.NAMESPACE_OID, '12345678990464US01')
    assert generic_asc == 'AC' + urlsafe_b64encode(uuid5.bytes).decode()[:-2]

    values_desc = dict(
        user_id='US01', bank_code='90464', account_number='123456789'
    )
    generic_desc = uuid_field_generic('AC', **values_desc)

    assert generic_asc == generic_desc
