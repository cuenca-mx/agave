import asyncio
from typing import Dict

import mongomock as mongomock
from fastapi import FastAPI
from mongoengine import connect

from agave.fastapi_support.middlewares import FastAgaveErrorHandler

from .middlewares import AuthedMiddleware
from .resources import app as resources
from .tasks.task_example import dummy_task, task_validator

connect(
    host='mongodb://localhost:27017/db',
    is_mock=True,
    alias='fast_connection',
)
app = FastAPI(title='example')
app.include_router(resources)

app.add_middleware(AuthedMiddleware)
app.add_middleware(FastAgaveErrorHandler)


@app.get('/')
async def iam_healty() -> Dict:
    return dict(greeting="I'm healthy!!!")


@app.on_event('startup')
async def on_startup() -> None:  # pragma: no cover
    # Inicializa el task que recibe mensajes
    # provenientes de SQS
    asyncio.create_task(dummy_task())
    asyncio.create_task(task_validator())
