import pytest

from agave.lib.core_mapper import (
    mapper_ledger_accounts,
    mapper_service_providers,
    mapper_service_transactions,
)
from agave.lib.core_mapper.exc import NotRequiredModelError


def test_mapper_service_providers_insert(service_provider_data):
    expected = {
        'id': 'SP-01',
        'created_at': '2021-11-17T13:15:29.832299+00:00',
        'name': 'Axtel',
        'provider_key': 'internet_axtel',
        'categories': ['cable', 'internet'],
    }
    data = mapper_service_providers(service_provider_data)
    assert data['service_providers'] == expected


def test_service_transaction_insert(service_transaction_data):
    expected = {
        'id': 'ST-01',
        'created_at': '2021-11-17T14:43:10.068104+00:00',
        'user_id': 'US1NlTaZwK3FubOhXNC9Vb8Y',
        'amount': 20000,
        'descriptor': 'Pago de servicio: CFE',
        'account_number': '0987654321233458',
        'provider': 'SP-01',
        'status': 'in_review',
    }
    data = mapper_service_transactions(service_transaction_data)
    assert data['bill_payments'] == expected


def test_service_transaction_update(service_transaction_data):
    service_transaction_data.pop('ledger_account')
    service_transaction_data.pop('service_account')
    service_transaction_data['status'] = 'succeeded'
    expected = {
        'id': 'ST-01',
        'created_at': '2021-11-17T14:43:10.068104+00:00',
        'amount': 20000,
        'status': 'succeeded',
    }
    data = mapper_service_transactions(service_transaction_data)
    assert data['bill_payments'] == expected


def test_mapper_ledger_accounts(ledger_account_data):
    expected = {
        'id': 'LA-DEF-01',
        'created_at': '2021-12-15T16:36:22.327730+00:00',
        'user_id': 'US2NFDj3FNs0rt0ZlTO0U7Y',
        'name': 'Frida Kahlo',
        'bank_code': '90646',
        'account_number': '646180157040841715',
    }
    data = mapper_ledger_accounts(ledger_account_data)
    assert data['accounts'] == expected


def test_mapper_ledger_accounts_savings(saving_ledger_account_data):
    expected = {
        'id': 'LA-SAV-01',
        'created_at': '2021-12-15T16:36:22.327730+00:00',
        'user_id': 'US2NFDj3FNs0rt0ZlTO0U7Y',
        'balance': 0,
    }
    data = mapper_ledger_accounts(saving_ledger_account_data)
    assert data['savings'] == expected


def test_mapper_ledger_accounts_not_implemented(hold_ledger_account_data):
    with pytest.raises(NotRequiredModelError):
        mapper_ledger_accounts(hold_ledger_account_data)
