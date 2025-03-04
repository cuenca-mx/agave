from typing import Optional, Union

import pytest
from cuenca_validations.types.general import LogConfig
from pydantic import BaseModel

from agave.core.loggers import (
    get_request_model,
    get_response_model,
    obfuscate_sensitive_data,
)


@pytest.mark.parametrize(
    "body, sensitive_fields, expected_result",
    [
        # Test 1: Obfuscate with exclusion
        (
            {"username": "user123", "password": "secret"},
            {"password": LogConfig(excluded=True)},
            {"username": "user123"},
        ),
        # Test 2: Obfuscate with masking
        (
            {"username": "user123", "password": "secret"},
            {"password": LogConfig(masked=True)},
            {"username": "user123", "password": "*****"},
        ),
        # Test 3: Obfuscate with partial masking
        (
            {"username": "user123", "password": "supersecret"},
            {"password": LogConfig(masked=True, unmasked_chars_length=4)},
            {"username": "user123", "password": "*****cret"},
        ),
        # Test 4: Obfuscate non-existing field
        (
            {"username": "user123"},
            {"password": LogConfig(masked=True)},
            {"username": "user123"},
        ),
    ],
)
def test_obfuscate_sensitive_data(body, sensitive_fields, expected_result):
    result = obfuscate_sensitive_data(body, sensitive_fields)
    assert result == expected_result


@pytest.mark.parametrize(
    'param_type, response_type',
    [
        (int, int),
        (float, float),
        (str, str),
        (bool, bool),
        (dict, dict),
        (Optional[int], Optional[int]),
        (list[int], list[int]),
        (tuple[int, str], tuple[int, str]),
        (set[int], set[int]),
        (Union[list[int], str], str),
    ],
)
def test_get_request_model_invalid_types(param_type, response_type) -> None:
    def my_function(param: param_type) -> response_type:
        return param

    request_model = get_request_model(my_function)
    response_model = get_response_model(my_function)

    assert request_model is None
    assert response_model is None


def test_get_request_model_valid_types() -> None:
    class RequestModel(BaseModel):
        id: int
        name: str

    class ResponseModel(BaseModel):
        id: int

    def my_function(param: RequestModel) -> ResponseModel:
        return ResponseModel(id=param.id)

    request_model = get_request_model(my_function)
    response_model = get_response_model(my_function)

    assert request_model == [RequestModel]
    assert response_model == ResponseModel
