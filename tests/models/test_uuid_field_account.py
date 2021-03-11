from agave.models.helpers import uuid_field_account


def test_uuid_field_account():
    data = dict(account_number='123456789', bank_code='90464', user_id='US01')
    account_id = uuid_field_account(**data)
    assert 'AC' in account_id
    assert account_id == 'ACg4Jt4p6FUTKhIg12j2csQw'
