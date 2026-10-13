from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.project import MemberAdd, MemberOut, ProjectCreate, ProjectDetail, ProjectOut, ProjectSummary
from app.services import project_service, task_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return project_service.create_project(db, payload, user)


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return project_service.list_projects(db, user)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return project_service.get_project(db, project_id, user)


@router.post("/{project_id}/members", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: int,
    payload: MemberAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return project_service.add_member(db, project_id, payload.user_id, payload.role, user)


@router.get("/{project_id}/summary", response_model=ProjectSummary)
def summary(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return task_service.project_summary(db, project_id, user)
