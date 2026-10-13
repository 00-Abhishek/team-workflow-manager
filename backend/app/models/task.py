from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base

TASK_STATUSES = ("To Do", "In Progress", "In Review", "Done")
PRIORITIES = ("Low", "Medium", "High", "Urgent")

# Allowed workflow transitions. Anything not listed is rejected.
STATUS_TRANSITIONS = {
    "To Do": ("In Progress",),
    "In Progress": ("In Review", "To Do"),
    "In Review": ("Done", "In Progress"),
    "Done": ("In Progress",),
}


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False, default="")
    status = Column(String(20), nullable=False, default="To Do")
    priority = Column(String(20), nullable=False, default="Medium")
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[created_by])
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tasks_project_status", "project_id", "status"),
        Index("ix_tasks_assignee", "assignee_id"),
        Index("ix_tasks_due_date", "due_date"),
    )
