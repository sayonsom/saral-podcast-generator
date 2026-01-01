"""Data models for blogs and episodes."""
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class Blog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: str  # markdown
    summary: str | None = None
    tags: list[str] = []
    key_facts: list[str] = []
    created_at: datetime = Field(default_factory=_utc_now)


class BlogAnalysis(BaseModel):
    key_facts: list[str]
    main_arguments: list[str]
    stakeholders: list[str]
    controversy_points: list[str]
    regulatory_hooks: list[str]


class Insights(BaseModel):
    utilities: list[str] = []
    consumers: list[str] = []
    startups: list[str] = []
    regulatory: list[str] = []
    expert_questions: list[str] = []


class GenerationSettings(BaseModel):
    duration: Literal["short", "medium", "long"] = "medium"  # 10, 20, 30 min
    humor_level: int = Field(default=3, ge=1, le=5)
    focus_areas: list[str] = []
    custom_talking_points: list[str] = []


class Episode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    blog_id: str
    title: str
    script: str
    duration_estimate: int = 20  # minutes
    humor_level: int = 3
    focus_areas: list[str] = []
    summary: str = ""  # for callbacks in future episodes
    insights: Insights = Field(default_factory=Insights)
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)


class Character(BaseModel):
    name: str
    role: str
    background: str
    political_lean: str
    speech_patterns: list[str]
    catchphrases: list[str]
    expertise_areas: list[str]
