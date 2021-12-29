import pytest
from cuenca_validations.typing import DictStrAny


@pytest.fixture
def service_provider_data():
    return {
        "name": "Axtel",
        "categories": [{"name": "cable"}, {"name": "internet"}],
        "fields": [
            {
                "service_provider_id": None,
                "service_provider_key": "internet_axtel",
                "mask": "(000) 000-0000",
                "type": "phone_number",
                "requires_accountholder_name": True,
                "topup_amounts": None,
                "hours_to_fullfill": None,
                "accepts_partial_payment": None,
            }
        ],
        "id": "SP-01",
        "updated_at": "2021-11-17T13:15:29.832299+00:00",
        "created_at": "2021-11-17T13:15:29.832299+00:00",
    }


@pytest.fixture
def service_transaction_data():
    return {
        "id": "ST-01",
        "amount": 20000,
        "numero_referencia": "1234567",
        "service_account": {
            "service_field": {
                "service_provider_key": "electricity_cfe",
                "mask": "00000000",
                "type": "account_number",
                "requires_accountholder_name": False,
                "is_active": True,
                "service_provider_id": "SP-01",
                "id": "SP5U6sT9yKiPNn5VAFlqaFgg",
                "can_check_balance": True,
                "topup_amounts": None,
                "accepts_partial_payment": None,
                "created_at": "2021-11-17T14:43:10.068104+00:00",
                "updated_at": "2021-11-17T14:43:10.068104+00:00",
                "hours_to_fullfill": None,
            },
            "name": "CFE",
            "account_number": "0987654321233458",
            "service_provider_field_id": "SP5U6sT9yKiPNn5VAFlqaFgg",
            "id": "SA7o66iYi9yhfCFovPCnYzYM",
            "created_at": "2021-11-17T14:43:10.068104+00:00",
            "user_id": None,
            "name_on_account": None,
            "updated_at": "2021-11-17T14:43:10.068104+00:00",
        },
        "ledger_account": {
            "user_id": "US1NlTaZwK3FubOhXNC9Vb8Y",
            "min_balance": -250000,
            "id": "LA7v0DYGgmGk9j5hxUBov2xR",
            "balance": 0,
            "debit_balance": 0,
            "account_type": "default",
            "currency": "mxn",
            "cash_deposit_references": [],
            "created_at": "2021-11-17T14:43:10.068104+00:00",
            "card_withdraw_limit": None,
        },
        "ledger_account_id": "LA7v0DYGgmGk9j5hxUBov2xR",
        "service_account_id": "SA7o66iYi9yhfCFovPCnYzYM",
        "arcusd_id": "AD2UUVUmmt37SLORxe1j4B7z",
        "status": "created",
        "created_at": "2021-11-17T14:43:10.068104+00:00",
        "reason": None,
        "updated_at": "2021-11-17T14:43:10.068104+00:00",
    }


@pytest.fixture
def ledger_account_data() -> DictStrAny:
    return {
        "user": {
            "pending_notifications": 0,
            "status": "active",
            "last_login_at": None,
            "type": "human",
            "available_invitations": 3,
            "id": "US2NFDj3FNs0rt0ZlTO0U7Y",
            "default_ledger_account_id": "LA3leMWCYRUxUeN0CUkmj04h",
            "login_attempts": 0,
            "beta_tester": False,
            "name": "Frida Kahlo",
            "updated_at": "2021-12-15T16:36:22.327730+00:00",
            "created_at": "2021-12-15T16:36:22.327730+00:00",
        },
        "card_withdraw_limit": None,
        "user_id": "US2NFDj3FNs0rt0ZlTO0U7Y",
        "balance": 0,
        "min_balance": 0,
        "currency": "mxn",
        "debit_balance": 0,
        "_clabe": {
            "ledger_account_id": "LA3leMWCYRUxUeN0CUkmj04h",
            "clabe": "646180157040841715",
            "updated_at": "2021-12-15T16:36:22.327730+00:00",
            "created_at": "2021-12-15T04:16:08.873910+00:00",
        },
        "account_type": "default",
        "id": "LA-DEF-01",
        "created_at": "2021-12-15T16:36:22.327730+00:00",
    }


@pytest.fixture
def saving_ledger_account_data(ledger_account_data) -> DictStrAny:
    ledger_account_data.pop('_clabe')
    ledger_account_data['account_type'] = 'saving'
    ledger_account_data['id'] = 'LA-SAV-01'
    return ledger_account_data


@pytest.fixture
def hold_ledger_account_data(ledger_account_data) -> DictStrAny:
    ledger_account_data.pop('_clabe')
    ledger_account_data['account_type'] = 'hold'
    ledger_account_data['id'] = 'LA-HOLD-01'
    return ledger_account_data
