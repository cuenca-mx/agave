import datetime as dt

from fastapi import Request
from fastapi.responses import JSONResponse as Response

from agave.core.filters import generic_query

from ...models import ApiKey as ApiKeyModel
from ...validators import ApiKeyRequest, ApiKeyResponse
from .base import app


@app.resource('/api_keys')
class ApiKey:
    model = ApiKeyModel
    response_model = ApiKeyResponse

    @staticmethod
    async def create(request: ApiKeyRequest) -> Response:
        ak = ApiKeyModel(
            user=request.user,
            password=request.password,
            user_id=app.current_user_id,
            platform_id=app.current_platform_id,
            secret='My-super-secret-key',
            another_field='12345678',
        )
        await ak.async_save()

        return Response(ak.to_dict(), status_code=201)
