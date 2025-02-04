import asyncio

import mongomock as mongomock
from cuenca_validations.errors import NoPasswordFoundError
from fastapi import APIRouter, FastAPI, HTTPException
from mongoengine import connect

from agave.fastapi.middlewares import AgaveErrorHandler
from agave.fastapi.middlewares.loggin_route import LoggingRoute

from ..tasks.task_example import dummy_task, task_validator
from .middlewares import AuthedMiddleware
from .resources import app as resources

connect(
    host='mongodb://localhost:27017/db',
    mongo_client_class=mongomock.MongoClient,
)
app = FastAPI(title='example')

router = APIRouter(route_class=LoggingRoute)

app.include_router(resources)


app.add_middleware(AuthedMiddleware)
app.add_middleware(AgaveErrorHandler)


@app.get('/')
async def iam_healty() -> dict:
    return dict(greeting="I'm healthy!!!")


@router.post("/simulate_400")
def simulate_bad_request():
    """Simulated endpoint that raises a bad request error (400)."""
    raise HTTPException(status_code=400, detail="Intentional bad request")


@router.post("/simulate_500")
def simulate_internal_error():
    """Simulated endpoint that raises an internal server error (500)."""
    raise RuntimeError("Intentional server error")


@router.post("/simulate_401")
def simulate_unauthorized():
    """Simulated endpoint that raises an unauthorized error (401)."""
    raise NoPasswordFoundError('Password not set')


app.include_router(router)


@app.on_event('startup')
async def on_startup() -> None:  # pragma: no cover
    # Inicializa el task que recibe mensajes
    # provenientes de SQS
    asyncio.create_task(dummy_task())
    asyncio.create_task(task_validator())
