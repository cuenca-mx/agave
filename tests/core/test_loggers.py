from cuenca_validations.types.general import LogConfig

from agave.core.loggers import obfuscate_sensitive_data


def test_obfuscate_with_exclusion():
    body = {"username": "user123", "password": "secret"}
    sensitive_fields = {"password": LogConfig(excluded=True)}
    result = obfuscate_sensitive_data(body, sensitive_fields)
    assert "password" not in result  # Password should be removed


def test_obfuscate_with_masking():
    body = {"username": "user123", "password": "secret"}
    sensitive_fields = {"password": LogConfig(masked=True)}
    result = obfuscate_sensitive_data(body, sensitive_fields)
    assert result["password"] == "*****"  # Password should be fully masked


def test_obfuscate_with_partial_masking():
    body = {"username": "user123", "password": "supersecret"}
    sensitive_fields = {
        "password": LogConfig(masked=True, unmasked_chars_length=4)
    }
    result = obfuscate_sensitive_data(body, sensitive_fields)
    assert result["password"] == "*****cret"  # Only last 4 chars visible


def test_obfuscate_non_existing_field():
    body = {"username": "user123"}
    sensitive_fields = {"password": LogConfig(masked=True)}
    result = obfuscate_sensitive_data(body, sensitive_fields)
    assert "password" not in result  # Non-existing field should not be added
