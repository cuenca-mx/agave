import datetime as dt
from io import BytesIO

from typing import Tuple
from chalice import NotFoundError, Response
from mongoengine import DoesNotExist

from agave.filters import generic_query

from ..models import File as FileModel
from ..validators import FileQuery
from .base import app


@app.resource('/files')
class File:
    model = FileModel
    query_validator = FileQuery
    get_query_filter = generic_query

    @classmethod
    def download(cls, data: FileModel) -> Tuple[BytesIO, str]:
        mimetype = app.current_request.headers.get('accept')
        return BytesIO(bytes('Hello', 'utf-8')), mimetype
