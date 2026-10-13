from typing import Optional

from fastapi import HTTPException, status as http_status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import MEMBER_ROLES, Project, ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate


def create_project(db: Session, payload: ProjectCreate, owner: User) -> Project:
    project = Project(name=payload.name, description=payload.description, owner_id=owner.id)
    db.add(project)
    db.flush()
    db.add(ProjectMember(project_id=project.id, user_id=owner.id, role="owner"))
    db.commit()
    db.refresh(project)
    return project


def get_membership(db: Session, project_id: int, user_id: int) -> Optional[ProjectMember]:
    return db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
    )


def require_membership(db: Session, project_id: int, user: User) -> ProjectMember:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Project not found")
    membership = get_membership(db, project_id, user.id)
    if membership is None and user.role != "admin":
        # Do not leak existence of projects the caller cannot access.
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Project not found")
    return membership


def list_projects(db: Session, user: User):
    stmt = (
        select(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == user.id)
        .order_by(Project.created_at.desc())
    )
    if user.role == "admin":
        stmt = select(Project).order_by(Project.created_at.desc())
    return list(db.scalars(stmt).unique().all())


def get_project(db: Session, project_id: int, user: User) -> Project:
    require_membership(db, project_id, user)
    project = db.get(Project, project_id)
    return project


def add_member(db: Session, project_id: int, user_id: int, role: str, actor: User) -> ProjectMember:
    require_membership(db, project_id, actor)
    if role not in MEMBER_ROLES:
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid member role")
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="User not found")
    if get_membership(db, project_id, user_id) is not None:
        raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail="User is already a member")
    member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
