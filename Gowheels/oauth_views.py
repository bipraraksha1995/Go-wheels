"""
OAuth2 / SSO Integration with Google Login
Converts OAuth2 tokens to JWT tokens for secure API access
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.urls import reverse
import json
import requests

from .auth_models import UserAuthentication, UserRole
from .jwt_utils import JWTTokenManager
from .rbac_decorators import get_client_ip


def oauth_login_page(request):
    """Display OAuth2 login options"""
    google_client_id = '{{GOOGLE_CLIENT_ID}}'  # Will be configured in settings
    
    return render(request, 'oauth_login.html', {
        'google_client_id': google_client_id,
    })


@csrf_exempt
@require_http_methods(["POST"])
def oauth_google_callback(request):
    """
    Handle Google OAuth2 callback
    Exchange Google token for JWT token
    
    POST /api/auth/oauth/google/
    {
        "token": "google_id_token_from_frontend"
    }
    """
    try:
        data = json.loads(request.body)
        google_token = data.get('token')
        
        if not google_token:
            return JsonResponse({
                'success': False,
                'error': 'Google token required'
            }, status=400)
        
        # Verify Google token
        google_user = verify_google_token(google_token)
        if not google_user:
            return JsonResponse({
                'success': False,
                'error': 'Invalid Google token'
            }, status=401)
        
        # Get or create user from Google profile
        user = get_or_create_google_user(google_user)
        
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create user account'
            }, status=500)
        
        # Ensure UserAuthentication exists
        user_auth, created = UserAuthentication.objects.get_or_create(user=user)
        if created:
            # Assign default role (buyer)
            default_role = UserRole.objects.filter(name='buyer').first()
            if default_role:
                user_auth.role = default_role
                user_auth.save()
        
        # Check if account is active
        if not user_auth.is_active:
            return JsonResponse({
                'success': False,
                'error': 'Your account has been deactivated'
            }, status=403)
        
        # Generate JWT tokens
        tokens = JWTTokenManager.generate_tokens(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Record successful login
        user_auth.record_successful_login()
        
        return JsonResponse({
            'success': True,
            'message': 'Google login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user_auth.role.name if user_auth.role else None,
            },
            'tokens': tokens
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def verify_google_token(token):
    """
    Verify Google OAuth2 ID token
    Returns user data if valid
    """
    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token
        from decouple import config
        
        google_client_id = config('GOOGLE_CLIENT_ID', default=None)
        if not google_client_id:
            return None
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            google_client_id
        )
        
        # Token is valid
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return {
            'sub': idinfo.get('sub'),
            'email': idinfo.get('email'),
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'given_name': idinfo.get('given_name', ''),
            'family_name': idinfo.get('family_name', ''),
        }
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return None


def get_or_create_google_user(google_user):
    """
    Get or create Django user from Google profile
    """
    try:
        email = google_user.get('email')
        if not email:
            return None
        
        # Try to find existing user by email
        user = User.objects.filter(email=email).first()
        
        if user:
            # Update profile info
            user.first_name = google_user.get('given_name', '')
            user.last_name = google_user.get('family_name', '')
            user.save()
        else:
            # Create new user
            username = email.split('@')[0]
            
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=google_user.get('given_name', ''),
                last_name=google_user.get('family_name', ''),
                is_active=True
            )
        
        return user
    except Exception as e:
        print(f"Error creating Google user: {str(e)}")
        return None


@csrf_exempt
@require_http_methods(["POST"])
def oauth_github_callback(request):
    """
    Handle GitHub OAuth2 callback
    Exchange GitHub token for JWT token
    
    POST /api/auth/oauth/github/
    {
        "code": "github_authorization_code",
        "state": "state_parameter"
    }
    """
    try:
        from decouple import config
        
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({
                'success': False,
                'error': 'GitHub code required'
            }, status=400)
        
        # Exchange code for access token
        github_client_id = config('GITHUB_CLIENT_ID', default=None)
        github_client_secret = config('GITHUB_CLIENT_SECRET', default=None)
        
        if not github_client_id or not github_client_secret:
            return JsonResponse({
                'success': False,
                'error': 'GitHub OAuth2 not configured'
            }, status=500)
        
        token_response = requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': github_client_id,
                'client_secret': github_client_secret,
                'code': code,
            },
            headers={'Accept': 'application/json'}
        )
        
        if token_response.status_code != 200:
            return JsonResponse({
                'success': False,
                'error': 'Failed to get GitHub access token'
            }, status=401)
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            return JsonResponse({
                'success': False,
                'error': 'No access token received'
            }, status=401)
        
        # Get GitHub user info
        user_response = requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_response.status_code != 200:
            return JsonResponse({
                'success': False,
                'error': 'Failed to get GitHub user info'
            }, status=401)
        
        github_user = user_response.json()
        
        # Get or create user
        user = get_or_create_github_user(github_user)
        
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create user account'
            }, status=500)
        
        # Ensure UserAuthentication exists
        user_auth, created = UserAuthentication.objects.get_or_create(user=user)
        if created:
            default_role = UserRole.objects.filter(name='buyer').first()
            if default_role:
                user_auth.role = default_role
                user_auth.save()
        
        if not user_auth.is_active:
            return JsonResponse({
                'success': False,
                'error': 'Your account has been deactivated'
            }, status=403)
        
        # Generate JWT tokens
        tokens = JWTTokenManager.generate_tokens(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        user_auth.record_successful_login()
        
        return JsonResponse({
            'success': True,
            'message': 'GitHub login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user_auth.role.name if user_auth.role else None,
            },
            'tokens': tokens
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_or_create_github_user(github_user):
    """Get or create Django user from GitHub profile"""
    try:
        email = github_user.get('email')
        username = github_user.get('login')
        
        if not username:
            return None
        
        # Try to find by GitHub username
        user = User.objects.filter(username=username).first()
        
        if user and email:
            user.email = email
            user.save()
        elif not user:
            user = User.objects.create_user(
                username=username,
                email=email or f"{username}@github.local",
                first_name=github_user.get('name', '').split()[0] if github_user.get('name') else '',
                last_name=' '.join(github_user.get('name', '').split()[1:]) if github_user.get('name') else '',
                is_active=True
            )
        
        return user
    except Exception as e:
        print(f"Error creating GitHub user: {str(e)}")
        return None


def oauth_success_redirect(request):
    """
    Redirect page after OAuth success
    Shows tokens and user info
    """
    return render(request, 'oauth_success.html')
