from fastapi.responses import JSONResponse as Response

from agave.core.filters import generic_query

from ...validators import CardQuery
from ...models import Card as CardModel
from .base import app


@app.resource('/cards')
class Card:
    model = CardModel
    query_validator = CardQuery
    get_query_filter = generic_query

    @staticmethod
    async def retrieve(card: CardModel) -> Response:
        data = card.to_dict()
        data['number'] = '*' * 16
        return Response(content=data)

    @staticmethod
    async def query(response: dict):
        for item in response['items']:
            item['number'] = '*' * 16
        return response
