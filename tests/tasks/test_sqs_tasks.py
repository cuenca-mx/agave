import asyncio
import datetime as dt
import json
import uuid
from typing import Union
from unittest.mock import AsyncMock, call, patch

import aiobotocore.client
from aiobotocore.httpsession import HTTPClientError
from pydantic import BaseModel

from agave.core.exc import RetryTask
from agave.tasks.sqs_tasks import (
    BACKGROUND_TASKS,
    get_running_fast_agave_tasks,
    task,
)

from ..utils import CORE_QUEUE_REGION


async def test_execute_tasks(sqs_client) -> None:
    """
    Happy path: Se obtiene el mensaje y se ejecuta el task exitosamente.
    El mensaje debe ser eliminado automáticamente del queue
    """
    test_message = dict(id='abc123', name='fast-agave')

    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='1234',
    )

    async_mock_function = AsyncMock()

    async def my_task(data: dict) -> None:
        await async_mock_function(data)

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )(my_task)()
    async_mock_function.assert_called_with(test_message)
    assert async_mock_function.call_count == 1

    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp
    assert len(BACKGROUND_TASKS) == 0


async def test_execute_tasks_with_validator(sqs_client) -> None:
    class Validator(BaseModel):
        id: str
        name: str

    async_mock_function = AsyncMock(return_value=None)

    async def my_task(data: Validator) -> None:
        await async_mock_function(data)

    task_params = dict(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )
    # Invalid body, not execute function
    await sqs_client.send_message(
        MessageBody=json.dumps(dict(foo='bar')),
        MessageGroupId='4321',
    )
    await task(**task_params)(my_task)()
    assert async_mock_function.call_count == 0
    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp

    # Body approve validator, function receive Validator
    test_message = Validator(id='abc123', name='fast-agave')
    await sqs_client.send_message(
        MessageBody=test_message.json(),
        MessageGroupId='1234',
    )
    await task(**task_params)(my_task)()
    async_mock_function.assert_called_with(test_message)
    assert async_mock_function.call_count == 1

    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp
    assert len(BACKGROUND_TASKS) == 0


async def test_execute_tasks_with_union_validator(sqs_client) -> None:
    class User(BaseModel):
        id: str
        name: str

    class Company(BaseModel):
        id: str
        legal_name: str
        rfc: str

    async_mock_function = AsyncMock(return_value=None)

    async def my_task(data: Union[User, Company]) -> None:
        await async_mock_function(data.model_dump())

    task_params = dict(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )
    # Invalid body, not execute function
    test_message = dict(id='ID123', name='Sor Juana Inés de la Cruz')
    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='4321',
    )
    await task(**task_params)(my_task)()
    async_mock_function.assert_called_with(test_message)
    assert async_mock_function.call_count == 1

    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp
    assert len(BACKGROUND_TASKS) == 0

    async_mock_function.reset_mock()
    test_message = dict(id='ID123', legal_name='FastAgave', rfc='FA')

    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='54321',
    )
    await task(**task_params)(my_task)()
    async_mock_function.assert_called_with(test_message)
    assert async_mock_function.call_count == 1

    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp
    assert len(BACKGROUND_TASKS) == 0


async def test_not_execute_tasks(sqs_client) -> None:
    """
    Este caso es cuando el queue está vacío. No hay nada que ejecutar
    """
    async_mock_function = AsyncMock()

    async def my_task(data: dict) -> None:
        await async_mock_function(data)

    # No escribimos un mensaje en el queue
    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )(my_task)()
    async_mock_function.assert_not_called()
    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp
    assert len(BACKGROUND_TASKS) == 0


async def test_http_client_error_tasks(sqs_client) -> None:
    """
    Este test prueba el caso cuando hay un error de conexión al intentar
    obtener recibir el mensaje del queue. Se maneja correctamente la
    excepción `HTTPClientError` para evitar que el loop que consume mensajes
    se rompe inesperadamente.
    """

    test_message = dict(id='abc123', name='fast-agave')

    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='1234',
    )

    original_create_client = aiobotocore.client.AioClientCreator.create_client

    # Esta función hace un patch de la función `receive_message` para simular
    # un error de conexión, la recuperación de la conexión y posteriores
    # recepciones de mensajes sin body del queue.
    async def mock_create_client(*args, **kwargs):
        client = await original_create_client(*args, **kwargs)
        client.receive_message = AsyncMock(
            side_effect=[
                HTTPClientError(error='[Errno 104] Connection reset by peer'),
                await sqs_client.receive_message(),
                dict(),
                dict(),
                dict(),
            ]
        )
        return client

    async_mock_function = AsyncMock(return_value=None)

    async def my_task(data: dict) -> None:
        await async_mock_function(data)

    with patch(
        'aiobotocore.client.AioClientCreator.create_client', mock_create_client
    ):
        await task(
            queue_url=sqs_client.queue_url,
            region_name=CORE_QUEUE_REGION,
            wait_time_seconds=1,
            visibility_timeout=3,
            max_retries=1,
        )(my_task)()
        async_mock_function.assert_called_once()


