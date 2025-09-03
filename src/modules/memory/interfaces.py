"""Interfaces for the memory module."""

from typing import Any, Dict, Iterable, List, Optional, Protocol, TypedDict


class MemoryRecord(TypedDict, total=False):
    id: str
    user_id: str
    app_id: Optional[str]
    agent_id: Optional[str]
    text: str
    metadata: Dict[str, Any]
    tags: List[str]
    created_at: str


class SearchResult(TypedDict):
    record: MemoryRecord
    score: float


class MemoryStore(Protocol):
    def add(
        self,
        *,
        user_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        app_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> MemoryRecord: ...

    def search(
        self,
        *,
        user_id: Optional[str] = None,
        query: Optional[str] = None,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]: ...

    def delete(self, *, memory_id: str) -> bool: ...
    
    def users(self) -> List[Dict[str, Any]]: ...
    
    def export(self, *, schema: Dict[str, Any], filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: ...