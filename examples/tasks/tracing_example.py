from pydantic import BaseModel

from agave.core.tracing import (
    accept_trace_from_queue,
    add_custom_attribute,
    background_task,
    get_trace_headers,
    inject_trace_headers,
    trace_attributes,
)
from agave.tasks.sqs_tasks import task

# Esta URL es solo un mock de la queue.
# Debes reemplazarla con la URL de tu queue
QUEUE_URL = "http://127.0.0.1:4000/123456789012/core.fifo"


class Abono(BaseModel):
    clave_rastreo: str
    clave_emisor: str
    monto: float


async def process_order(order: Abono) -> None:
    with background_task(name="process_order", group="Orders"):
        add_custom_attribute("order_id", order.clave_rastreo)
        print(f"Processing order: {order.clave_rastreo}")


async def send_to_external_service(order: Abono) -> None:
    headers = get_trace_headers()
    print(f"Sending with headers: {headers}")


@inject_trace_headers()
async def request(
    method: str, endpoint: str, trace_headers: dict | None = None
) -> None:
    # trace_headers ya contiene los headers de New Relic
    print(f"{method} {endpoint} with headers: {trace_headers}")


@task(queue_url=QUEUE_URL, region_name="us-east-1")
@accept_trace_from_queue
async def process_incoming_transaction(transaction: dict) -> None:
    print(f"Processing: {transaction}")


@trace_attributes(
    clave_rastreo="order.clave_rastreo",
    clave_emisor="order.clave_emisor",
    monto=lambda kw: f"{kw['order'].monto:.2f}",
)
async def handle_order(order: Abono, folio: str) -> None:
    print(f"Handling order {folio}: {order.clave_rastreo}")


async def process_from_queue(message: dict, trace_headers: dict) -> None:
    with background_task(
        name="process_from_queue",
        group="Queue",
        trace_headers=trace_headers,
    ):
        print(f"Processing message: {message}")
