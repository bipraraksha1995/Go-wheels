"""
Enhanced authentication API views with JWT, RBAC, and MFA
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
import json

from .auth_models import (
    UserAuthentication, UserRole, JWTToken, 
    MultiFactorAuth, AuditLog
)
from .jwt_utils import JWTTokenManager
from .mfa_utils import MFAManager, AuditLogger
from .rbac_decorators import (
    require_auth, require_permission, require_role, 
    get_user_from_request, PermissionChecker, get_client_ip
)


def get_user_agent(request):
    """Extract user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


@csrf_exempt
def auth_login(request):
    """
    JWT Login endpoint
    
    POST /api/auth/login
    {
        "username": "user@example.com",
        "password": "password",
        "remember_me": false
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password required'
            }, status=400)
        
        # Find user by username or email
        user = User.objects.filter(username=username).first() or \
               User.objects.filter(email=username).first()
        
        if not user:
            ip_address = get_client_ip(request)
            AuditLogger.log_login_attempt(
                user=None,
                ip_address=ip_address,
                user_agent=get_user_agent(request),
                success=False,
                reason='User not found'
            )
            return JsonResponse({
                'success': False,
                'error': 'Invalid credentials'
            }, status=401)
        
        # Verify password
        if not check_password(password, user.password):
            ip_address = get_client_ip(request)
            user_auth = UserAuthentication.objects.get_or_create(user=user)[0]
            user_auth.record_failed_login()
            
            AuditLogger.log_login_attempt(
                user=user,
                ip_address=ip_address,
                user_agent=get_user_agent(request),
                success=False,
                reason='Invalid password'
            )
            
            return JsonResponse({
                'success': False,
                'error': 'Invalid credentials'
            }, status=401)
        
        # Check user auth status
        try:
            user_auth = UserAuthentication.objects.get(user=user)
        except UserAuthentication.DoesNotExist:
            user_auth = UserAuthentication.objects.create(user=user)
        
        if not user_auth.is_active:
            return JsonResponse({
                'success': False,
                'error': 'Your account has been deactivated'
            }, status=403)
        
        if user_auth.is_account_locked():
            return JsonResponse({
                'success': False,
                'error': 'Your account is locked. Try again later.'
            }, status=403)
        
        ip_address = get_client_ip(request)
        
        # Check if MFA is enabled
        try:
            mfa = MultiFactorAuth.objects.get(user=user, is_enabled=True)
            # Create MFA session
            session_token = MFAManager.create_mfa_session(user)
            
            AuditLogger.log_action(
                user=user,
                action='login_mfa',
                ip_address=ip_address,
                user_agent=get_user_agent(request),
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'MFA verification required',
                'mfa_required': True,
                'mfa_session': session_token,
                'mfa_method': mfa.method
            })
        except MultiFactorAuth.DoesNotExist:
            # No MFA, proceed with token generation
            pass
        
        # Generate JWT tokens
        tokens = JWTTokenManager.generate_tokens(
            user=user,
            ip_address=ip_address,
            user_agent=get_user_agent(request)
        )
        
        # Record successful login
        user_auth.record_successful_login()
        
        AuditLogger.log_login_attempt(
            user=user,
            ip_address=ip_address,
            user_agent=get_user_agent(request),
            success=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'role': user_auth.role.name if user_auth.role else None,
            },
            'tokens': tokens
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def auth_register(request):
    """
    Register new user
    
    POST /api/auth/register
    {
        "username": "username",
        "email": "email@example.com",
        "password": "secure_password",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        # Validation
        if not all([username, email, password]):
            return JsonResponse({
                'success': False,
                'error': 'Username, email, and password required'
            }, status=400)
        
        if len(password) < 8:
            return JsonResponse({
                'success': False,
                'error': 'Password must be at least 8 characters'
            }, status=400)
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'error': 'Username already taken'
            }, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'Email already registered'
            }, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create authentication profile with default 'buyer' role
        default_role = UserRole.objects.filter(name='buyer').first()
        UserAuthentication.objects.create(
            user=user,
            role=default_role,
            is_active=True
        )
        
        # Log registration
        AuditLogger.log_action(
            user=user,
            action='login_success',
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details='User registered'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful. Please log in.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def auth_logout(request):
    """
    Logout and revoke token
    
    POST /api/auth/logout
    Header: Authorization: Bearer <token>
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = get_user_from_request(request)
    if not user:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)
    
    try:
        # Get token from header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            JWTTokenManager.revoke_token(token)
        
        # Log logout
        AuditLogger.log_logout(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Logged out successfully'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def auth_refresh_token(request):
    """
    Refresh access token using refresh token
    
    POST /api/auth/refresh
    {
        "refresh": "refresh_token"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh')
        
        if not refresh_token:
            return JsonResponse({
                'success': False,
                'error': 'Refresh token required'
            }, status=400)
        
        success, result = JWTTokenManager.refresh_access_token(
            refresh_token,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'tokens': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result
            }, status=401)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_auth
def auth_me(request):
    """Get current user information"""
    user = request.user
    
    try:
        user_auth = UserAuthentication.objects.get(user=user)
        permissions = list(user_auth.get_permissions())
    except UserAuthentication.DoesNotExist:
        permissions = []
    
    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user_auth.role.name if user_auth.role else None,
            'permissions': permissions,
            'is_active': user_auth.is_active,
            'last_login': user_auth.last_login.isoformat() if user_auth.last_login else None,
        }
    })


