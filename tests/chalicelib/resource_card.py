from chalice import ForbiddenError, Response
from cuenca_validations.types import CardStatus
from cuenca_validations.types.queries import CardQuery
from cuenca_validations.types.requests import CardUpdateRequest

from tests.chalicelib.model_card import Card as CardModel

from .base import app


@app.resource('/cards')
class Card:
    model = CardModel
    query_validator = CardQuery
    update_validator = CardUpdateRequest

    @staticmethod
    def update(card: CardModel, data: CardUpdateRequest):
        if card.status == CardStatus.deactivated:
            raise ForbiddenError('Invalid operation')

        for attr, val in data.dict().items():
            setattr(card, attr, val)
        card.save()
        return Response(card.to_dict(), status_code=200)
