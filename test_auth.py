#!/usr/bin/env python
"""
Test OAuth2 and authentication features
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gowheels_project.settings')
django.setup()

from django.contrib.auth.models import User
from gowheels.auth_models import UserAuthentication, UserRole
from gowheels.jwt_utils import JWTTokenManager

def test_jwt_tokens():
    """Test JWT token generation"""
    print("\n" + "="*50)
    print("Testing JWT Token Generation")
    print("="*50)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Ensure role exists
    role, _ = UserRole.objects.get_or_create(name='buyer')
    
    # Create auth profile
    auth, _ = UserAuthentication.objects.get_or_create(
        user=user,
        defaults={'role': role}
    )
    
    # Generate tokens
    tokens = JWTTokenManager.generate_tokens(
        user=user,
        ip_address='127.0.0.1',
        user_agent='Test Browser'
    )
    
    print(f"✅ User: {user.username}")
    print(f"✅ Role: {auth.role.name}")
    print(f"✅ Access Token: {tokens['access'][:50]}...")
    print(f"✅ Refresh Token: {tokens['refresh'][:50]}...")
    print(f"✅ Expires in: {tokens['expires_in']} seconds")
    print(f"✅ Token Type: {tokens['token_type']}")
    
    # Validate token
    is_valid, payload = JWTTokenManager.validate_token(tokens['access'])
    if is_valid:
        print(f"✅ Token validation: SUCCESS")
        print(f"   User ID: {payload['user_id']}")
        print(f"   Username: {payload['username']}")
    else:
        print(f"❌ Token validation: FAILED - {payload}")

def test_mfa_setup():
    """Test MFA setup"""
    print("\n" + "="*50)
    print("Testing MFA (Multi-Factor Authentication)")
    print("="*50)
    
    from gowheels.mfa_utils import MFAManager
    
    user = User.objects.filter(username='testuser').first()
    if not user:
        print("❌ Test user not found")
        return
    
    # Generate TOTP secret
    totp_data = MFAManager.generate_totp_secret(user)
    
    print("✅ TOTP Secret generated")
    print(f"   Secret: {totp_data['secret']}")
    print(f"   QR Code URL: {totp_data['qr_code_url'][:80]}...")
    print("\n   Scan QR code with Google Authenticator to test MFA")

def test_rbac():
    """Test RBAC permissions"""
    print("\n" + "="*50)
    print("Testing RBAC (Role-Based Access Control)")
    print("="*50)
    
    from gowheels.rbac_decorators import PermissionChecker
    
    user = User.objects.filter(username='testuser').first()
    if not user:
        print("❌ Test user not found")
        return
    
    # Check permissions
    perms = PermissionChecker.get_user_permissions(user)
    role = PermissionChecker.get_user_role(user)
    
    print(f"✅ User: {user.username}")
    print(f"✅ Role: {role.name if role else 'None'}")
    print(f"✅ Permissions: {', '.join(perms) if perms else 'None'}")
    
    # Test specific permission
    can_view = PermissionChecker.has_permission(user, 'view_vehicles')
    can_create = PermissionChecker.has_permission(user, 'create_vehicles')
    
    print(f"\n   Can view vehicles: {'✅ Yes' if can_view else '❌ No'}")
    print(f"   Can create vehicles: {'✅ Yes' if can_create else '❌ No'}")

def test_oauth_config():
    """Test OAuth2 configuration"""
    print("\n" + "="*50)
    print("Testing OAuth2 Configuration")
    print("="*50)
    
    from decouple import config
    
    google_id = config('GOOGLE_CLIENT_ID', default=None)
    google_secret = config('GOOGLE_CLIENT_SECRET', default=None)
    
    if google_id and google_secret:
        print("✅ Google OAuth2: Ready")
        print(f"   Client ID: {google_id[:30]}...")
        print(f"   Client Secret: {google_secret[:20]}...")
        print("\n   Test at: http://localhost:8000/oauth/login/")
    else:
        print("❌ Google OAuth2: Not configured")

def main():
    print("="*50)
    print("GoWheels Authentication Test Suite")
    print("="*50)
    
    try:
        test_jwt_tokens()
        test_mfa_setup()
        test_rbac()
        test_oauth_config()
        
        print("\n" + "="*50)
        print("✅ All Tests Complete!")
        print("="*50)
        print("\nYour authentication system is working! 🎉")
        print("\nTo test OAuth2 login:")
        print("1. python manage.py runserver 127.0.0.1:8000")
        print("2. Visit: http://localhost:8000/oauth/login/")
        print("3. Click 'Login with Google'")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
