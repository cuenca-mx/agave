from fastapi.requests import Request
from fastapi.responses import JSONResponse as Response

from ...models import Jwt as JwtModel
from .base import app


@app.resource('/token')
class Jwt:
    model = JwtModel

    @staticmethod
    async def create(request: Request) -> Response:
        return Response(content={}, status_code=201)
