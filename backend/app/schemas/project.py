from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: str = ""


class MemberAdd(BaseModel):
    user_id: int
    role: str = "member"


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role: str


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime


class ProjectDetail(ProjectOut):
    members: list[MemberOut] = []


class ProjectSummary(BaseModel):
    project_id: int
    total: int
    to_do: int
    in_progress: int
    in_review: int
    done: int
    overdue: int
