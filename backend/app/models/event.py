from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class TaskEvent(Base):
    __tablename__ = "task_events"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # e.g. created, status_changed, assigned, priority_changed, due_date_changed, commented
    event_type = Column(String(40), nullable=False)
    detail = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    task = relationship("Task", back_populates="events")
    actor = relationship("User")

    __table_args__ = (Index("ix_task_events_task_created", "task_id", "created_at"),)
