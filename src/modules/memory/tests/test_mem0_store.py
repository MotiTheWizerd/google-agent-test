"""Tests for the Mem0 adapter."""

import types
from mem0_wrapper.adapters.mem0_store import Mem0Store
from mem0_wrapper.config import Mem0Config


class FakeClient:
    """Fake Mem0 client for testing."""
    
    def __init__(self, *a, **k):
        self._mem = []
        self._id = 0
        
    def add(self, messages, **kw):
        self._id += 1
        text = messages[0]["content"] if messages and isinstance(messages, list) and "content" in messages[0] else ""
        rec = {"id": str(self._id), "text": text, "created_at": "2025-09-03T00:00:00Z", **kw}
        self._mem.append(rec)
        return rec
        
    def search(self, query, **kw):
        return [{"record": m, "score": 0.9} for m in self._mem[: kw.get("limit", 10)]]
        
    def delete(self, mid):
        return {"success": True}
        
    def users(self): 
        return [{"user_id": "u1"}]
        
    def create_memory_export(self, **kw): 
        return {"export": []}


def test_add_and_search(monkeypatch):
    """Test adding and searching memories."""
    cfg = Mem0Config(api_key="x")
    store = Mem0Store.__new__(Mem0Store)
    store._client = FakeClient()  # monkeypatch
    rec = store.add(user_id="u1", text="I like window seats")
    assert rec["user_id"] == "u1"
    hits = store.search(user_id="u1", query="seats", k=1)
    assert hits and hits[0]["record"]["text"].startswith("I like")