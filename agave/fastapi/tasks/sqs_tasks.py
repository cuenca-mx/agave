import asyncio
import json
import os
from functools import wraps
from itertools import count
from json import JSONDecodeError
from typing import AsyncGenerator, Callable, Coroutine

from aiobotocore.httpsession import HTTPClientError
from aiobotocore.session import get_session
from pydantic import validate_call

from ..exc import RetryTask

AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', '')

BACKGROUND_TASKS = set()


async def run_task(
    task_func: Callable,
    body: dict,
    sqs,
    queue_url: str,
    receipt_handle: str,
    message_receive_count: int,
    max_retries: int,
) -> None:
    delete_message = True
    try:
        await task_func(body)
    except RetryTask as retry:
        delete_message = message_receive_count >= max_retries + 1
        if not delete_message and retry.countdown and retry.countdown > 0:
            await sqs.change_message_visibility(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
                VisibilityTimeout=retry.countdown,
            )
    finally:
        if delete_message:
            await sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
            )


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
                                sqs,
                                queue_url,
                                message['ReceiptHandle'],
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
