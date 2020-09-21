import datetime as dt
from typing import Dict

from cuenca_validations.types import StrictTransferRequest, TransactionStatus
from mongoengine import DateTimeField, Document, IntField, StringField

from agave.models.helpers import EnumField, uuid_field


class Transfer(Document):
    id = StringField(primary_key=True, default=uuid_field('TR'))
    created_at = DateTimeField(default=dt.datetime.utcnow)
    account_number = StringField(required=True)
    recipient_name = StringField(required=True)
    amount = IntField(required=True)
    descriptor = StringField()
    idempotency_key = StringField(required=True)
    status: TransactionStatus = EnumField(
        TransactionStatus, default=TransactionStatus.created
    )

    def create(self, transfer_request: StrictTransferRequest) -> None:
        self.account_number = transfer_request.account_number
        self.recipient_name = transfer_request.recipient_name
        self.amount = transfer_request.amount
        self.descriptor = transfer_request.descriptor
        self.idempotency_key = transfer_request.idempotency_key

    def to_dict(self) -> Dict:
        """Returns a dictionary with data that represents a transfer request
        for Cuenca core

        Note:
            Since `reference_number` is an optional value
             `None` values are allowed
        """
        return dict(
            id=self.id,
            account_number=self.account_number,
            amount=self.amount,
            descriptor=self.descriptor,
            recipient_name=self.recipient_name,
        )
