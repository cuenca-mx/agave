import uuid
from base64 import urlsafe_b64encode


def uuid_field(prefix: str = ''):
    def base64_uuid_func() -> str:
        return prefix + urlsafe_b64encode(uuid.uuid4().bytes).decode()[:-2]

    return base64_uuid_func
