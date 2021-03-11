import uuid
from base64 import urlsafe_b64encode


def uuid_field(prefix: str = ''):
    def base64_uuid_func() -> str:
        return prefix + urlsafe_b64encode(uuid.uuid4().bytes).decode()[:-2]

    return base64_uuid_func


def uuid_field_account(
    account_number: str, bank_code: str, user_id: str
) -> str:
    text = f"{bank_code}{account_number}{user_id}"
    uuid5 = uuid.uuid5(uuid.NAMESPACE_DNS, text)
    return 'AC' + urlsafe_b64encode(uuid5.bytes).decode()[:-2]
