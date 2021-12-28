from cuenca_validations.typing import DictStrAny

from .exc import NotRequiredModelError

STP_BANK_CODE = '90646'


def mapper_ledger_accounts(data: DictStrAny) -> DictStrAny:
    account_type = data['account_type']
    # Ignore hold an internal
    if account_type not in ['saving', 'default']:
        raise NotRequiredModelError
    model = dict(
        id=data['id'],
        created_at=data['created_at'],
        user_id=data['user_id'],
    )

    if clabe := data.get('_clabe'):
        model = dict(
            **model,
            bank_code=STP_BANK_CODE,
            account_number=clabe['clabe'],
        )
    if account_type == 'saving':
        collection = 'savings'
        model['balance'] = data['balance']
    else:
        collection = 'accounts'
        model['name'] = data['user']['name']
    return {collection: model}
