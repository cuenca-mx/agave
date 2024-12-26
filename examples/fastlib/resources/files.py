from io import BytesIO

from agave.core.filters import generic_query
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse as Response

from ..models import File as FileModel
from ..validators import FileQuery, FileUploadValidator
from .base import app


def save_file_to_disk(file: bytes, name: str) -> None:
    with open(name, 'wb') as out_file:
        out_file.write(file)


@app.resource('/files')
class File:
    model = FileModel
    query_validator = FileQuery
    upload_validator = FileUploadValidator
    get_query_filter = generic_query

    @classmethod
    async def download(cls, data: FileModel) -> BytesIO:
        return BytesIO(bytes('Hello', 'utf-8'))

    @classmethod
    async def upload(
        cls, request: FileUploadValidator, background_tasks: BackgroundTasks
    ) -> Response:
        file = request.file
        name = request.file_name
        background_tasks.add_task(save_file_to_disk, file=file, name=name)
        file = FileModel(name=name, user_id='US01')
        await file.async_save()
        return Response(content=file.to_dict(), status_code=201)
