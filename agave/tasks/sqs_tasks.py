import asyncio
import json
import logging
import os
from functools import wraps
from itertools import count
from json import JSONDecodeError
from typing import AsyncGenerator, Callable, Coroutine

from aiobotocore.httpsession import HTTPClientError
from aiobotocore.session import get_session
from pydantic import BaseModel, validate_call

from ..core.exc import RetryTask
from ..core.loggers import (
    get_request_model,
    get_response_model,
    get_sensitive_fields,
    obfuscate_sensitive_data,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', '')

BACKGROUND_TASKS = set()


async def run_task(
    task_func: Callable,
    body: dict,
    message: dict,
    sqs,
    queue_url: str,
    message_receive_count: int,
    max_retries: int,
) -> None:
    delete_message = True
    request_model = get_request_model(task_func)
    request_log_config_fields = get_sensitive_fields(request_model)
    ofuscated_request_body = obfuscate_sensitive_data(
        body,
        request_log_config_fields,
    )
    response_model = get_response_model(task_func)
    response_log_config_fields = get_sensitive_fields(response_model)
    log_data = {
        'request': {
            'task_func': task_func.__name__,
            'task_module': task_func.__module__,
            'queue_url': queue_url,
            'max_retries': max_retries,
            'body': ofuscated_request_body,
            'message_id': message['MessageId'],
            'message_attributes': message.get('Attributes', {}),
            'receipt_handle': message['ReceiptHandle'],
        },
        'response': {
            'status': 'success',
        },
    }
    try:
        resp = await task_func(body)
    except RetryTask as retry:
        delete_message = message_receive_count >= max_retries + 1
        if not delete_message and retry.countdown and retry.countdown > 0:
            await sqs.change_message_visibility(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle'],
                VisibilityTimeout=retry.countdown,
            )
        log_data['response']['delete_message'] = delete_message
        log_data['response']['status'] = 'retrying'
    except Exception as exp:
        log_data['response']['status'] = 'failed'
        log_data['response']['error'] = str(exp)
    else:
        if isinstance(resp, BaseModel):
            ofuscated_response_body = obfuscate_sensitive_data(
                resp.model_dump(),
                response_log_config_fields,
            )
        else:
            ofuscated_response_body = resp
        log_data['response']['body'] = ofuscated_response_body
    finally:
        if delete_message:
            await sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle'],
            )
        logger.info(json.dumps(log_data, default=str))


async def message_consumer(
    queue_url: str,
    wait_time_seconds: int,
    visibility_timeout: int,
    can_read: asyncio.Event,
    sqs,
) -> AsyncGenerator:
    for _ in count():
        await can_read.wait()
        try:
            response = await sqs.receive_message(
                QueueUrl=queue_url,
                WaitTimeSeconds=wait_time_seconds,
                VisibilityTimeout=visibility_timeout,
                AttributeNames=['ApproximateReceiveCount'],
            )
            messages = response['Messages']
        except KeyError:
            continue
        except HTTPClientError:
            await asyncio.sleep(1)
            continue
        for message in messages:
            yield message


async def get_running_fast_agave_tasks():
    return [
        t
        for t in asyncio.all_tasks()
        if t.get_name().startswith('fast-agave-task')
    ]


def task(
    queue_url: str,
    region_name: str = AWS_DEFAULT_REGION,
    wait_time_seconds: int = 15,
    visibility_timeout: int = 3600,
    max_retries: int = 1,
    max_concurrent_tasks: int = 5,
):
    def task_builder(task_func: Callable):
        @wraps(task_func)
        async def start_task(*args, **kwargs) -> None:
            can_read = asyncio.Event()
            concurrency_semaphore = asyncio.Semaphore(max_concurrent_tasks)
            can_read.set()

            async def concurrency_controller(coro: Coroutine) -> None:
                async with concurrency_semaphore:
                    if concurrency_semaphore.locked():
                        can_read.clear()

                    try:
                        await coro
                    finally:
                        can_read.set()

            session = get_session()

            task_with_validators = validate_call(task_func)

            async with session.create_client('sqs', region_name) as sqs:
                async for message in message_consumer(
                    queue_url,
                    wait_time_seconds,
                    visibility_timeout,
                    can_read,
                    sqs,
                ):
                    try:
                        body = json.loads(message['Body'])
                    except JSONDecodeError:
                        continue

                    message_receive_count = int(
                        message['Attributes']['ApproximateReceiveCount']
                    )
                    bg_task = asyncio.create_task(
                        concurrency_controller(
                            run_task(
                                task_with_validators,
                                body,
                                message,
                                sqs,
                                queue_url,
                                message_receive_count,
                                max_retries,
                            ),
                        ),
                        name='fast-agave-task',
                    )
                    BACKGROUND_TASKS.add(bg_task)
                    bg_task.add_done_callback(BACKGROUND_TASKS.discard)

                # Espera a que terminen todos los tasks pendientes creados por
                # `asyncio.create_task`. De esta forma los tasks
                # podrán borrar el mensaje del queue usando la misma instancia
                # del cliente de SQS
                running_tasks = await get_running_fast_agave_tasks()
                await asyncio.gather(*running_tasks)

        return start_task

    return task_builder
