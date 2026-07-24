"""Conversation domain DTOs (M7). Maps to tables `conversations`, `messages`."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

ConversationTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
]


class ConversationSummary(BaseModel):
    id: str
    project_id: str
    title: str | None = None
    created_at: datetime


class ConversationMessage(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


class ConversationListResponse(BaseModel):
    items: list[ConversationSummary] = Field(default_factory=list)


class ConversationMessagesResponse(BaseModel):
    items: list[ConversationMessage] = Field(default_factory=list)


class ConversationCreate(BaseModel):
    project_id: str = Field(min_length=1)
    title: ConversationTitle | None = None


class ConversationUpdate(BaseModel):
    title: ConversationTitle
