from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import JobStatus, Task
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.utils.retry import retry_with_backoff

router = APIRouter()


async def get_task_or_404(session: AsyncSession, task_id: str) -> Task:
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, session: AsyncSession = Depends(get_db)) -> TaskOut:
    task = Task(
        id=data.id,
        name=data.name,
        payload=data.payload,
        status=JobStatus.PENDING,
        max_retries=data.max_retries,
    )
    session.add(task)
    await session.flush()
    await session.refresh(task)
    return TaskOut.model_validate(task)


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    status_filter: JobStatus | None = None,
    session: AsyncSession = Depends(get_db),
) -> list[TaskOut]:
    query = select(Task)
    if status_filter:
        query = query.where(Task.status == status_filter)
    query = query.order_by(Task.created_at.desc())
    result = await session.execute(query)
    tasks = result.scalars().all()
    return [TaskOut.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, session: AsyncSession = Depends(get_db)) -> TaskOut:
    task = await get_task_or_404(session, task_id)
    return TaskOut.model_validate(task)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    session: AsyncSession = Depends(get_db),
) -> TaskOut:
    task = await get_task_or_404(session, task_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = datetime.now(timezone.utc)
    await session.flush()
    await session.refresh(task)
    return TaskOut.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, session: AsyncSession = Depends(get_db)) -> None:
    task = await get_task_or_404(session, task_id)
    await session.delete(task)
    await session.flush()