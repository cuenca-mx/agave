import asyncio
import json
import logging
import os
import signal
import time
from functools import wraps
from itertools import count
from json import JSONDecodeError
from typing import AsyncGenerator, Awaitable, Callable, Coroutine, Optional

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
from .metrics import TaskMetrics, emit_metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', '')

BACKGROUND_TASKS: set[asyncio.Task] = set()


async def run_task(
    task_func: Callable,
    body: dict,
    message: dict,
    sqs,
    queue_url: str,
    message_receive_count: int,
    max_retries: int,
    delete_on_failure: bool,
    task_name: str,
    task_module: str,
    metrics_callback: Optional[Callable[..., Awaitable[None]]] = None,
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
            'task_func': task_name,
            'task_module': task_module,
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
    start_time = time.monotonic()
    try:
        resp = await task_func(body)
    except asyncio.CancelledError:
        delete_message = False
        log_data['response']['status'] = 'cancelled'
        raise
    except RetryTask as retry:
        retries_exhausted = message_receive_count >= max_retries + 1
        delete_message = retries_exhausted and delete_on_failure
        if not retries_exhausted and retry.countdown and retry.countdown > 0:
            await sqs.change_message_visibility(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle'],
                VisibilityTimeout=retry.countdown,
            )
        log_data['response']['delete_message'] = delete_message
        log_data['response']['status'] = (
            'failed' if retries_exhausted else 'retrying'
        )
    except Exception as exp:
        delete_message = delete_on_failure
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
        duration_ms = round((time.monotonic() - start_time) * 1000, 2)
        log_data['response']['duration_ms'] = duration_ms
        if delete_message:
            await sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle'],
            )
        logger.info(json.dumps(log_data, default=str))
        if metrics_callback:
            try:
                task_metrics = TaskMetrics(
                    task_name=task_name,
                    queue_url=queue_url,
                    concurrent_tasks_counter=lambda: len(BACKGROUND_TASKS),
                )
                await emit_metrics(
                    metrics=task_metrics,
                    status=log_data['response']['status'],
                    duration_ms=duration_ms,
                    metrics_callback=metrics_callback,
                )
            except Exception as exc:
                logger.warning(f'metrics_callback failed: {exc}')


async def message_consumer(
    queue_url: str,
    wait_time_seconds: int,
    visibility_timeout: int,
    can_read: asyncio.Event,
    sqs,
    shutdown_event: asyncio.Event,
) -> AsyncGenerator:
    for _ in count():
        await can_read.wait()
        if shutdown_event.is_set():
            return
        try:
            response = await sqs.receive_message(
                QueueUrl=queue_url,
                WaitTimeSeconds=wait_time_seconds,
                VisibilityTimeout=visibility_timeout,
                AttributeNames=['ApproximateReceiveCount'],
            )
            messages = response['Messages']
        except KeyError:
            if shutdown_event.is_set():
                return
            continue
        except HTTPClientError:
            if shutdown_event.is_set():
                return
            await asyncio.sleep(1)
            continue
        if shutdown_event.is_set():
            return
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
    delete_on_failure: bool = True,
    metrics_callback: Optional[Callable[..., Awaitable[None]]] = None,
):
    def task_builder(task_func: Callable):
        @wraps(task_func)
        async def start_task(*args, **kwargs) -> None:
            can_read = asyncio.Event()
            shutdown_event = asyncio.Event()
            concurrency_semaphore = asyncio.Semaphore(max_concurrent_tasks)
            can_read.set()

            async def concurrency_controller(coro: Coroutine) -> None:
                async with concurrency_semaphore:
                    if concurrency_semaphore.locked():
                        can_read.clear()

                    try:
                        await coro
                    finally:
                        if not shutdown_event.is_set():
                            can_read.set()

            loop = asyncio.get_running_loop()

            def _handle_signal(sig):
                logger.info(
                    f'Received {sig.name}, initiating graceful shutdown'
                )
                shutdown_event.set()
                can_read.set()

            previous_handlers = {}
            for sig in (signal.SIGTERM, signal.SIGINT):
                previous_handlers[sig] = signal.getsignal(sig)
                loop.add_signal_handler(sig, _handle_signal, sig)

            try:
                session = get_session()

                task_with_validators = validate_call(task_func)

                async with session.create_client('sqs', region_name) as sqs:
                    async for message in message_consumer(
                        queue_url,
                        wait_time_seconds,
                        visibility_timeout,
                        can_read,
                        sqs,
                        shutdown_event,
                    ):
                        try:
                            body = json.loads(message['Body'])
                        except JSONDecodeError:
                            msg_id = message['MessageId']
                            log_data = dict(
                                message_id=msg_id,
                                status='invalid_json',
                            )
                            logger.warning(json.dumps(log_data))
                            await sqs.delete_message(
                                QueueUrl=queue_url,
                                ReceiptHandle=message['ReceiptHandle'],
                            )
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
                                    delete_on_failure,
                                    task_name=task_func.__name__,
                                    task_module=task_func.__module__,
                                    metrics_callback=metrics_callback,
                                ),
                            ),
                            name='fast-agave-task',
                        )
                        BACKGROUND_TASKS.add(bg_task)
                        bg_task.add_done_callback(BACKGROUND_TASKS.discard)

                    running_tasks = await get_running_fast_agave_tasks()
                    if shutdown_event.is_set():
                        try:
                            await asyncio.wait_for(
                                asyncio.gather(*running_tasks),
                                timeout=visibility_timeout,
                            )
                        except asyncio.TimeoutError:
                            logger.warning(
                                'Graceful shutdown timeout, tasks may retry'
                            )
                    else:
                        await asyncio.gather(*running_tasks)
            finally:
                for sig, handler in previous_handlers.items():
                    loop.remove_signal_handler(sig)
                    if handler and handler not in (
                        signal.SIG_DFL,
                        signal.SIG_IGN,
                    ):
                        signal.signal(sig, handler)

        return start_task

    return task_builder
