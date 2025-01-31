import json
import logging
import re
from io import StringIO

from fastapi.testclient import TestClient


def test_logger_api_route(fastapi_client: TestClient) -> None:
    """
    This test verifies the logger properly masks sensitive data:
    - Request headers
    - Request body fields
    - Response body fields
    """
    # Setup temporary logger handler to capture output
    string_io = StringIO()
    string_handler = logging.StreamHandler(string_io)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    original_handlers = logger.handlers
    logger.handlers = [string_handler]

    data = dict(
        user='user', password='My-super-secret-password', short_secret='123'
    )
    headers = {
        'X-Cuenca-LoginId': 'My-secret-login-id',
        'X-Cuenca-LoginToken': 'My-secret-login-token',
        'Authorization': '123',
        'content-type': 'application/json',
        'connection': 'keep-alive',
    }
    resp = fastapi_client.post('/api_keys', json=data, headers=headers)
    json_body = resp.json()
    assert resp.status_code == 201
    assert json_body['secret'] == 'My-super-secret-key'
    assert json_body['password'] == 'My-super-secret-password'

    # Validate logger output
    log_output = string_io.getvalue()
    match = re.search(r'Info: (\{.*\})', log_output)
    if match:
        json_str = match.group(1)
        log_data = json.loads(json_str)
    else:
        raise ValueError("No se encontró el objeto Info")

    # Validate request masking
    log_headers = log_data['request']['headers']
    assert log_headers['x-cuenca-loginid'] == '*****n-id'
    assert log_headers['x-cuenca-logintoken'] == '*****oken'
    assert log_headers['authorization'] == '123'
    assert 'connection' not in log_headers

    # Validate request body masking
    log_body = log_data['request']['body']
    assert log_body['password'] == '*****'
    assert log_body['user'] == 'user'
    assert log_body['short_secret'] == '*****'

    # Validate response body masking
    log_response = log_data['response']['body']
    assert log_response['secret'] == '*****-key'
    assert log_response['password'] == '*****word'
    assert log_response['user_id'] == 'US123456789'
    assert log_response['platform_id'] == 'PT123456'

    logger.handlers = original_handlers
