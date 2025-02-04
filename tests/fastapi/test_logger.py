import json
import logging
import re
from io import StringIO
from tempfile import TemporaryFile

from fastapi.testclient import TestClient

from examples.models import Account


def extract_log_data(
    log_output: str, pattern: str, error_message: str
) -> dict:
    """Extracts JSON data from log output using a regex pattern."""
    match = re.search(pattern, log_output)
    if not match:
        raise RuntimeError(error_message)
    return json.loads(match.group(1))


def test_logger_retrieve_resource(
    fastapi_client: TestClient, account: Account
) -> None:
    """
    Test that verifies:
    - A resource can be retrieved successfully (HTTP 200)
    - The response body matches the expected resource data
    - The request and response are properly logged
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    original_handlers = logger.handlers
    log_stream = StringIO()
    log_handler = logging.StreamHandler(log_stream)
    logger.handlers = [log_handler]

    try:
        response = fastapi_client.get(f'/accounts/{account.id}')
        response_body = response.json()

        assert response.status_code == 200
        assert response_body == account.to_dict()

        # Extract and validate logger output
        log_output = log_stream.getvalue()
        log_data_request = extract_log_data(
            log_output,
            r"Request Info: (\{.*\})",
            "Request Info not found in logs",
        )
        log_data_response = extract_log_data(
            log_output,
            r"Response Info: (\{.*\})",
            "Response Info not found in logs",
        )

        assert log_data_request['request']['method'] == 'GET'
        assert log_data_request['request']['url'].endswith(
            f'/accounts/{account.id}'
        )

        assert log_data_response['response']['status_code'] == 200
        assert log_data_response['response']['body'] == response_body
    finally:
        logger.handlers = original_handlers


def test_logger_create_resource_bad_request(
    fastapi_client: TestClient,
) -> None:
    """
    Test that verifies the logger correctly captures and logs a 422 Bad Request
    when an invalid request payload is sent.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    original_handlers = logger.handlers
    log_stream = StringIO()
    log_handler = logging.StreamHandler(log_stream)
    logger.handlers = [log_handler]

    try:
        request_data = {'invalid_field': 'some value'}
        response = fastapi_client.post('/accounts', json=request_data)

        assert response.status_code == 422

        # Extract and validate logger output
        log_output = log_stream.getvalue()
        log_data_request = extract_log_data(
            log_output,
            r"Request Info: (\{.*\})",
            "Request Info not found in logs",
        )

        assert log_data_request['request']['body'] == request_data
    finally:
        logger.handlers = original_handlers


def test_logger_test_logger_retrieve_resource_not_found(
    fastapi_client: TestClient,
) -> None:
    """
    Test that verifies:
    - A request for a non-existent resource returns a 404
    - The request and response are properly logged
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    original_handlers = logger.handlers
    log_stream = StringIO()
    log_handler = logging.StreamHandler(log_stream)
    logger.handlers = [log_handler]

    try:
        resource_id = "unknown_id"
        response = fastapi_client.get(f"/accounts/{resource_id}")

        assert response.status_code == 404

        # Extract and validate logger output
        log_output = log_stream.getvalue()
        log_data_request = extract_log_data(
            log_output,
            r"Request Info: (\{.*\})",
            "Request Info not found in logs",
        )

        assert log_data_request["request"]["method"] == "GET"
        assert log_data_request["request"]["url"].endswith(
            f"/accounts/{resource_id}"
        )
    finally:
        logger.handlers = original_handlers


def test_logger_upload_resource(fastapi_client: TestClient) -> None:
    """
    Test that verifies the logger properly handles file uploads, ensuring:
    - Request body is logged as None (since files are not logged)
    - Content-Type is correctly set to multipart/form-data
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    original_handlers = logger.handlers
    log_stream = StringIO()
    log_handler = logging.StreamHandler(log_stream)
    logger.handlers = [log_handler]

    try:
        with TemporaryFile(mode='rb') as f:
            file_body = f.read()
        response = fastapi_client.post(
            '/files',
            files=dict(
                file=(None, file_body), file_name=(None, 'test_file.txt')
            ),
        )

        assert response.status_code == 201
        response_body = response.json()
        assert response_body['name'] == 'test_file.txt'

        # Extract and validate logger output
        log_output = log_stream.getvalue()
        log_data = extract_log_data(
            log_output,
            r"Request Info: (\{.*\})",
            "Request Info not found in logs",
        )

        assert log_data['request']['body'] is None
        assert log_data['request']['headers']['content-type'].startswith(
            'multipart/form-data'
        )
    finally:
        logger.handlers = original_handlers


def test_logger_api_route(fastapi_client: TestClient) -> None:
    """
    Test that verifies the logger properly masks sensitive data in:
    - Request headers
    - Request body fields
    - Response body fields
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    original_handlers = logger.handlers
    log_stream = StringIO()
    log_handler = logging.StreamHandler(log_stream)
    logger.handlers = [log_handler]

    try:
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

        # Extract and validate logger output
        log_output = log_stream.getvalue()
        log_data_request = extract_log_data(
            log_output,
            r"Request Info: (\{.*\})",
            "Request Info not found in logs",
        )
        log_data_response = extract_log_data(
            log_output,
            r"Response Info: (\{.*\})",
            "Response Info not found in logs",
        )

        # Validate request headers masking
        logged_headers = log_data_request['request']['headers']
        assert logged_headers['x-cuenca-loginid'] == '*****n-id'
        assert logged_headers['x-cuenca-logintoken'] == '*****oken'
        assert logged_headers['authorization'] == '123'
        assert 'connection' not in logged_headers  # Ensuring it is removed

        # Validate request body masking
        logged_request_body = log_data_request['request']['body']
        assert logged_request_body['password'] == '*****'
        assert logged_request_body['user'] == 'user'
        assert logged_request_body['short_secret'] == '*****'

        # Validate response body masking
        logged_response_body = log_data_response['response']['body']
        assert logged_response_body['secret'] == '*****-key'
        assert logged_response_body['password'] == '*****word'
        assert logged_response_body['user_id'] == 'US123456789'
        assert logged_response_body['platform_id'] == 'PT123456'
        assert (
            'deactivated_at' not in logged_response_body
        )  # Ensuring it is removed
    finally:
        logger.handlers = original_handlers


def test_logger_internal_server_error(fastapi_client: TestClient) -> None:
    """
    Test that verifies:
    - A request that causes a 500 error is logged.
    - The request is logged correctly.
    - The response is NOT logged, since the server crashed.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    original_handlers = logger.handlers
    log_stream = StringIO()
    log_handler = logging.StreamHandler(log_stream)
    logger.handlers = [log_handler]

    try:
        request_data = {'some_field': 'some value'}
        response = fastapi_client.post('/simulate_500', json=request_data)
        assert response.status_code == 500

        log_output = log_stream.getvalue()

        log_data_request = extract_log_data(
            log_output,
            r"Request Info: (\{.*\})",
            "Request Info not found in logs",
        )
        assert log_data_request['request']['method'] == 'POST'
        assert log_data_request['request']['url'].endswith('/simulate_500')
        assert log_data_request['request']['body'] == request_data

    finally:
        logger.handlers = original_handlers
