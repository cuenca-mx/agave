from typing import Optional

from cuenca_validations.types import QueryParams
from pydantic import BaseModel


class AccountQuery(QueryParams):
    name: Optional[str] = None
    user_id: Optional[str] = None
    is_active: Optional[bool] = None


class TransactionQuery(QueryParams):
    user_id: Optional[str] = None


class AccountRequest(BaseModel):
    name: str


class AccountUpdateRequest(BaseModel):
    name: str


class FileQuery(QueryParams):
    user_id: Optional[str] = None


class CardQuery(QueryParams):
    number: Optional[str] = None
