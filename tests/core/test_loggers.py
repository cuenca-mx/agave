import pytest
from cuenca_validations.types.general import LogConfig

from agave.core.loggers import obfuscate_sensitive_data


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
