import json
from inspect import Signature, signature
from typing import Any, Optional, Union

from cuenca_validations.types.helpers import get_log_config
from pydantic import BaseModel

EXCLUDED_HEADERS: set[str] = set()
SENSITIVE_HEADERS: set[str] = set()
SENSITIVE_RESPONSE_MODEL_FIELDS: set[str] = set()
SENSITIVE_REQUEST_MODEL_FIELDS: set[str] = set()


def obfuscate_sensitive_headers(headers: dict[str, Any]) -> dict[str, Any]:
    obfuscated = {
        k: v for k, v in headers.items() if k.lower() not in EXCLUDED_HEADERS
    }

    for header in SENSITIVE_HEADERS:
        if (value := obfuscated.get(header.lower())) and len(value) > 4:
            obfuscated[header.lower()] = f"{'*' * 5}{value[-4:]}"

    return obfuscated


def obfuscate_sensitive_body(
    body: dict[str, Any],
    model_name: str,
    sensitive_fields: set[str],
) -> dict[str, Any]:
    obfuscated = body.copy()

    for field_spec in sensitive_fields:

        _, field_name, log_chars_str = field_spec.split('.')
        full_field_name = f"{model_name}.{field_name}.{log_chars_str}"

        if (
            full_field_name not in sensitive_fields
            or field_name not in obfuscated
        ):
            continue

        if full_field_name.endswith('.excluded'):
            del obfuscated[field_name]
            continue

        value = obfuscated[field_name]
        log_chars = int(log_chars_str)

        obfuscated[field_name] = (
            '*' * 5 + value[-log_chars:] if log_chars > 0 else '*' * 5
        )

    return obfuscated


def get_request_model(method: Any) -> Optional[type[BaseModel]]:
    """
    Analyzes a method's parameters to extract request model.
    """
    create_signature: Signature = signature(method)
    parameters = list(create_signature.parameters.values())
    request_model = None

    if parameters:
        request_param = parameters[0]
        request_model = request_param.annotation

    return request_model


def get_sensitive_fields(model: type[BaseModel]) -> set[str]:
    """
    Analyzes a Pydantic model and returns a set of field names
    marked as sensitive in their metadata.
    """

    sensitive_fields: set[str] = set()

    if not issubclass(model, BaseModel):
        return sensitive_fields

    sensitive_fields = set()
    for field_name, field in model.model_fields.items():
        log_config = get_log_config(field)
        if log_config and log_config.masked:
            sensitive_fields.add(
                f"{model.__name__}."
                f"{field_name}."
                f"{log_config.unmasked_chars_length}"
            )
        if log_config and log_config.excluded:
            sensitive_fields.add(
                f"{model.__name__}." f"{field_name}." f"excluded"
            )
    return sensitive_fields


def parse_body(body: bytes) -> Union[dict, None]:
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None
