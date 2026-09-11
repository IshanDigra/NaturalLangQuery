from typing import Dict, Any

_CACHE: Dict[str, Any] = {}

def get_cached(query: str) -> Any:
    return _CACHE.get(query.lower())

def set_cached(query: str, value: Any):
    _CACHE[query.lower()] = value

def reset_cache():
    _CACHE.clear()
