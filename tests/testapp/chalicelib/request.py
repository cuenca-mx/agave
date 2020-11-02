from pydantic import BaseModel


class NameRequest(BaseModel):
    name: str
    key: str


class NameUpdate(BaseModel):
    name: str
