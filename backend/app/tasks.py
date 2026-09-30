import logging
from datetime import datetime, timezone
from typing import Any

from celery import current_task
from celery.utils.log import get_task_logger

from app.celery_app import celery_app
from app.db import get_session
from app.models import JobStatus, Task
from app.utils.retry import retry_with_backoff

logger = get_task_logger(__name__)


@celery_app.task(bind=True, name="tasks.process_task", max_retries=3)
def process_task(self: Any, task_id: str, payload: dict) -> dict:
    """Sample task with retry logic."""
    logger.info("Processing task %s with payload %s", task_id, payload)

    @retry_with_backoff(max_retries=3, base_delay=1)
    def _do_work() -> dict:
        # Simulate work that may fail
        import random

        if random.random() < 0.3:
            raise RuntimeError("Simulated transient failure")
        return {"processed": True, "task_id": task_id, "result": "ok"}

    try:
        result = _do_work()
        logger.info("Task %s completed successfully", task_id)
        return result
    except Exception as exc:
        logger.error("Task %s failed: %s", task_id, exc)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(bind=True, name="tasks.health_check")
def health_check(self: Any) -> dict:
    """Simple health check task."""
    logger.info("Health check task executed")
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


async def update_task_status(
    task_id: str, status: JobStatus, error: str | None = None
) -> None:
    """Update task status in the database."""
    async with get_session() as session:
        try:
            from sqlalchemy import select

            result = await session.execute(select(Task).where(Task.id == task_id))
            row = result.scalar_one_or_none()
            if row is None:
                logger.warning("Task %s not found for status update", task_id)
                return
            row.status = status
            row.updated_at = datetime.now(timezone.utc)
            if error:
                row.error = error
            if status == JobStatus.COMPLETED:
                row.completed_at = datetime.now(timezone.utc)
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("Failed to update task %s status", task_id)
            raise
        finally:
            await session.close()