"""
Simple in-memory cache with a Redis-ready interface placeholder.
"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, Tuple


class MemoryCache:
    def __init__(self) -> None:
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        expires, value = entry
        if expires and expires < time.time():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires = time.time() + ttl if ttl else 0
        self._store[key] = (expires, value)


cache = MemoryCache()
