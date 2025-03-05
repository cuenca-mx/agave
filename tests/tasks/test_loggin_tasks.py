import json
from typing import Annotated, Union
from unittest.mock import AsyncMock, call

from cuenca_validations.types import LogConfig
from pydantic import BaseModel

from agave.core.exc import RetryTask
from agave.tasks.sqs_tasks import task

from ..utils import CORE_QUEUE_REGION, extract_log_data


async def test_execute_tasks_logger(sqs_client, caplog) -> None:
    test_message = dict(foo='bar')
    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='1234',
    )

    async_mock_function = AsyncMock()

    async def my_task_with_logger(data: dict) -> None:
        await async_mock_function(data)

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )(my_task_with_logger)()
    async_mock_function.assert_called_with(test_message)

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(log_output)

    assert len(log_data) == 1  # one log entry for the task
    assert log_data[0]['request']['task_func'] == my_task_with_logger.__name__
    assert log_data[0]['request']['body'] == test_message
    assert log_data[0]['response']['status'] == 'success'
    assert log_data[0]['response']['body'] is None


async def test_execute_tasks_with_validator_logger(sqs_client, caplog) -> None:
    class ValidatorRequest(BaseModel):
        id: str
        secret: Annotated[str, LogConfig(masked=True, unmasked_chars_length=3)]

    class ValidatorResponse(BaseModel):
        id: str
        api_key: Annotated[
            str, LogConfig(masked=True, unmasked_chars_length=3)
        ]
        status: str

    async_mock_function = AsyncMock(return_value=None)

    async def my_task(data: ValidatorRequest) -> ValidatorResponse:
        await async_mock_function(data)
        return ValidatorResponse(
            id='abc123', api_key='1234567890', status='success'
        )

    data = dict(id='abc123', secret='my-secret')
    expected_message = dict(id='abc123', secret='*****ret')
    expected_response = dict(id='abc123', api_key='*****890', status='success')

    test_message = ValidatorRequest(**data)
    await sqs_client.send_message(
        MessageBody=test_message.model_dump_json(),
        MessageGroupId='1234',
    )
    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )(my_task)()
    async_mock_function.assert_called_with(test_message)

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(log_output)

    assert log_data[0]['request']['task_func'] == my_task.__name__
    assert log_data[0]['request']['body'] == expected_message
    assert log_data[0]['response']['status'] == 'success'
    assert log_data[0]['response']['body'] == expected_response


async def test_execute_tasks_with_union_validator_logger(
    sqs_client, caplog
) -> None:
    class User(BaseModel):
        id: str
        name: str
        secret: Annotated[str, LogConfig(masked=True, unmasked_chars_length=3)]

    class Company(BaseModel):
        id: str
        legal_name: str
        rfc: str
        secret: Annotated[str, LogConfig(masked=True, unmasked_chars_length=3)]

    async_mock_function = AsyncMock(return_value=None)

    async def my_task(data: Union[User, Company]) -> None:
        await async_mock_function(data.model_dump())

    task_params = dict(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )
    test_message = dict(
        id='ID123', name='Sor Juana Inés de la Cruz', secret='my-secret'
    )
    expected_message_user = dict(
        id='ID123', name='Sor Juana Inés de la Cruz', secret='*****ret'
    )
    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='4321',
    )
    await task(**task_params)(my_task)()
    async_mock_function.assert_called_with(test_message)

    async_mock_function.reset_mock()
    test_message = dict(
        id='ID123',
        legal_name='FastAgave',
        rfc='FA123456789',
        secret='my-secret',
    )
    expected_message_company = dict(
        id='ID123',
        legal_name='FastAgave',
        rfc='FA123456789',
        secret='*****ret',
    )
    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='54321',
    )
    await task(**task_params)(my_task)()
    async_mock_function.assert_called_with(test_message)

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(log_output)

    assert len(log_data) == 2  # two log entries for the task
    assert log_data[0]['request']['body'] == expected_message_user
    assert log_data[1]['request']['body'] == expected_message_company


async def test_execute_tasks_with_response_logger(sqs_client, caplog) -> None:
    test_message = dict(foo='bar')

    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='1234',
    )
    async_mock_function = AsyncMock()

    async def my_task_with_logger(data: dict) -> dict:
        await async_mock_function(data)
        my_response = dict(response='my_custom_response')
        return my_response

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )(my_task_with_logger)()
    async_mock_function.assert_called_with(test_message)

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(log_output)

    assert log_data[0]['request']['task_func'] == my_task_with_logger.__name__
    assert log_data[0]['request']['body'] == test_message
    assert log_data[0]['response']['status'] == 'success'
    assert log_data[0]['response']['body'] == dict(
        response='my_custom_response'
    )


async def test_execute_tasks_with_response_non_serializable(
    sqs_client, caplog
) -> None:

    class NonSerializableResponse:
        def __init__(self, value):
            self.value = value

    test_message = dict(foo='bar')

    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='1234',
    )
    async_mock_function = AsyncMock()

    async def my_task(data: dict) -> NonSerializableResponse:
        await async_mock_function(data)
        return NonSerializableResponse('test_value')

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )(my_task)()
    async_mock_function.assert_called_with(test_message)

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(log_output)

    assert log_data[0]['response']['status'] == 'success'
    assert (
        'NonSerializableResponse object at' in log_data[0]['response']['body']
    )


async def test_retry_tasks_default_max_retries_logger(
    sqs_client, caplog
) -> None:
    test_message = dict(id='abc123', name='fast-agave')

    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='1234',
    )

    async_mock_function = AsyncMock(side_effect=RetryTask)

    async def my_task(data: dict) -> None:
        await async_mock_function(data)

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
        max_retries=2,
    )(my_task)()

    expected_calls = [call(test_message)] * 3
    async_mock_function.assert_has_calls(expected_calls)
    assert async_mock_function.call_count == len(expected_calls)

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(log_output)

    assert len(log_data) == 3  # 3 log entries for the task

    assert log_data[0]['request']['task_func'] == my_task.__name__
    assert log_data[0]['request']['body'] == test_message

    # For the first execution
    assert log_data[0]['response']['status'] == 'retrying'
    assert (
        log_data[0]['request']['message_attributes']['ApproximateReceiveCount']
        == '1'
    )

    # For the second execution
    assert log_data[1]['response']['status'] == 'retrying'
    assert (
        log_data[1]['request']['message_attributes']['ApproximateReceiveCount']
        == '2'
    )

    # For the third execution
    assert log_data[2]['response']['status'] == 'retrying'
    assert (
        log_data[2]['request']['message_attributes']['ApproximateReceiveCount']
        == '3'
    )


async def test_task_with_exception_logger(sqs_client, caplog) -> None:
    test_message = dict(foo='bar')
    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='1234',
    )

    async def my_task_with_logger(data: dict) -> None:
        raise Exception('test_exception')

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
        max_retries=2,
    )(my_task_with_logger)()

    # Extract and validate logger output
    log_output = caplog.text
    log_data = extract_log_data(log_output)

    assert log_data[0]['response']['status'] == 'failed'
    assert log_data[0]['response']['error'] == 'test_exception'
