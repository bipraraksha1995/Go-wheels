# 🔐 Security Features Implementation Guide

This guide documents the security features used in the GoWheels application and how to implement them correctly.

---

## 1. TLS (Data Encryption)

### Why We Use It
- **Data in Transit Protection**: Encrypts all data sent between client and server
- **Prevents Eavesdropping**: Protects usernames, passwords, vehicle data from packet sniffing
- **Authentication**: Verifies the server is legitimate (not a fake server)
- **Integrity**: Ensures data isn't tampered with during transmission

### Implementation

#### Django Settings (`gowheels_project/settings.py`)

```python
# Enable HTTPS only
SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
SESSION_COOKIE_SECURE = True  # Send cookies only over HTTPS
CSRF_COOKIE_SECURE = True  # Send CSRF tokens only over HTTPS

# Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True  # Add to HSTS preload list

# Additional security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

#### Local Development (self-signed cert)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run Django with SSL
python manage.py runserver_plus --cert cert
```

#### Production (Let's Encrypt)

```bash
# Using Certbot
sudo certbot certonly --standalone -d yourdomain.com

# Update Nginx/Apache with cert paths
# Then test:
curl -I https://yourdomain.com  # Should show 200 OK, no warnings
```

#### Verification
```bash
# Check certificate validity
openssl s_client -connect yourdomain.com:443

# Verify HSTS header
curl -i https://yourdomain.com | grep Strict-Transport-Security
```

---

## 2. Certificate Pinning (Block Fake Servers)

### Why We Use It
- **Man-in-the-Middle (MITM) Prevention**: Even if attacker has valid cert, your app won't trust it
- **Prevents Compromised CAs**: Protects against rogue certificate authorities
- **Mobile Security**: Critical for APIs used by mobile apps
- **Vendor Lock-in Resistance**: Ensures only legitimate server certs are accepted

### Implementation

#### Pin Server Certificate (Mobile/Client App)

For Django backend, implement pinning in client apps calling your API:

**Python (Requests Library)**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

class PinnedHTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.check_hostname = False  # We'll pin instead
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# Pin certificate
session = requests.Session()
session.mount('https://', PinnedHTTPAdapter())

# Your cert fingerprint (SHA256 hash)
CERT_FINGERPRINT = "abcd1234..."
response = session.get('https://api.yourdomain.com/vehicle')
```

**Swift (iOS)**
```swift
import Alamofire

let certificates = ServerTrustPolicy.PinningMode.certificate(
    [/*load your .cer file*/]
)

let serverTrustPolicy = [
    "api.yourdomain.com": ServerTrustPolicy.pinCertificates(certificates: certificates)
]

Alamofire.request("https://api.yourdomain.com/vehicle")
```

#### Generate Certificate Fingerprint

```bash
# Get cert from server
openssl s_client -connect api.yourdomain.com:443 < /dev/null | openssl x509 -outform DER | sha256sum

# Or use openssl directly
openssl x509 -in cert.pem -outform DER | sha256sum
```

#### Django Side: Serve Pinning Info

```python
# gowheels/views.py
from django.http import JsonResponse

def cert_pinning_info(request):
    """Endpoint that returns cert pinning details for clients"""
    return JsonResponse({
        "pin_sha256": "your_cert_sha256_hash_here",
        "backup_pin_sha256": "backup_cert_hash",
        "expiration": "2025-12-31T23:59:59Z"
    })
```

---

## 3. Secure Cookies (Stop Session Theft)

### Why We Use It
- **Session Hijacking Prevention**: Stops attackers from stealing session IDs
- **CSRF Protection**: Prevents cross-site request forgery attacks
- **XSS Mitigation**: HttpOnly flag prevents JavaScript from accessing cookies
- **SSL Only**: Ensures cookies transmitted only over encrypted HTTPS

### Implementation

#### Django Settings

```python
# gowheels_project/settings.py

# Session Cookie Security
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # Block cross-site cookies
SESSION_COOKIE_AGE = 3600  # 1 hour timeout
SESSION_COOKIE_NAME = '_gsid'  # Custom name (obscures Django)

# CSRF Protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_AGE = 31536000  # 1 year
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://app.yourdomain.com'
]

# Cross-Origin Policies
CSRF_USE_SESSIONS = True  # Store CSRF token in session, not cookie

# Additional Headers
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
```

#### Middleware for Cookie Validation

```python
# gowheels/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden

class CookieValidationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """Validate session cookie is present for protected views"""
        # Skip for public endpoints
        if request.path in ['/api/login/', '/api/register/', '/health/']:
            return None
        
        # Require session for API calls
        if request.path.startswith('/api/') and not request.session.session_key:
            return HttpResponseForbidden("Session required")
        
        return None

# gowheels_project/settings.py
MIDDLEWARE = [
    # ... other middleware
    'gowheels.middleware.CookieValidationMiddleware',
]
```

#### Test Cookies Locally

```bash
# Start server with debug
python manage.py runserver

# Login and inspect cookies
curl -i -c cookies.txt -b cookies.txt -X POST \
  http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Check cookie attributes
cat cookies.txt
# Should show: "Secure", "HttpOnly", "SameSite=Strict"
```

---

## 4. Argon2 / bcrypt Password Hashing

### Why We Use It
- **GPU/ASIC Resistant**: Argon2 is memory-hard; bcrypt is slow
- **Brute-Force Prevention**: Makes dictionary attacks computationally expensive
- **Rainbow Table Immune**: Salt ensures identical passwords hash differently
- **Password Breach Safe**: Even if database stolen, passwords can't be cracked quickly

### Implementation

#### Install Password Hashers

```bash
pip install argon2-cffi bcrypt
```

#### Django Settings

```python
# gowheels_project/settings.py

