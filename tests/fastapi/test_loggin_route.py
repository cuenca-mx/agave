import json
import logging
import re
from tempfile import TemporaryFile

import pytest
from fastapi.testclient import TestClient

from examples.models import Account


def extract_log_data(
    log_output: str, pattern: str, error_message: str
) -> dict:
    """Extracts JSON data from log output using a regex pattern."""
    match = re.search(pattern, log_output)
    if not match:
        raise Exception(error_message)
    return json.loads(match.group(1))


def test_logger_no_request_model(fastapi_client: TestClient, caplog) -> None:
    """
    Test that verifies:
    - A resource can be retrieved successfully (HTTP 200)
    - The request and response are properly logged
    """
    caplog.set_level(logging.INFO)

    request_data = {
        'some_field': 'some value',
    }
    response = fastapi_client.post('/token', json=request_data)
    response_body = response.json()

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data['request']['body'] == request_data
    assert log_data['response']['body'] == response_body


def test_logger_retrieve_resource(
    fastapi_client: TestClient, account: Account, caplog
) -> None:
    """
    Test that verifies:
    - A resource can be retrieved successfully (HTTP 200)
    - The request and response are properly logged
    """
    caplog.set_level(logging.INFO)

    response = fastapi_client.get(f'/accounts/{account.id}')
    response_body = response.json()

    assert response.status_code == 200
    assert response_body == account.to_dict()

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data['request']['url'].endswith(f'/accounts/{account.id}')
    assert log_data['response']['status_code'] == 200
    assert log_data['response']['body']['name'] == '*****Kahlo'


def test_logger_update_resource(
    fastapi_client: TestClient, account: Account, caplog
) -> None:
    """
    Test that verifies:
    - A resource can be updated successfully (HTTP 200)
    - The request and response are properly logged
    """
    caplog.set_level(logging.INFO)

    resp = fastapi_client.patch(
        f'/accounts/{account.id}',
        json=dict(name='Maria Felix'),
    )
    json_body = resp.json()
    status_code = resp.status_code
    account.reload()
    assert json_body['name'] == 'Maria Felix'
    assert status_code == 200

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data['response']['status_code'] == 200
    assert log_data['response']['body']['name'] == '*****Felix'


def test_logger_create_resource_bad_request(
    fastapi_client: TestClient, caplog
) -> None:
    """
    Test that verifies the logger correctly captures and logs a 422 Bad Request
    when an invalid request payload is sent.
    """
    caplog.set_level(logging.INFO)

    request_data = {'invalid_field': 'some value'}
    response = fastapi_client.post('/accounts', json=request_data)

    assert response.status_code == 422

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data['request']['body'] == request_data
    assert log_data['response']['status_code'] == 422


def test_logger_test_logger_retrieve_resource_not_found(
    fastapi_client: TestClient, caplog
) -> None:
    """
    Test that verifies:
    - A request for a non-existent resource returns a 404
    - The request and response are properly logged
    """
    caplog.set_level(logging.INFO)

    resource_id = "unknown_id"
    response = fastapi_client.get(f"/accounts/{resource_id}")

    assert response.status_code == 404

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data["request"]["url"].endswith(f"/accounts/{resource_id}")
    assert log_data['response']['status_code'] == 404


def test_logger_upload_resource(fastapi_client: TestClient, caplog) -> None:
    """
    Test that verifies the logger properly handles file uploads, ensuring:
    - Request body is logged as None (since files are not logged)
    - Content-Type is correctly set to multipart/form-data
    """
    caplog.set_level(logging.INFO)

    with TemporaryFile(mode='rb') as f:
        file_body = f.read()
    response = fastapi_client.post(
        '/files',
        files=dict(file=(None, file_body), file_name=(None, 'test_file.txt')),
    )

    assert response.status_code == 201
    response_body = response.json()
    assert response_body['name'] == 'test_file.txt'

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data['request']['body'] is None
    assert log_data['request']['headers']['content-type'].startswith(
        'multipart/form-data'
    )