@require_auth
def auth_setup_mfa(request):
    """
    Setup MFA for user
    
    POST /api/auth/setup-mfa
    {
        "method": "totp"  # totp, sms, email
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = request.user
    
    try:
        data = json.loads(request.body)
        method = data.get('method', 'totp')
        
        # Generate TOTP secret
        if method == 'totp':
            totp_data = MFAManager.generate_totp_secret(user)
            mfa = MFAManager.enable_mfa(user, method='totp')
            mfa.totp_secret = totp_data['secret']
            mfa.save()
            
            return JsonResponse({
                'success': True,
                'message': 'MFA setup initialized',
                'mfa_data': {
                    'method': 'totp',
                    'secret': totp_data['secret'],
                    'provisioning_uri': totp_data['provisioning_uri'],
                    'qr_code_url': totp_data['qr_code_url']
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'MFA method {method} not supported yet'
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_auth
@csrf_exempt
def auth_enable_mfa(request):
    """
    Enable MFA after verification
    
    POST /api/auth/enable-mfa
    {
        "code": "123456"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = request.user
    
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({
                'success': False,
                'error': 'MFA code required'
            }, status=400)
        
        # Verify TOTP code
        is_valid, message = MFAManager.verify_totp(user, code)
        
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': message
            }, status=400)
        
        # Enable MFA
        mfa = MultiFactorAuth.objects.get(user=user)
        mfa.is_enabled = True
        mfa.save()
        
        # Generate backup codes
        backup_codes = MFAManager.generate_backup_codes()
        MFAManager.save_backup_codes(user, backup_codes)
        
        AuditLogger.log_action(
            user=user,
            action='mfa_enabled',
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details=f'MFA enabled: {mfa.method}'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'MFA enabled successfully',
            'backup_codes': backup_codes
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except MultiFactorAuth.DoesNotExist:
        return JsonResponse({'error': 'MFA not configured'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def auth_verify_mfa(request):
    """
    Verify MFA code during login
    
    POST /api/auth/verify-mfa
    {
        "mfa_session": "session_token",
        "code": "123456"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        mfa_session = data.get('mfa_session')
        code = data.get('code')
        
        if not mfa_session or not code:
            return JsonResponse({
                'success': False,
                'error': 'MFA session and code required'
            }, status=400)
        
        from .auth_models import MFASession
        session = MFASession.objects.filter(session_token=mfa_session).first()
        
        if not session:
            return JsonResponse({
                'success': False,
                'error': 'Invalid MFA session'
            }, status=401)
        
        user = session.user
        is_valid, message = MFAManager.verify_mfa_session(user, mfa_session, code)
        
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': message
            }, status=401)
        
        # Generate JWT tokens
        tokens = JWTTokenManager.generate_tokens(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        # Update last login
        user_auth = UserAuthentication.objects.get(user=user)
        user_auth.record_successful_login()
        
        AuditLogger.log_login_attempt(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            success=True,
            reason='MFA verified'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'MFA verified, login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'tokens': tokens
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