PASSWORD_HASHERS = [
    # Argon2 is default and recommended
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    # Fallback for legacy passwords
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Argon2 parameters (tune for your hardware)
ARGON2_PARAMETERS = {
    'memory_cost': 512,      # MB
    'time_cost': 2,          # Iterations
    'parallelism': 2,        # Threads
}
```

#### Hash Password on User Creation

```python
# gowheels/views.py
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

def register_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    
    # Django ORM automatically hashes password
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password  # Automatically hashed with Argon2
    )
    
    return JsonResponse({'status': 'created'})
```

#### Verify Password During Login

```python
# gowheels/views.py
from django.contrib.auth import authenticate

def login_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Password matched (hashed comparison done internally)
        login(request, user)
        return JsonResponse({'status': 'logged_in'})
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
```

#### Update Legacy Passwords

```bash
# Django automatically upgrades weak hashes on next login
# Or run migration to force rehash:
python manage.py shell

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

for user in User.objects.all():
    if not user.password.startswith('argon2'):
        # Re-hash with Argon2
        user.password = make_password(user.password)
        user.save()
```

#### Test Password Hashing

```bash
python manage.py shell

from django.contrib.auth.hashers import make_password, check_password

# Hash a password
hashed = make_password('mypassword123')
print(hashed)  # argon2$...$...

# Verify password
check_password('mypassword123', hashed)  # True
check_password('wrongpassword', hashed)  # False
```

---

## 5. Strong Cryptography (No Cracking)

### Why We Use It
- **Encryption Security**: Strong algorithms prevent decryption attacks
- **Token Generation**: Cryptographically secure random tokens for password resets, OTP
- **Data Protection**: Sensitive data encrypted at rest
- **FIPS Compliance**: Meets federal/industry standards

### Implementation

#### Strong Encryption Library

```bash
pip install cryptography pycryptodome
```

#### Generate Secure Tokens

```python
# gowheels/views.py
import secrets
from django.contrib.auth.tokens import default_token_generator

def generate_password_reset_token(user):
    """Generate secure token for password reset"""
    token = default_token_generator.make_token(user)
    # Token is cryptographically secure and time-limited
    return token

def generate_session_token():
    """Generate secure session/API token"""
    return secrets.token_urlsafe(32)  # 256 bits of entropy
```

#### Encrypt Sensitive Data at Rest

```python
# gowheels/encryption.py
from cryptography.fernet import Fernet
import os

class Cipher:
    def __init__(self):
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY not set")
        self.cipher = Fernet(key)
    
    def encrypt(self, plaintext):
        """Encrypt sensitive data"""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext):
        """Decrypt sensitive data"""
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Generate key once (store in .env)
# from cryptography.fernet import Fernet
# key = Fernet.generate_key()  # Keep this safe!
# print(key.decode())  # Add to .env as ENCRYPTION_KEY
```

#### Use in Models

```python
# gowheels/models.py
from django.db import models
from .encryption import Cipher

class Vehicle(models.Model):
    vin = models.CharField(max_length=17)
    license_plate = models.CharField(max_length=20)
    owner_phone = models.CharField(max_length=15)  # Will encrypt
    
    def save(self, *args, **kwargs):
        # Encrypt sensitive fields before saving
        cipher = Cipher()
        self.owner_phone = cipher.encrypt(self.owner_phone)
        super().save(*args, **kwargs)
    
    def get_phone(self):
        # Decrypt when needed
        cipher = Cipher()
        return cipher.decrypt(self.owner_phone)
```

#### Strong Random Numbers

```python
# gowheels/utils.py
import secrets
import string

def generate_strong_password(length=16):
    """Generate cryptographically secure password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_otp(length=6):
    """Generate secure One-Time Password"""
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))

def generate_api_key():
    """Generate secure API key"""
    return secrets.token_urlsafe(32)
```

#### Test Cryptography

```bash
python manage.py shell

import secrets
from gowheels.encryption import Cipher

# Generate secure token
token = secrets.token_urlsafe(32)
print(f"Token: {token}")

# Encrypt/Decrypt
cipher = Cipher()
encrypted = cipher.encrypt("555-1234-5678")
print(f"Encrypted: {encrypted}")

decrypted = cipher.decrypt(encrypted)
print(f"Decrypted: {decrypted}")
```

#### Environment Setup

```bash
# .env
ENCRYPTION_KEY=your_fernet_key_from_Fernet.generate_key()

# requirements.txt
cryptography==42.0.0
pycryptodome==3.20.0
```

---

## Security Checklist

Before deploying to production:

- [ ] TLS enabled with valid certificate (not self-signed)
- [ ] HSTS header configured (Strict-Transport-Security)
- [ ] All cookies marked Secure, HttpOnly, SameSite=Strict
- [ ] Passwords using Argon2 (or bcrypt as fallback)
- [ ] Sensitive data encrypted at rest (encryption keys in .env)
- [ ] No plaintext credentials in code or version control
- [ ] Strong random token generation (secrets module)
- [ ] Certificate pinning documented for mobile clients
- [ ] SSL/TLS tests passing (A+ on ssllabs.com)
- [ ] Security headers present in all responses
- [ ] Dependency scan passing (pip-audit, Safety)
- [ ] Code review completed

---

## References

- [Django Security Documentation](https://docs.djangoproject.com/en/4.2/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Argon2 Parameters](https://argon2-cffi.readthedocs.io/)
- [Mozilla SSL Configuration](https://ssl-config.mozilla.org/)
- [CWE-327: Use of Broken Cryptography](https://cwe.mitre.org/data/definitions/327.html)

---

**Status:** ✅ Security features documented and ready for implementation
