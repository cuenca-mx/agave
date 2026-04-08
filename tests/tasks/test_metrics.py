from unittest.mock import AsyncMock

from agave.tasks.metrics import TaskMetrics, emit_metrics

TASK_NAME = 'my_task'
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/queue'


async def test_emit_metrics_calls_callback() -> None:
    callback = AsyncMock()
    metrics = TaskMetrics(
        task_name=TASK_NAME,
        queue_url=QUEUE_URL,
        concurrent_tasks_counter=lambda: 3,
    )

    await emit_metrics(
        metrics=metrics,
        status='success',
        duration_ms=150.5,
        metrics_callback=callback,
    )

    callback.assert_called_once_with(
        task_name=TASK_NAME,
        queue_url=QUEUE_URL,
        status='success',
        duration_ms=150.5,
        concurrent_tasks=3,
    )


async def test_emit_metrics_skips_when_no_callback() -> None:
    metrics = TaskMetrics(
        task_name=TASK_NAME,
        queue_url=QUEUE_URL,
        concurrent_tasks_counter=lambda: 0,
    )
    await emit_metrics(
        metrics=metrics,
        status='success',
        duration_ms=100.0,
    )
