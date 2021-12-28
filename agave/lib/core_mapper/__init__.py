__all__ = [
    'core_mapper',
    'mapper_ledger_accounts',
    'mapper_service_providers',
    'mapper_service_transactions',
]
from .ledger_accounts import mapper_ledger_accounts
from .service_transactions import (
    mapper_service_providers,
    mapper_service_transactions,
)

# All mapper functions has to return a dictionary with these key, value
# key -> oaxaca collection
# value -> oaxaca data
core_mapper = dict(
    service_providers=mapper_service_providers,
    service_transactions=mapper_service_transactions,
    ledger_accounts=mapper_ledger_accounts,
)
