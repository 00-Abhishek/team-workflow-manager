from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import CommentCreate, CommentOut, TaskCreate, TaskDetail, TaskList, TaskOut, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/api", tags=["tasks"])


@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.create_task(db, project_id, payload, user)


@router.get("/tasks", response_model=TaskList)
def list_tasks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    project_id: Optional[int] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    due_before: Optional[date] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    total, items = task_service.list_tasks(
        db,
        user,
        project_id=project_id,
        status=status_filter,
        priority=priority,
        assignee_id=assignee_id,
        due_before=due_before,
        search=search,
        limit=limit,
        offset=offset,
    )
    return TaskList(total=total, items=items)


@router.get("/tasks/{task_id}", response_model=TaskDetail)
def get_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return task_service.get_task_for_user(db, task_id, user)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.update_task(db, task_id, payload, user)


@router.post("/tasks/{task_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.add_comment(db, task_id, payload.body, user)
