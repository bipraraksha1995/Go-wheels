"""
Cryptographic utilities for GoWheels
Provides secure random token generation and strong crypto functions
"""

import secrets
import string
from django.contrib.auth.tokens import default_token_generator


def generate_secure_token(length=32):
    """
    Generate a cryptographically secure random token (URL-safe)
    
    Args:
        length (int): Number of bytes of entropy (default 32 = 256 bits)
        
    Returns:
        str: URL-safe base64-encoded token
    """
    return secrets.token_urlsafe(length)


def generate_session_token():
    """Generate a secure session/API token"""
    return generate_secure_token(32)


def generate_api_key():
    """Generate a secure API key"""
    return generate_secure_token(32)


def generate_password_reset_token(user):
    """
    Generate a secure, time-limited password reset token
    
    Args:
        user: Django User instance
        
    Returns:
        str: Password reset token (expires in 1 day by default)
    """
    return default_token_generator.make_token(user)


def verify_password_reset_token(user, token):
    """
    Verify a password reset token
    
    Args:
        user: Django User instance
        token (str): Token to verify
        
    Returns:
        bool: True if valid, False otherwise
    """
    return default_token_generator.check_token(user, token)


def generate_strong_password(length=16):
    """
    Generate a cryptographically secure random password
    Contains: letters, digits, special characters
    
    Args:
        length (int): Password length (default 16)
        
    Returns:
        str: Strong random password
    """
    chars = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_otp(length=6):
    """
    Generate a secure One-Time Password (numeric)
    
    Args:
        length (int): OTP length (default 6 digits)
        
    Returns:
        str: Numeric OTP
    """
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))


def generate_phone_otp():
    """Generate a 6-digit OTP for phone verification"""
    return generate_otp(6)


def generate_email_otp():
    """Generate an 8-digit OTP for email verification"""
    return generate_otp(8)


def generate_secure_random_bytes(length=32):
    """
    Generate cryptographically secure random bytes
    
    Args:
        length (int): Number of bytes
        
    Returns:
        bytes: Random bytes
    """
    return secrets.token_bytes(length)


def generate_device_id():
    """Generate a unique device ID for API clients"""
    return generate_secure_token(32)


def is_secure_string(s, min_length=8):
    """
    Check if a string has minimum security properties
    (for validating passwords, etc.)
    
    Args:
        s (str): String to check
        min_length (int): Minimum length
        
    Returns:
        tuple: (is_secure: bool, reason: str)
    """
    if not isinstance(s, str):
        return False, "Not a string"
    
    if len(s) < min_length:
        return False, f"Too short (minimum {min_length} characters)"
    
    has_upper = any(c.isupper() for c in s)
    has_lower = any(c.islower() for c in s)
    has_digit = any(c.isdigit() for c in s)
    has_special = any(c in "!@#$%^&*-_=+" for c in s)
    
    if not has_upper:
        return False, "Missing uppercase letter"
    if not has_lower:
        return False, "Missing lowercase letter"
    if not has_digit:
        return False, "Missing digit"
    if not has_special:
        return False, "Missing special character"
    
    return True, "OK"
