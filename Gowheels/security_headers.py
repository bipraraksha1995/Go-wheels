"""
Security Headers Middleware
Implements CSP, HSTS, X-Frame-Options, and other security headers
"""
from django.conf import settings
import logging

logger = logging.getLogger('gowheels.security')


class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy (CSP)
        response['Content-Security-Policy'] = self._get_csp_policy()
        
        # Strict Transport Security (HSTS)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # X-Frame-Options (Clickjacking protection)
        response['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options (MIME sniffing protection)
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection (XSS filter)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature Policy)
        response['Permissions-Policy'] = self._get_permissions_policy()
        
        # Cross-Origin policies
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        
        # Remove server header
        if 'Server' in response:
            del response['Server']
        
        # Remove X-Powered-By
        if 'X-Powered-By' in response:
            del response['X-Powered-By']
        
        return response
    
    def _get_csp_policy(self):
        """Generate Content Security Policy"""
        policy = {
            'default-src': ["'self'"],
            'script-src': [
                "'self'",
                "'unsafe-inline'",  # Required for Django admin
                "https://unpkg.com",  # Swagger UI
                "https://cdn.redoc.ly",  # ReDoc
            ],
            'style-src': [
                "'self'",
                "'unsafe-inline'",  # Required for Django admin
                "https://unpkg.com",
                "https://fonts.googleapis.com",
            ],
            'img-src': [
                "'self'",
                "data:",
                "https:",
            ],
            'font-src': [
                "'self'",
                "https://fonts.gstatic.com",
            ],
            'connect-src': [
                "'self'",
                "https://api.gowheels.com",
            ],
            'frame-ancestors': ["'none'"],
            'base-uri': ["'self'"],
            'form-action': ["'self'"],
            'upgrade-insecure-requests': [],
        }
        
        # Build CSP string
        csp_parts = []
        for directive, sources in policy.items():
            if sources:
                csp_parts.append(f"{directive} {' '.join(sources)}")
            else:
                csp_parts.append(directive)
        
        return '; '.join(csp_parts)
    
    def _get_permissions_policy(self):
        """Generate Permissions Policy"""
        policies = [
            'geolocation=(self)',
            'microphone=()',
            'camera=()',
            'payment=(self)',
            'usb=()',
            'magnetometer=()',
            'gyroscope=()',
            'accelerometer=()',
        ]
        return ', '.join(policies)


class CSPReportMiddleware:
    """Handle CSP violation reports"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path == '/csp-report/' and request.method == 'POST':
            return self._handle_csp_report(request)
        
        return self.get_response(request)
    
    def _handle_csp_report(self, request):
        """Log CSP violations"""
        try:
            import json
            report = json.loads(request.body)
            logger.warning(f"CSP Violation: {report}")
        except Exception as e:
            logger.error(f"Failed to parse CSP report: {e}")
        
        from django.http import HttpResponse
        return HttpResponse(status=204)


class HSTSPreloadMiddleware:
    """HSTS Preload middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Only add HSTS in production
        if not settings.DEBUG and request.is_secure():
            response['Strict-Transport-Security'] = (
                'max-age=63072000; '  # 2 years
                'includeSubDomains; '
                'preload'
            )
        
        return response


class ClickjackingProtectionMiddleware:
    """Enhanced clickjacking protection"""
    
    ALLOWED_ORIGINS = [
        'https://gowheels.com',
        'https://www.gowheels.com',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if embedding is allowed
        origin = request.META.get('HTTP_ORIGIN', '')
        
        if origin in self.ALLOWED_ORIGINS:
            response['X-Frame-Options'] = f'ALLOW-FROM {origin}'
        else:
            response['X-Frame-Options'] = 'DENY'
        
        return response


class SecureHeadersConfig:
    """Security headers configuration"""
    
    @staticmethod
    def get_recommended_headers():
        """Get recommended security headers"""
        return {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'X-Frame-Options': 'DENY',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(self), microphone=(), camera=()',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
        }
    
    @staticmethod
    def validate_headers(response):
        """Validate security headers are present"""
        required_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
        ]
        
        missing = []
        for header in required_headers:
            if header not in response:
                missing.append(header)
        
        if missing:
            logger.warning(f"Missing security headers: {missing}")
        
        return len(missing) == 0
