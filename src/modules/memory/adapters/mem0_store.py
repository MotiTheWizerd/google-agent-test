"""Mem0 adapter for the memory module."""

from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional
from mem0 import MemoryClient  # SDK
from ..interfaces import MemoryStore, MemoryRecord, SearchResult
from ..config import Mem0Config
from ..errors import Mem0Error, Mem0AuthError, Mem0NotFound, Mem0RateLimited
from ..utils.retry import with_retry


class Mem0Store(MemoryStore):
    """Mem0 implementation of the MemoryStore interface."""

    def __init__(self, cfg: Mem0Config):
        if not cfg.api_key:
            raise Mem0AuthError("Missing MEM0_API_KEY")
        self._client = MemoryClient(
            api_key=cfg.api_key,
            org_id=cfg.org_id,
            project_id=cfg.project_id,
        )

    # ---- create
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
    ) -> MemoryRecord:
        # Prepare the message in the format expected by Mem0
        messages = [{"role": "user", "content": text}]
        
        # Prepare additional parameters
        params: Dict[str, Any] = {
            "user_id": user_id,
            "metadata": metadata or {},
            "tags": list(tags) if tags else [],
            "output_format": "v1.1"  # Use the new output format to avoid deprecation warning
        }
        
        if app_id: 
            params["app_id"] = app_id
        if agent_id: 
            params["agent_id"] = agent_id
        if run_id: 
            params["run_id"] = run_id
        if source: 
            params["source"] = source

        def _call():
            # The SDK exposes memory operations via the client; exact method names
            # can vary by minor version; prefer documented endpoints.
            return self._client.add(messages=messages, **params)  # returns dict

        try:
            data = with_retry(_call)
            return data  # conforms to MemoryRecord-ish dict
        except Exception as e:
            raise _translate(e)

    # ---- search
    def search(
        self,
        *,
        user_id: Optional[str] = None,
        query: Optional[str] = None,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        # Mem0 search requires a query parameter
        search_query = query if query is not None else ""
            
        params: Dict[str, Any] = {
            "limit": k,
            "output_format": "v1.1"  # Use the new output format to avoid deprecation warning
        }
        if user_id: 
            params["user_id"] = user_id
        if filters: 
            params["filters"] = filters

        def _call():
            results = self._client.search(query=search_query, **params)
            # Convert to the expected format: [{"record": {...}, "score": 0.xx}, ...]
            formatted_results = []
            for result in results:
                # Mem0 returns results in a different format, we need to adapt
                if isinstance(result, dict) and 'memory' in result:
                    # New format
                    memory = result['memory']
                    formatted_results.append({
                        "record": memory,
                        "score": result.get('score', 0.0)
                    })
                else:
                    # Old format or direct memory object
                    formatted_results.append({
                        "record": result,
                        "score": 1.0  # Default score
                    })
            return formatted_results

        try:
            return with_retry(_call)
        except Exception as e:
            raise _translate(e)

    # ---- delete
    def delete(self, *, memory_id: str) -> bool:
        def _call():
            return self._client.delete(memory_id)
        try:
            res = with_retry(_call)
            return bool(res.get("success", False)) if isinstance(res, dict) else bool(res)
        except Exception as e:
            raise _translate(e)

    # ---- list users
    def users(self) -> List[Dict[str, Any]]:
        def _call():
            return self._client.users()
        try:
            return with_retry(_call)
        except Exception as e:
            raise _translate(e)

    # ---- export
    def export(self, *, schema: Dict[str, Any], filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        def _call():
            return self._client.create_memory_export(json_schema=schema, filters=filters or {})
        try:
            return with_retry(_call)
        except Exception as e:
            raise _translate(e)


def _translate(e: Exception) -> Mem0Error:
    """Translate Mem0 SDK exceptions to our custom exceptions."""
    msg = str(e).lower()
    if "401" in msg or "unauthorized" in msg:
        return Mem0AuthError(str(e))
    if "404" in msg:
        return Mem0NotFound(str(e))
    if "429" in msg or "rate limit" in msg:
        return Mem0RateLimited(str(e))
    return Mem0Error(str(e))