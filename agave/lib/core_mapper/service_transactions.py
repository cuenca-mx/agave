from cuenca_validations.typing import DictStrAny

from .types import CoreTransactionStatus, transaction_status_mapper


def mapper_service_providers(data: DictStrAny) -> DictStrAny:
    fields = data['fields']
    provider_key = fields[0]['service_provider_key'].replace('_barcode', '')
    categories = data.get('categories', [])
    model = dict(
        id=data['id'],
        created_at=data['created_at'],
        name=data['name'],
        provider_key=provider_key,
        categories=[category['name'] for category in categories],
    )
    return dict(service_providers=model)


def mapper_service_transactions(data: DictStrAny) -> DictStrAny:
    core_status = CoreTransactionStatus[data['status']]
    account = data.get('service_account')
    ledger = data.get('ledger_account')
    model = dict(
        id=data['id'],
        status=transaction_status_mapper[core_status],
        created_at=data['created_at'],
        amount=data['amount'],
    )
    if ledger:
        model['user_id'] = data['ledger_account']['user_id']
    if account:
        model = dict(
            **model,
            descriptor=f'Pago de servicio: {account["name"]}',
            account_number=account['account_number'],
            provider=account['service_field']['service_provider_id'],
        )
    return dict(bill_payments=model)
