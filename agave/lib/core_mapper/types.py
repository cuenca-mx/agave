from enum import Enum

from cuenca_validations.types import TransactionStatus


class CoreTransactionStatus(str, Enum):
    created = 'created'
    failed = 'failed'
    submitted = 'submitted'
    succeeded = 'succeeded'
    transfer_to_default = 'transfer_to_default'
    return_to_origin = 'return_to_origin'
    suspect = 'suspect'
    completed = 'completed'
    duplicated = 'duplicated'
    pld_review = 'pld_review'


transaction_status_mapper = {
    CoreTransactionStatus.created: TransactionStatus.in_review,
    CoreTransactionStatus.failed: TransactionStatus.failed,
    CoreTransactionStatus.submitted: TransactionStatus.in_review,
    CoreTransactionStatus.succeeded: TransactionStatus.succeeded,
    CoreTransactionStatus.transfer_to_default: TransactionStatus.succeeded,
    CoreTransactionStatus.return_to_origin: TransactionStatus.failed,
    CoreTransactionStatus.suspect: TransactionStatus.in_review,
    CoreTransactionStatus.completed: TransactionStatus.succeeded,
    CoreTransactionStatus.duplicated: TransactionStatus.failed,
    CoreTransactionStatus.pld_review: TransactionStatus.in_review,
}
