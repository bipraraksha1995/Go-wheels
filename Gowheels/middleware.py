"""
Security middleware for GoWheels
Adds custom security headers and cookie validation
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.conf import settings


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds additional security headers to all responses
    Complements Django's built-in security middleware
    """
    
    def process_response(self, request, response):
        """Add security headers to response"""
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
        )
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS filtering
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Referrer Policy (limit what gets sent)
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy (restrict browser features)
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), '
            'gyroscope=(), magnetometer=(), microphone=(), '
            'payment=(), usb=()'
        )
        
        return response


class CookieValidationMiddleware(MiddlewareMixin):
    """
    Validates session cookies for protected endpoints
    Ensures API calls have valid sessions
    """
    
    # Public endpoints that don't require session
    PUBLIC_PATHS = [
        '/api/login/',
        '/api/register/',
        '/api/phone-check/',
        '/health/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """Validate session cookie for protected views"""
        
        # Skip public paths
        for public_path in self.PUBLIC_PATHS:
            if request.path.startswith(public_path):
                return None
        
        # Require session for API endpoints
        if request.path.startswith('/api/'):
            if not request.session or not request.session.session_key:
                # Allow GET requests without session
                if request.method != 'GET':
                    return HttpResponseForbidden(
                        'Session required. Please login first.'
                    )
        
        return None


class TLSRedirectMiddleware(MiddlewareMixin):
    """
    Enforce HTTPS for production
    This complements Django's SECURE_SSL_REDIRECT setting
    """
    
    def process_request(self, request):
        """Redirect HTTP to HTTPS if not in debug mode"""
        if not settings.DEBUG:
            if not request.is_secure():
                # Get the full URL and replace http with https
                url = request.build_absolute_uri(request.get_full_path())
                if url.startswith('http://'):
                    url = 'https://' + url[7:]
                    # Return permanent redirect (301)
                    from django.http import HttpResponsePermanentRedirect
                    return HttpResponsePermanentRedirect(url)
        
        return None
