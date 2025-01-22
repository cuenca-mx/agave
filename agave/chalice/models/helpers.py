import uuid
from base64 import urlsafe_b64encode


# This function is used to generate an id composed of a
# list of fields in alphabetical order, for example if we want
# uuid_field_generic('AC', account_number='bla', user_id='ble')
# it will always generate the same id, because it is based on the arguments
def uuid_field_generic(prefix: str = '', **fields) -> str:
    sorted_text = ''.join(
        [
            item[1]
            for item in sorted(fields.items(), key=lambda x: x[0].lower())
        ]
    )
    uuid5 = uuid.uuid5(uuid.NAMESPACE_OID, sorted_text)
    return prefix + urlsafe_b64encode(uuid5.bytes).decode()[:-2]
