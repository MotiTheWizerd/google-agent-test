"""Data models for the memory module."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class MemoryRecordModel(BaseModel):
    """Model for a memory record."""
    id: Optional[str] = None
    user_id: str
    app_id: Optional[str] = None
    agent_id: Optional[str] = None
    text: str
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    created_at: Optional[str] = None


class SearchResultModel(BaseModel):
    """Model for a search result."""
    record: MemoryRecordModel
    score: float


class ExportSchemaModel(BaseModel):
    """Model for export schema."""
    title: str
    type: str
    properties: Dict[str, Dict[str, str]]
    required: List[str]