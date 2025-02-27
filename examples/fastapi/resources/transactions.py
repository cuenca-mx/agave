from fastapi.responses import JSONResponse as Response

from ...models.transactions import Transaction as TransactionModel
from .base import app


@app.resource('/transactions')
class Transaction:
    model = TransactionModel

    @staticmethod
    async def create() -> Response:
        return Response(content={}, status_code=201)
