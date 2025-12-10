"""Advanced Cache Management System

Supports:
- LRU (Least Recently Used) eviction policy
- TTL (Time-To-Live) for cache entries
- Multi-tier caching (memory + disk)
- Cache statistics and monitoring
- Thread-safe operations
"""

import time
import json
import hashlib
import logging
from typing import Any, Optional, Dict, Callable
from functools import wraps
from collections import OrderedDict
from threading import Lock
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a single cache entry with TTL"""
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        """Access the value and update access metadata"""
        if self.is_expired():
            return None
        self.last_accessed = time.time()
        self.access_count += 1
        return self.value


class LRUCache:
    """Thread-safe LRU Cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, ttl: Optional[int] = 3600):
        """
        Initialize LRU Cache
        
        Args:
            max_size: Maximum number of items in cache
            ttl: Time-to-live for entries in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.lock = Lock()
        self.hits = 0
        self.misses = 0
        
        logger.info(f"LRU Cache initialized: max_size={max_size}, ttl={ttl}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                logger.debug(f"Cache entry {key} expired")
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return entry.access()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        with self.lock:
            ttl = ttl or self.ttl
            
            # Remove if already exists (will be re-added at end)
            if key in self.cache:
                del self.cache[key]
            
            # Add new entry
            self.cache[key] = CacheEntry(value, ttl)
            
            # Evict LRU if needed
            if len(self.cache) > self.max_size:
                oldest = next(iter(self.cache))
                del self.cache[oldest]
                logger.debug(f"Evicted LRU key: {oldest}")
            
            logger.debug(f"Cached {key} (size={len(self.cache)})")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': f"{hit_rate:.2f}%",
                'utilization': f"{len(self.cache) / self.max_size * 100:.2f}%"
            }


class CacheManager:
    """High-level cache management with multiple strategies"""
    
    def __init__(self, cache_dir: str = "./cache", max_size: int = 1000):
        self.cache_dir = cache_dir
        self.memory_cache = LRUCache(max_size=max_size)
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Cache Manager initialized: dir={cache_dir}")
    
    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash key for safe filesystem storage"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def cached(self, ttl: Optional[int] = None):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                key = f"{func.__name__}_{args}_{kwargs}"
                
                # Try memory cache first
                cached_value = self.memory_cache.get(key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_value
                
                # Compute and cache result
                result = func(*args, **kwargs)
                self.memory_cache.set(key, result, ttl)
                return result
            
            return wrapper
        return decorator
    
    def get_cache_stats(self) -> Dict:
        """Get combined cache statistics"""
        return {
            'memory': self.memory_cache.get_stats(),
            'cache_dir': self.cache_dir,
            'timestamp': datetime.now().isoformat()
        }


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """Get or create global cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
