import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from recommender.database import get_db
from recommender.models import TaskStatus

logger = logging.getLogger(__name__)


async def create_task(search_query: str, request_id: str) -> TaskStatus:
    db: Session = next(get_db())
    try:
        task = TaskStatus(
            request_id=request_id,
            search_query=search_query,
            status="processing",
            progress=0,
        )
        db.add(task)
        db.commit()
        return task
    finally:
        db.close()


async def update_task_status(
    request_id: str,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    error: Optional[str] = None,
    data: Optional[dict] = None,
) -> TaskStatus:
    db: Session = next(get_db())
    try:
        task = (
            db.query(TaskStatus)
            .filter(TaskStatus.request_id == request_id)
            .first()
        )
        if task:
            if status:
                task.status = status
            if progress is not None:
                task.progress = progress
            if error:
                task.error = error
            if data:
                task.data = data
            task.updated_at = func.now()
            db.commit()
        return task
    finally:
        db.close()


async def get_task_status(request_id: str) -> Optional[TaskStatus]:
    db: Session = next(get_db())
    try:
        return (
            db.query(TaskStatus)
            .filter(TaskStatus.request_id == request_id)
            .first()
        )
    finally:
        db.close()


async def cleanup_old_tasks():
    db: Session = next(get_db())
    try:
        # Delete tasks older than 1 hour
        cutoff = datetime.utcnow() - timedelta(hours=1)
        db.query(TaskStatus).filter(
            and_(
                TaskStatus.created_at < cutoff,
                TaskStatus.status.in_(["complete", "error"]),
            )
        ).delete()
        db.commit()
    finally:
        db.close()
