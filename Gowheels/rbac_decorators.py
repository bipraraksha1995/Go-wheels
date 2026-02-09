"""
Role-Based Access Control (RBAC) and permission decorators
"""
from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.models import User
from .jwt_utils import JWTTokenManager
from .auth_models import UserAuthentication, AuditLog
import json


def get_user_from_request(request):
    """Extract user from JWT token in request header"""
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        is_valid, payload = JWTTokenManager.validate_token(token, token_type='access')
        
        if is_valid:
            return User.objects.get(id=payload['user_id'])
    except Exception:
        pass
    
    return None


def require_auth(view_func):
    """Decorator: Require JWT authentication"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_user_from_request(request)
        
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required. Please provide a valid token.'
            }, status=401)
        
        # Check if user auth profile exists and is active
        try:
            auth_profile = UserAuthentication.objects.get(user=user)
            if not auth_profile.is_active:
                return JsonResponse({
                    'success': False,
                    'error': 'Your account has been deactivated.'
                }, status=403)
            
            if auth_profile.is_account_locked():
                return JsonResponse({
                    'success': False,
                    'error': 'Your account is temporarily locked due to too many failed login attempts.'
                }, status=403)
        except UserAuthentication.DoesNotExist:
            pass
        
        # Add user to request
        request.user = user
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_permission(permission_name):
    """Decorator: Require specific permission"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = get_user_from_request(request)
            
            if not user:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required.'
                }, status=401)
            
            try:
                auth_profile = UserAuthentication.objects.get(user=user)
                
                # Get user's permissions
                permissions = auth_profile.get_permissions()
                
                if permission_name not in permissions:
                    # Log permission denied
                    ip_address = get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', '')
                    AuditLog.objects.create(
                        user=user,
                        action='permission_change',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        status='failed',
                        details=f'Access denied for permission: {permission_name}'
                    )
                    
                    return JsonResponse({
                        'success': False,
                        'error': f'Permission denied. Required: {permission_name}'
                    }, status=403)
                
                request.user = user
                return view_func(request, *args, **kwargs)
                
            except UserAuthentication.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'User authentication profile not found.'
                }, status=404)
        
        return wrapper
    return decorator


def require_role(*allowed_roles):
    """Decorator: Require specific role(s)"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = get_user_from_request(request)
            
            if not user:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required.'
                }, status=401)
            
            try:
                auth_profile = UserAuthentication.objects.get(user=user)
                
                if not auth_profile.role or auth_profile.role.name not in allowed_roles:
                    return JsonResponse({
                        'success': False,
                        'error': f'Access denied. Required role(s): {", ".join(allowed_roles)}'
                    }, status=403)
                
                request.user = user
                request.user_role = auth_profile.role
                return view_func(request, *args, **kwargs)
                
            except UserAuthentication.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'User authentication profile not found.'
                }, status=404)
        
        return wrapper
    return decorator


def permission_required(permission_name):
    """Class-based view decorator for permissions"""
    def decorator(cls):
        original_dispatch = cls.dispatch
        
        def new_dispatch(self, request, *args, **kwargs):
            user = get_user_from_request(request)
            
            if not user:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required.'
                }, status=401)
            
            try:
                auth_profile = UserAuthentication.objects.get(user=user)
                permissions = auth_profile.get_permissions()
                
                if permission_name not in permissions:
                    return JsonResponse({
                        'success': False,
                        'error': f'Permission denied. Required: {permission_name}'
                    }, status=403)
                
                request.user = user
                return original_dispatch(self, request, *args, **kwargs)
                
            except UserAuthentication.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'User authentication profile not found.'
                }, status=404)
        
        cls.dispatch = new_dispatch
        return cls
    
    return decorator


class PermissionChecker:
    """Check permissions for a user"""
    
    @staticmethod
    def has_permission(user, permission_name):
        """Check if user has specific permission"""
        try:
            auth_profile = UserAuthentication.objects.get(user=user)
            permissions = auth_profile.get_permissions()
            return permission_name in permissions
        except UserAuthentication.DoesNotExist:
            return False
    
    @staticmethod
    def has_role(user, role_name):
        """Check if user has specific role"""
        try:
            auth_profile = UserAuthentication.objects.get(user=user)
            return auth_profile.role and auth_profile.role.name == role_name
        except UserAuthentication.DoesNotExist:
            return False
    
    @staticmethod
    def has_any_role(user, role_names):
        """Check if user has any of the specified roles"""
        try:
            auth_profile = UserAuthentication.objects.get(user=user)
            return auth_profile.role and auth_profile.role.name in role_names
        except UserAuthentication.DoesNotExist:
            return False
    
    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for a user"""
        try:
            auth_profile = UserAuthentication.objects.get(user=user)
            return list(auth_profile.get_permissions())
        except UserAuthentication.DoesNotExist:
            return []
    
    @staticmethod
    def get_user_role(user):
        """Get user's role"""
        try:
            auth_profile = UserAuthentication.objects.get(user=user)
            return auth_profile.role
        except UserAuthentication.DoesNotExist:
            return None


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
