"""
Enhanced authentication models with JWT tokens, RBAC, and MFA support
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import string
from datetime import timedelta


class UserRole(models.Model):
    """Define user roles in the system"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
        ('moderator', 'Moderator'),
    ]
    
    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Permission(models.Model):
    """Define granular permissions"""
    PERMISSION_CHOICES = [
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
    
    name = models.CharField(max_length=100, unique=True, choices=PERMISSION_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class RolePermission(models.Model):
    """Many-to-many relationship between roles and permissions"""
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('role', 'permission')
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserAuthentication(models.Model):
    """Enhanced user auth with roles and security"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_profile')
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True)
    
    # Account status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Security
    password_changed_at = models.DateTimeField(auto_now=True)
    require_password_change = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.role.name if self.role else 'No role'})"
    
    def is_account_locked(self):
        """Check if account is locked due to failed login attempts"""
        if self.locked_until:
            if timezone.now() < self.locked_until:
                return True
            else:
                self.login_attempts = 0
                self.locked_until = None
                self.save()
        return False
    
    def record_failed_login(self):
        """Record failed login attempt and lock if needed"""
        self.login_attempts += 1
        if self.login_attempts >= 5:  # Lock after 5 failed attempts
            self.locked_until = timezone.now() + timedelta(minutes=15)
        self.save()
    
    def record_successful_login(self):
        """Clear failed attempts on successful login"""
        self.login_attempts = 0
        self.locked_until = None
        self.last_login = timezone.now()
        self.save()
    
    def get_permissions(self):
        """Get all permissions for this user's role"""
        if not self.role:
            return []
        return self.role.permissions.all().values_list('permission__name', flat=True)


class JWTToken(models.Model):
    """Store JWT tokens for revocation and tracking"""
    TOKEN_TYPE_CHOICES = [
        ('access', 'Access Token'),
        ('refresh', 'Refresh Token'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jwt_tokens')
    token_hash = models.CharField(max_length=255, unique=True)  # Hash of token for unique constraint
    token = models.TextField()  # Full token
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES)
    
    # Token expiry
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Revocation
    is_revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    # Device/IP tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.token_type} - {self.created_at}"
    
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() > self.expires_at or self.is_revoked
    
    def revoke(self):
        """Revoke this token"""
        self.is_revoked = True
        self.revoked_at = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['-created_at']


class MultiFactorAuth(models.Model):
    """Multi-factor authentication (MFA) configuration"""
    MFA_METHOD_CHOICES = [
        ('totp', 'Time-based OTP (Authenticator App)'),
        ('sms', 'SMS OTP'),
        ('email', 'Email OTP'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mfa_config')
    method = models.CharField(max_length=20, choices=MFA_METHOD_CHOICES)
    
    # TOTP (Google Authenticator, etc.)
    totp_secret = models.CharField(max_length=32, blank=True)
    
    # Recovery codes for account recovery
    backup_codes = models.TextField(blank=True)  # JSON list of codes
    
    # Status
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.method}"


class MFASession(models.Model):
    """Temporary session during MFA verification"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mfa_sessions')
    
    # Session token
    session_token = models.CharField(max_length=255, unique=True)
    
    # Verification status
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    # Attempt tracking
    attempts = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - MFA Session"
    
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() > self.expires_at
    
    def can_attempt(self):
        """Check if user can attempt MFA verification"""
        return self.attempts < 3 and not self.is_expired()


class AuditLog(models.Model):
    """Security audit log for all authentication events"""
    ACTION_CHOICES = [
        ('login_success', 'Successful Login'),
        ('login_failed', 'Failed Login'),
        ('login_mfa', 'MFA Verification'),
        ('logout', 'Logout'),
        ('password_change', 'Password Changed'),
        ('password_reset', 'Password Reset'),
        ('mfa_enabled', 'MFA Enabled'),
        ('mfa_disabled', 'MFA Disabled'),
        ('token_created', 'Token Created'),
        ('token_revoked', 'Token Revoked'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('permission_change', 'Permission Changed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    
    # Request details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Additional details
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='success')  # success, failed, warning
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
        ]


class SessionManagement(models.Model):
    """Enhanced session tracking for security"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    
    # Session details
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Activity tracking
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    # Device fingerprinting
    device_id = models.CharField(max_length=255, blank=True)
    device_name = models.CharField(max_length=255, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - Session"
    
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() > self.expires_at or not self.is_active
    
    class Meta:
        ordering = ['-last_activity']
