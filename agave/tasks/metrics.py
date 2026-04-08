from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class TaskMetrics:
    task_name: str
    queue_url: str
    concurrent_tasks_counter: Callable[[], int]


async def emit_metrics(
    metrics: TaskMetrics,
    status: str,
    duration_ms: float,
    metrics_callback: Optional[Callable] = None,
) -> None:
    if not metrics_callback:
        return
    await metrics_callback(
        task_name=metrics.task_name,
        queue_url=metrics.queue_url,
        status=status,
        duration_ms=duration_ms,
        concurrent_tasks=metrics.concurrent_tasks_counter(),
    )
