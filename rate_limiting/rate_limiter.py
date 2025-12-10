"""Rate Limiter Module

Provides API rate limiting and request throttling for protecting against abuse
and ensuring fair usage of resources. Implements token bucket and sliding window
algorithms.
"""

import time
import logging
from collections import defaultdict, deque
from threading import Lock
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """Token Bucket algorithm-based rate limiter.
    
    Allows burst traffic up to the bucket capacity while maintaining
    a steady-state rate of token replenishment.
    """
    
    def __init__(self, rate: int, capacity: int):
        """Initialize token bucket rate limiter.
        
        Args:
            rate: Number of tokens added per second
            capacity: Maximum tokens in the bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = Lock()
    
    def allow_request(self) -> bool:
        """Check if a request is allowed under the rate limit.
        
        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


class SlidingWindowRateLimiter:
    """Sliding window-based rate limiter.
    
    Tracks requests in a moving time window for precise rate limiting.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """Initialize sliding window rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = Lock()
    
    def allow_request(self) -> bool:
        """Check if a request is allowed under the rate limit.
        
        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Remove requests outside the window
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False


class PerClientRateLimiter:
    """Per-client rate limiting with configurable strategies."""
    
    def __init__(self, strategy: str = 'token_bucket',
                 rate: int = 100, capacity: int = 200):
        """Initialize per-client rate limiter.
        
        Args:
            strategy: 'token_bucket' or 'sliding_window'
            rate: Rate parameter (tokens/sec or requests for window)
            capacity: Capacity parameter (bucket size or window duration)
        """
        self.strategy = strategy
        self.rate = rate
        self.capacity = capacity
        self.limiters: Dict[str, object] = {}
        self.lock = Lock()
    
    def allow_request(self, client_id: str) -> bool:
        """Check if a client's request is allowed.
        
        Args:
            client_id: Unique client identifier (IP, user_id, etc.)
            
        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            if client_id not in self.limiters:
                if self.strategy == 'token_bucket':
                    self.limiters[client_id] = TokenBucketRateLimiter(
                        self.rate, self.capacity
                    )
                else:  # sliding_window
                    self.limiters[client_id] = SlidingWindowRateLimiter(
                        self.rate, self.capacity
                    )
            
            limiter = self.limiters[client_id]
            return limiter.allow_request()
    
    def get_limiter_stats(self, client_id: str) -> Dict:
        """Get rate limiter statistics for a client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dictionary with limiter statistics
        """
        with self.lock:
            if client_id not in self.limiters:
                return {'status': 'no_data'}
            
            limiter = self.limiters[client_id]
            if isinstance(limiter, TokenBucketRateLimiter):
                return {
                    'strategy': 'token_bucket',
                    'tokens': limiter.tokens,
                    'capacity': limiter.capacity,
                    'rate': limiter.rate
                }
            else:
                return {
                    'strategy': 'sliding_window',
                    'requests_in_window': len(limiter.requests),
                    'max_requests': limiter.max_requests,
                    'window_seconds': limiter.window_seconds
                }


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts limits based on system load."""
    
    def __init__(self, base_rate: int = 100, 
                 load_factor: float = 1.0):
        """Initialize adaptive rate limiter.
        
        Args:
            base_rate: Base rate limit
            load_factor: System load factor (1.0 = normal)
        """
        self.base_rate = base_rate
        self.load_factor = load_factor
        self.effective_rate = int(base_rate * load_factor)
        self.per_client = PerClientRateLimiter(
            strategy='token_bucket',
            rate=self.effective_rate,
            capacity=self.effective_rate * 2
        )
        self.lock = Lock()
    
    def update_load_factor(self, factor: float) -> None:
        """Update system load factor.
        
        Args:
            factor: New load factor (affects rate limiting)
        """
        with self.lock:
            self.load_factor = factor
            self.effective_rate = max(10, int(self.base_rate * factor))
            logger.info(f'Updated load factor to {factor}, effective rate: {self.effective_rate}')
    
    def allow_request(self, client_id: str) -> bool:
        """Check if request is allowed under adaptive limits.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if request is allowed, False otherwise
        """
        return self.per_client.allow_request(client_id)


def get_client_ip(request) -> str:
    """Extract client IP from Flask/FastAPI request.
    
    Args:
        request: HTTP request object
        
    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header for proxy chains
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or 'unknown'
