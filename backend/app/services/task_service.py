from datetime import date
from typing import Optional

from fastapi import HTTPException, status as http_status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.event import TaskEvent
from app.models.task import PRIORITIES, STATUS_TRANSITIONS, TASK_STATUSES, Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.project_service import get_membership, require_membership


def _record(db: Session, task_id: int, actor_id: Optional[int], event_type: str, detail: str = None):
    db.add(TaskEvent(task_id=task_id, actor_id=actor_id, event_type=event_type, detail=detail))


def _validate_enum(value: str, allowed, field: str):
    if value not in allowed:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {field} '{value}'. Allowed: {', '.join(allowed)}",
        )


def _assert_assignee_is_member(db: Session, project_id: int, assignee_id: int):
    if get_membership(db, project_id, assignee_id) is None:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A task can only be assigned to a member of its project",
        )


def create_task(db: Session, project_id: int, payload: TaskCreate, actor: User) -> Task:
    require_membership(db, project_id, actor)
    _validate_enum(payload.status, TASK_STATUSES, "status")
    _validate_enum(payload.priority, PRIORITIES, "priority")
    if payload.status != "To Do":
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New tasks must start in 'To Do'",
        )
    if payload.assignee_id is not None:
        _assert_assignee_is_member(db, project_id, payload.assignee_id)

    task = Task(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        status="To Do",
        priority=payload.priority,
        assignee_id=payload.assignee_id,
        created_by=actor.id,
        due_date=payload.due_date,
    )
    db.add(task)
    db.flush()
    _record(db, task.id, actor.id, "created", f"Task created by {actor.email}")
    if task.assignee_id:
        _record(db, task.id, actor.id, "assigned", f"Assigned to user #{task.assignee_id}")
    db.commit()
    db.refresh(task)
    return task


def get_task_for_user(db: Session, task_id: int, user: User) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    require_membership(db, task.project_id, user)
    return task


def list_tasks(
    db: Session,
    user: User,
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    due_before: Optional[date] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    limit = max(1, min(limit, 200))
    # Restrict to projects the user belongs to (admins see all).
    if project_id is not None:
        require_membership(db, project_id, user)

    from app.models.project import ProjectMember

    stmt = select(Task)
    if user.role != "admin":
        member_projects = select(ProjectMember.project_id).where(ProjectMember.user_id == user.id)
        stmt = stmt.where(Task.project_id.in_(member_projects))
    if project_id is not None:
        stmt = stmt.where(Task.project_id == project_id)
    if status:
        stmt = stmt.where(Task.status == status)
    if priority:
        stmt = stmt.where(Task.priority == priority)
    if assignee_id is not None:
        stmt = stmt.where(Task.assignee_id == assignee_id)
    if due_before is not None:
        stmt = stmt.where(Task.due_date.is_not(None), Task.due_date <= due_before)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(Task.title.ilike(like) | Task.description.ilike(like))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Task.created_at.desc()).limit(limit).offset(offset)
    return total, list(db.scalars(stmt).all())


def update_task(db: Session, task_id: int, payload: TaskUpdate, actor: User) -> Task:
    task = get_task_for_user(db, task_id, actor)

    if payload.status is not None and payload.status != task.status:
        _validate_enum(payload.status, TASK_STATUSES, "status")
        allowed = STATUS_TRANSITIONS.get(task.status, ())
        if payload.status not in allowed:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Illegal transition {task.status} -> {payload.status}. Allowed: {', '.join(allowed) or 'none'}",
            )
        _record(db, task.id, actor.id, "status_changed", f"{task.status} -> {payload.status}")
        task.status = payload.status

    if payload.priority is not None:
        _validate_enum(payload.priority, PRIORITIES, "priority")
        if payload.priority != task.priority:
            _record(db, task.id, actor.id, "priority_changed", f"{task.priority} -> {payload.priority}")
            task.priority = payload.priority

    if payload.assignee_id is not None:
        _assert_assignee_is_member(db, task.project_id, payload.assignee_id)
        if payload.assignee_id != task.assignee_id:
            _record(db, task.id, actor.id, "assigned", f"Assigned to user #{payload.assignee_id}")
            task.assignee_id = payload.assignee_id

    if payload.due_date is not None:
        _record(db, task.id, actor.id, "due_date_changed", f"{task.due_date} -> {payload.due_date}")
        task.due_date = payload.due_date

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description

    db.commit()
    db.refresh(task)
    return task


def add_comment(db: Session, task_id: int, body: str, author: User) -> Comment:
    task = get_task_for_user(db, task_id, author)
    comment = Comment(task_id=task.id, author_id=author.id, body=body)
    db.add(comment)
    _record(db, task.id, author.id, "commented", body[:200])
    db.commit()
    db.refresh(comment)
    return comment


def project_summary(db: Session, project_id: int, user: User) -> dict:
    require_membership(db, project_id, user)
    rows = db.execute(
        select(Task.status, func.count()).where(Task.project_id == project_id).group_by(Task.status)
    ).all()
    counts = {s: 0 for s in TASK_STATUSES}
    for status_value, count in rows:
        counts[status_value] = count
    overdue = db.scalar(
        select(func.count()).select_from(Task).where(
            Task.project_id == project_id,
            Task.due_date.is_not(None),
            Task.due_date < date.today(),
            Task.status != "Done",
        )
    ) or 0
    return {
        "project_id": project_id,
        "total": sum(counts.values()),
        "to_do": counts["To Do"],
        "in_progress": counts["In Progress"],
        "in_review": counts["In Review"],
        "done": counts["Done"],
        "overdue": overdue,
    }


def dashboard_summary(db: Session, user: User) -> dict:
    from app.models.project import ProjectMember

    member_projects = select(ProjectMember.project_id).where(ProjectMember.user_id == user.id)

    counts_stmt = select(Task.status, func.count()).group_by(Task.status)
    if user.role != "admin":
        counts_stmt = counts_stmt.where(Task.project_id.in_(member_projects))
    rows = db.execute(counts_stmt).all()
    counts = {s: 0 for s in TASK_STATUSES}
    for status_value, count in rows:
        counts[status_value] = count

    overdue_stmt = select(func.count()).select_from(Task).where(
        Task.due_date.is_not(None), Task.due_date < date.today(), Task.status != "Done"
    )
    if user.role != "admin":
        overdue_stmt = overdue_stmt.where(Task.project_id.in_(member_projects))
    overdue = db.scalar(overdue_stmt) or 0

    return {
        "to_do": counts["To Do"],
        "in_progress": counts["In Progress"],
        "in_review": counts["In Review"],
        "done": counts["Done"],
        "overdue": overdue,
        "total": sum(counts.values()),
    }
