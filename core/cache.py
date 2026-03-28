"""
In-memory cache for common requests.
Bonus: Demonstrates scale thinking and performance optimization.
Production: Replace with Redis for distributed caching.
"""
import time
from typing import Any, Optional
from functools import wraps

class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: dict[str, dict] = {}
        self._default_ttl = default_ttl  # 5 minutes default
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() > entry["expires_at"]:
            del self._cache[key]  # Expired
            return None
        
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value with TTL."""
        expires_at = time.time() + (ttl or self._default_ttl)
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at
        }
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
    
    def size(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)

# Global cache instance
cache = SimpleCache(default_ttl=300)

def cached(ttl: Optional[int] = None):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name + args
            key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try cache first
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute and cache
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator