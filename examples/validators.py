import datetime as dt
from typing import Annotated, Optional

from cuenca_validations.types import Metadata, QueryParams
from pydantic import BaseModel, SecretStr


class AccountQuery(QueryParams):
    name: Optional[str] = None
    user_id: Optional[str] = None
    platform_id: Optional[str] = None
    active: Optional[bool] = None


class TransactionQuery(QueryParams):
    user_id: Optional[str] = None


class BillerQuery(QueryParams):
    name: str


class UserQuery(QueryParams):
    platform_id: Optional[str] = None


class AccountRequest(BaseModel):
    name: str


class AccountResponse(BaseModel):
    id: str
    name: str
    user_id: str
    platform_id: str
    created_at: dt.datetime
    deactivated_at: Optional[dt.datetime] = None


class AccountUpdateRequest(BaseModel):
    name: str


class ApiKeyRequest(BaseModel):
    user: str
    password: Annotated[str, Metadata(sensitive=True)]
    short_secret: Annotated[str, Metadata(sensitive=True)]


class ApiKeyResponse(BaseModel):
    id: str
    secret: Annotated[str, Metadata(sensitive=True, log_chars=4)]
    user: str
    password: Annotated[str, Metadata(sensitive=True, log_chars=4)]
    user_id: str
    platform_id: str
    created_at: dt.datetime
    deactivated_at: Optional[dt.datetime] = None


class FileQuery(QueryParams):
    user_id: Optional[str] = None


class CardQuery(QueryParams):
    number: Optional[str] = None


class FileUploadValidator(BaseModel):
    file: bytes
    file_name: str


class UserUpdateRequest(BaseModel):
    name: str