def test_logger_headers_case_insensitive(
    fastapi_client: TestClient, caplog
) -> None:
    caplog.set_level(logging.INFO)

    request_data = {
        'user': 'user',
        'password': 'My-super-secret-password',
        'short_secret': '123',
    }

    request_headers = {
        'x-cuenca-loginid': 'My-secret-login-id',
        'X-CUENCA-LOGINTOKEN': 'My-secret-login-token',
        'AUTHORIZATION': '123',
        'Content-Type': 'application/json',
        'connection': 'keep-alive',
    }

    response = fastapi_client.post(
        '/api_keys', json=request_data, headers=request_headers
    )

    assert response.status_code == 201

    expected_log_headers = {
        'host': 'testserver',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'user-agent': 'testclient',
        'x-cuenca-loginid': '*****n-id',
        'x-cuenca-logintoken': '*****oken',
        'authorization': '*****',
        'content-type': 'application/json',
    }

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data['request']['headers'] == expected_log_headers


def test_logger_api_route(fastapi_client: TestClient, caplog) -> None:
    """
    Test that verifies the logger properly masks sensitive data in:
    - Request headers
    - Request body fields
    - Response body fields
    """
    caplog.set_level(logging.INFO)

    request_data = {
        'user': 'user',
        'password': 'My-super-secret-password',
        'short_secret': '123',
    }
    request_headers = {
        'X-Cuenca-LoginId': 'My-secret-login-id',
        'X-Cuenca-LoginToken': 'My-secret-login-token',
        'Authorization': '123',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
    }

    response = fastapi_client.post(
        '/api_keys', json=request_data, headers=request_headers
    )
    response_body = response.json()

    assert response.status_code == 201
    assert response_body['secret'] == 'My-super-secret-key'
    assert response_body['password'] == 'My-super-secret-password'

    expected_log = {
        'request': {
            'method': 'POST',
            'url': 'http://testserver/api_keys',
            'query_params': '',
            'headers': {
                'host': 'testserver',
                'accept': '*/*',
                'accept-encoding': 'gzip, deflate',
                'user-agent': 'testclient',
                'x-cuenca-loginid': '*****n-id',
                'x-cuenca-logintoken': '*****oken',
                'authorization': '*****',
                'content-type': 'application/json',
            },
            'body': {
                'user': 'user',
                'password': '*****',
                'short_secret': '*****',
            },
        },
        'response': {
            'status_code': 201,
            'headers': {'content-type': 'application/json'},
            'body': {
                'id': response_body['id'],
                'secret': '*****-key',
                'user': 'user',
                'password': '*****word',
                'user_id': 'US123456789',
                'platform_id': 'PT123456',
                'created_at': None,
                'another_field': '12345678',
            },
        },
    }

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data == expected_log


def test_logger_internal_server_error(
    fastapi_client: TestClient, caplog
) -> None:
    """
    Test that verifies:
    - A request that causes a 500 error is logged.
    """
    caplog.set_level(logging.INFO)

    request_data = {'some_field': 'some value'}

    with pytest.raises(Exception):
        fastapi_client.post('/simulate_500', json=request_data)

    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data['request']['body'] == request_data
    assert log_data['response']['status_code'] == 500


def test_logger_bad_request(fastapi_client: TestClient, caplog) -> None:
    """
    Test that verifies:
    - A request that causes a 400 error is logged.
    """
    caplog.set_level(logging.INFO)

    request_data = {'some_field': 'some value'}
    response = fastapi_client.post('/simulate_400', json=request_data)
    assert response.status_code == 400

    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data['request']['body'] == request_data


def test_logger_unauthorized(fastapi_client: TestClient, caplog) -> None:
    """
    Test that verifies:
    - A request that causes a 401 error is logged.
    """

    caplog.set_level(logging.INFO)

    request_data = {'some_field': 'some value'}
    response = fastapi_client.post('/simulate_401', json=request_data)
    assert response.status_code == 401

    log_output = caplog.text
    log_data = extract_log_data(
        log_output,
        r"(\{.*\})",
        "Info not found in logs",
    )

    assert log_data['request']['body'] == request_data
