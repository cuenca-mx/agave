from typing import Dict

from chalice import Response

from agave.filters import generic_query

from ..models import Card as CardModel
from ..validators import CardQuery
from .base import app


@app.resource('/cards')
class Card:
    model = CardModel
    query_validator = CardQuery
    get_query_filter = generic_query

    @staticmethod
    def retrieve(card: CardModel) -> Response:
        data = card.to_dict()
        data['number'] = '*' * 16
        return Response(data)

    @staticmethod
    def query(response: Dict):
        for item in response['items']:
            item['number'] = '*' * 16
        return response
