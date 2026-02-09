"""
Rate Limiting Middleware
Implements IP-based, user-based, and endpoint-based rate limiting
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import time
import hashlib
import logging

logger = logging.getLogger('gowheels.ratelimit')


class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    # Rate limit configurations
    RATE_LIMITS = {
        'default': {'requests': 100, 'window': 60},  # 100 req/min
        'auth': {'requests': 5, 'window': 60},       # 5 req/min for auth
        'api': {'requests': 1000, 'window': 3600},   # 1000 req/hour for API
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip rate limiting for health checks and OAuth callbacks
        if request.path in ['/health/', '/ready/'] or '/accounts/' in request.path:
            return self.get_response(request)
        
        # Determine rate limit type
        limit_type = self._get_limit_type(request.path)
        config = self.RATE_LIMITS.get(limit_type, self.RATE_LIMITS['default'])
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        allowed, remaining, reset_time = self._check_rate_limit(
            client_id, 
            limit_type,
            config['requests'],
            config['window']
        )
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_id} on {request.path}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'retry_after': int(reset_time - time.time())
            }, status=429, headers={
                'Retry-After': str(int(reset_time - time.time())),
                'X-RateLimit-Limit': str(config['requests']),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(int(reset_time))
            })
        
        # Process request
        response = self.get_response(request)
        
        # Add rate limit headers
        response['X-RateLimit-Limit'] = str(config['requests'])
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(int(reset_time))
        
        return response
    
    def _get_limit_type(self, path):
        """Determine rate limit type based on path"""
        if '/auth/' in path or '/login/' in path or '/register/' in path:
            return 'auth'
        elif path.startswith('/api/'):
            return 'api'
        return 'default'
    
    def _get_client_id(self, request):
        """Get unique client identifier"""
        # Use user ID if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        # Use IP address
        ip = self._get_client_ip(request)
        return f"ip:{ip}"
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _check_rate_limit(self, client_id, limit_type, max_requests, window):
        """Check if request is within rate limit"""
        cache_key = f"ratelimit:{limit_type}:{client_id}"
        
        # Get current request count and window start
        data = cache.get(cache_key, {'count': 0, 'start': time.time()})
        
        current_time = time.time()
        window_start = data['start']
        count = data['count']
        
        # Reset if window expired
        if current_time - window_start >= window:
            count = 0
            window_start = current_time
        
        # Check limit
        if count >= max_requests:
            reset_time = window_start + window
            return False, 0, reset_time
        
        # Increment count
        count += 1
        cache.set(cache_key, {'count': count, 'start': window_start}, window)
        
        remaining = max_requests - count
        reset_time = window_start + window
        
        return True, remaining, reset_time


class IPRateLimiter:
    """Simple IP-based rate limiter"""
    
    @staticmethod
    def is_allowed(ip: str, max_requests: int = 100, window: int = 60) -> bool:
        """Check if IP is within rate limit"""
        cache_key = f"ratelimit:ip:{ip}"
        count = cache.get(cache_key, 0)
        
        if count >= max_requests:
            return False
        
        cache.set(cache_key, count + 1, window)
        return True
    
    @staticmethod
    def get_remaining(ip: str, max_requests: int = 100) -> int:
        """Get remaining requests for IP"""
        cache_key = f"ratelimit:ip:{ip}"
        count = cache.get(cache_key, 0)
        return max(0, max_requests - count)


def rate_limit(max_requests: int = 100, window: int = 60):
    """Decorator for rate limiting views"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            ip = request.META.get('REMOTE_ADDR')
            
            if not IPRateLimiter.is_allowed(ip, max_requests, window):
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': window
                }, status=429)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Distributed rate limiting with Redis (optional)
class RedisRateLimiter:
    """Redis-based distributed rate limiter"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, key: str, max_requests: int, window: int) -> tuple:
        """Check rate limit using Redis"""
        current = int(time.time())
        window_start = current - window
        
        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count requests in window
        count = self.redis.zcard(key)
        
        if count >= max_requests:
            return False, 0
        
        # Add current request
        self.redis.zadd(key, {current: current})
        self.redis.expire(key, window)
        
        remaining = max_requests - count - 1
        return True, remaining
