"""
models.py — Pydantic v2 request/response models for SceneForge.
"""

from typing import Any, List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    project_id: str
    history: List[dict[str, Any]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    sources: List[dict]


class UploadResponse(BaseModel):
    success: bool
    filename: str
    chunks_created: int
    message: str


class ProjectMemoryResponse(BaseModel):
    memories: List[str]
