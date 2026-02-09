#!/usr/bin/env python
"""
Quick setup script for GoWheels authentication system
Creates default roles and permissions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gowheels_project.settings')
django.setup()

from gowheels.auth_models import UserRole, Permission, RolePermission

def setup_roles():
    """Create default roles"""
    roles_data = [
        ('buyer', 'Regular user who can browse and rent vehicles'),
        ('seller', 'Vehicle owner who can list vehicles'),
        ('admin', 'System administrator with full access'),
        ('moderator', 'Content moderator who can approve listings'),
    ]
    
    print("Creating roles...")
    for name, description in roles_data:
        role, created = UserRole.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        status = "[CREATED]" if created else "[EXISTS]"
        print(f"  {status}: {name}")
    
    return UserRole.objects.all()

def setup_permissions():
    """Create default permissions"""
    permissions_data = [
        ('view_vehicles', 'Can view vehicles'),
        ('create_vehicles', 'Can create vehicles'),
        ('edit_vehicles', 'Can edit vehicles'),
        ('delete_vehicles', 'Can delete vehicles'),
        ('manage_users', 'Can manage users'),
        ('manage_sellers', 'Can manage sellers'),
        ('view_analytics', 'Can view analytics'),
        ('approve_listings', 'Can approve listings'),
        ('manage_payments', 'Can manage payments'),
    ]
    
    print("\nCreating permissions...")
    for name, description in permissions_data:
        perm, created = Permission.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        status = "[CREATED]" if created else "[EXISTS]"
        print(f"  {status}: {name}")
    
    return Permission.objects.all()

def assign_permissions():
    """Assign permissions to roles"""
    print("\nAssigning permissions to roles...")
    
    # Buyer permissions
    buyer = UserRole.objects.get(name='buyer')
    buyer_perms = ['view_vehicles']
    for perm_name in buyer_perms:
        perm = Permission.objects.get(name=perm_name)
        RolePermission.objects.get_or_create(role=buyer, permission=perm)
    print(f"  [OK] Buyer: {len(buyer_perms)} permissions")
    
    # Seller permissions
    seller = UserRole.objects.get(name='seller')
    seller_perms = ['view_vehicles', 'create_vehicles', 'edit_vehicles', 'delete_vehicles']
    for perm_name in seller_perms:
        perm = Permission.objects.get(name=perm_name)
        RolePermission.objects.get_or_create(role=seller, permission=perm)
    print(f"  [OK] Seller: {len(seller_perms)} permissions")
    
    # Moderator permissions
    moderator = UserRole.objects.get(name='moderator')
    mod_perms = ['view_vehicles', 'approve_listings', 'view_analytics']
    for perm_name in mod_perms:
        perm = Permission.objects.get(name=perm_name)
        RolePermission.objects.get_or_create(role=moderator, permission=perm)
    print(f"  [OK] Moderator: {len(mod_perms)} permissions")
    
    # Admin permissions (all)
    admin = UserRole.objects.get(name='admin')
    all_perms = Permission.objects.all()
    for perm in all_perms:
        RolePermission.objects.get_or_create(role=admin, permission=perm)
    print(f"  [OK] Admin: {all_perms.count()} permissions (all)")

def verify_oauth_config():
    """Verify OAuth2 configuration"""
    from decouple import config
    
    print("\n" + "="*50)
    print("OAuth2 Configuration Check")
    print("="*50)
    
    google_id = config('GOOGLE_CLIENT_ID', default=None)
    google_secret = config('GOOGLE_CLIENT_SECRET', default=None)
    
    if google_id and google_secret:
        print("[OK] Google OAuth2: Configured")
        print(f"   Client ID: {google_id[:20]}...")
    else:
        print("[ERROR] Google OAuth2: Not configured")
    
    github_id = config('GITHUB_CLIENT_ID', default=None)
    github_secret = config('GITHUB_CLIENT_SECRET', default=None)
    
    if github_id and github_secret:
        print("[OK] GitHub OAuth2: Configured")
    else:
        print("[WARN] GitHub OAuth2: Not configured (optional)")

def main():
    print("="*50)
    print("GoWheels Authentication Setup")
    print("="*50)
    
    try:
        setup_roles()
        setup_permissions()
        assign_permissions()
        verify_oauth_config()
        
        print("\n" + "="*50)
        print("[SUCCESS] Setup Complete!")
        print("="*50)
        print("\nNext steps:")
        print("1. Start server: python manage.py runserver 127.0.0.1:8000")
        print("2. Visit: http://localhost:8000/oauth/login/")
        print("3. Click 'Login with Google'")
        print("\nYour authentication system is ready!")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nMake sure:")
        print("1. Database is running")
        print("2. Migrations are applied: python manage.py migrate")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
