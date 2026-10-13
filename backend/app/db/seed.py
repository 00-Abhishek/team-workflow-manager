"""Seed demo users, a project, members and tasks. Safe to run repeatedly."""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.project import Project, ProjectMember
from app.models.task import Task
from app.models.user import User

DEMO_USERS = [
    ("admin@example.com", "Ada Admin", "admin", "admin123"),
    ("lead@example.com", "Leah Lead", "user", "lead123"),
    ("dev@example.com", "Dev Member", "user", "dev123"),
]


def seed(db: Session) -> None:
    users = {}
    for email, name, role, password in DEMO_USERS:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, full_name=name, role=role, hashed_password=hash_password(password))
            db.add(user)
            db.flush()
        users[email] = user

    if db.scalar(select(Project).limit(1)) is None:
        lead = users["lead@example.com"]
        dev = users["dev@example.com"]
        project = Project(name="Website Launch", description="Marketing site relaunch", owner_id=lead.id)
        db.add(project)
        db.flush()
        db.add_all([
            ProjectMember(project_id=project.id, user_id=lead.id, role="owner"),
            ProjectMember(project_id=project.id, user_id=dev.id, role="member"),
        ])
        today = date.today()
        db.add_all([
            Task(project_id=project.id, title="Implement login form", description="Email + password login",
                 status="In Progress", priority="High", assignee_id=dev.id, created_by=lead.id,
                 due_date=today + timedelta(days=3)),
            Task(project_id=project.id, title="Design landing page", description="Hero + pricing sections",
                 status="To Do", priority="Medium", assignee_id=dev.id, created_by=lead.id,
                 due_date=today - timedelta(days=2)),
            Task(project_id=project.id, title="Set up CI", description="Build and test on push",
                 status="Done", priority="Low", created_by=lead.id),
        ])
    db.commit()
