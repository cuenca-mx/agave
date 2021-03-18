from agave.models.helpers import uuid_field_generic


def test_uuid_field_generic():
    values_asc = dict(
        account_number='123456789', bank_code='90464', user_id='US01'
    )
    generic_asc = uuid_field_generic('AC', **values_asc)

    values_desc = dict(
        user_id='US01', bank_code='90464', account_number='123456789'
    )
    generic_desc = uuid_field_generic('AC', **values_desc)

    assert generic_asc == generic_desc
