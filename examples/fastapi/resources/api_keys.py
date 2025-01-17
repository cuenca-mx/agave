import datetime as dt

from fastapi import Request
from fastapi.responses import JSONResponse as Response

from agave.core.filters import generic_query

from ...validators import ApiKeyRequest, ApiKeyResponse
from ..models import ApiKey as ApiKeyModel
from .base import app


@app.resource('/api_keys')
class ApiKey:
    model = ApiKeyModel
    response_model = ApiKeyResponse

    @staticmethod
    async def create(request: ApiKeyRequest) -> Response:
        ak = ApiKeyModel(
            user=request.user,
            password=request.password.get_secret_value(),
            user_id=app.current_user_id,
            platform_id=app.current_platform_id,
            secret='My-super-secret-key',
        )
        await ak.async_save()

        return Response(ak.to_dict(), status_code=201)