async def test_retry_tasks_default_max_retries(sqs_client) -> None:
    """
    Este test prueba la lógica de reintentos con la configuración default,
    es decir `max_retries=1`

    En este caso el task debe ejecutarse 2 veces
    (la ejecución normal + max_retries)

    Se ejecuta este número de veces para ser consistentes con la lógica
    de reintentos de Celery
    """
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
    )(my_task)()

    expected_calls = [call(test_message)] * 2
    async_mock_function.assert_has_calls(expected_calls)
    assert async_mock_function.call_count == len(expected_calls)

    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp


async def test_retry_tasks_custom_max_retries(sqs_client) -> None:
    """
    Este test prueba la lógica de reintentos con la configuración default,
    es decir `max_retries=2`

    En este caso el task debe ejecutarse 3 veces
    (la ejecución normal + max_retries)
    """
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

    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp
    assert len(BACKGROUND_TASKS) == 0


async def test_does_not_retry_on_unhandled_exceptions(sqs_client) -> None:
    """
    Este caso prueba que las excepciones no controladas no se reintentan por
    default (comportamiento consistente con Celery)

    Dentro de task deben manejarse las excepciones esperadas (como desconexión
    de la red). Véase los ejemplos de cómo aplicar este tipo de reintentos
    """
    test_message = dict(id='abc123', name='fast-agave')
    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='1234',
    )

    async_mock_function = AsyncMock(
        side_effect=Exception('something went wrong :(')
    )

    async def my_task(data: dict) -> None:
        await async_mock_function(data)

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
        max_retries=3,
    )(my_task)()

    async_mock_function.assert_called_with(test_message)
    assert async_mock_function.call_count == 1

    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp
    assert len(BACKGROUND_TASKS) == 0


async def test_retry_tasks_with_countdown(sqs_client) -> None:
    """
    Este test prueba la lógica de reintentos con un countdown,
    es decir, se modifica el visibility timeout del mensaje para que pueda
    simularse un delay en la recepción del mensaje por el siguiente
    `receive_message`

    En este caso el task debe ejecutarse 2 veces
    (la ejecución normal + 1 intento), sin embargo,
    después de ejecutarse por primera vez deben pasar aprox 2 segundos
    para que se ejecute el primer intento

    El parámetro es similar a `self.retry(exc, countdown=10)` en celery
    """
    test_message = dict(id='abc123', name='fast-agave')

    await sqs_client.send_message(
        MessageBody=json.dumps(test_message),
        MessageGroupId='1234',
    )

    async_mock_function = AsyncMock(side_effect=RetryTask(countdown=2))

    async def countdown_tester(data: dict):
        await async_mock_function(data, dt.datetime.now())

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )(countdown_tester)()

    call_times = [arg[1] for arg, _ in async_mock_function.call_args_list]
    assert async_mock_function.call_count == 2
    assert call_times[1] - call_times[0] >= dt.timedelta(seconds=2)
    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp


async def test_concurrency_controller(
    sqs_client,
) -> None:
    message_id = str(uuid.uuid4())
    test_message = dict(id=message_id, name='fast-agave')
    for i in range(5):
        await sqs_client.send_message(
            MessageBody=json.dumps(test_message),
            MessageGroupId=message_id,
        )

    async_mock_function = AsyncMock()

    async def task_counter(data: dict) -> None:
        await asyncio.sleep(5)
        running_tasks = len(await get_running_fast_agave_tasks())
        await async_mock_function(running_tasks)

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
        max_retries=3,
        max_concurrent_tasks=2,
    )(task_counter)()

    running_tasks = [call[0] for call, _ in async_mock_function.call_args_list]
    assert max(running_tasks) == 2


async def test_invalid_json_message(sqs_client) -> None:
    """
    Este test verifica que los mensajes con JSON inválido son ignorados
    y el mensaje es eliminado del queue sin ejecutar el task
    """
    # Enviamos un mensaje con JSON inválido
    await sqs_client.send_message(
        MessageBody='{invalid_json',
        MessageGroupId='1234',
    )

    async_mock_function = AsyncMock()

    async def my_task(data: dict) -> None:
        await async_mock_function(data)

    await task(
        queue_url=sqs_client.queue_url,
        region_name=CORE_QUEUE_REGION,
        wait_time_seconds=1,
        visibility_timeout=1,
    )(my_task)()

    # Verificamos que el task nunca fue ejecutado
    async_mock_function.assert_not_called()

    # Verificamos que el mensaje fue eliminado del queue
    resp = await sqs_client.receive_message()
    assert 'Messages' not in resp
    assert len(BACKGROUND_TASKS) == 0
