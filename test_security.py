#!/usr/bin/env python
"""
Security Testing Script
Tests rate limiting, security headers, and CSRF protection
"""
import requests
import time
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000"


def test_security_headers():
    """Test security headers"""
    print(f"\n{Fore.CYAN}=== Testing Security Headers ==={Style.RESET_ALL}")
    
    response = requests.get(f"{BASE_URL}/")
    headers = response.headers
    
    required_headers = {
        'Content-Security-Policy': 'CSP',
        'X-Frame-Options': 'Clickjacking Protection',
        'X-Content-Type-Options': 'MIME Sniffing Protection',
        'X-XSS-Protection': 'XSS Filter',
        'Referrer-Policy': 'Referrer Policy',
        'Permissions-Policy': 'Permissions Policy',
    }
    
    for header, description in required_headers.items():
        if header in headers:
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {description}: {headers[header][:50]}...")
        else:
            print(f"{Fore.RED}✗{Style.RESET_ALL} {description}: Missing")


def test_rate_limiting():
    """Test rate limiting"""
    print(f"\n{Fore.CYAN}=== Testing Rate Limiting ==={Style.RESET_ALL}")
    
    endpoint = f"{BASE_URL}/api/v1/vehicles/"
    
    print(f"Sending 105 requests to {endpoint}...")
    
    for i in range(105):
        response = requests.get(endpoint)
        
        if response.status_code == 429:
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} Rate limit triggered at request {i+1}")
            print(f"  Retry-After: {response.headers.get('Retry-After')} seconds")
            print(f"  X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit')}")
            return
        
        if i % 20 == 0:
            remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
            print(f"  Request {i+1}: Remaining = {remaining}")
    
    print(f"{Fore.RED}✗{Style.RESET_ALL} Rate limit not triggered after 105 requests")


def test_csrf_protection():
    """Test CSRF protection"""
    print(f"\n{Fore.CYAN}=== Testing CSRF Protection ==={Style.RESET_ALL}")
    
    # Test without CSRF token
    response = requests.post(f"{BASE_URL}/login/", data={
        'phone': '7305675201',
        'otp': '123456'
    })
    
    if response.status_code == 403:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} CSRF protection active (403 without token)")
    else:
        print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} CSRF protection may be disabled")


def test_hsts():
    """Test HSTS header"""
    print(f"\n{Fore.CYAN}=== Testing HSTS ==={Style.RESET_ALL}")
    
    try:
        response = requests.get(f"https://localhost:8000/", verify=False)
        hsts = response.headers.get('Strict-Transport-Security')
        
        if hsts:
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} HSTS enabled: {hsts}")
        else:
            print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} HSTS not enabled (expected in development)")
    except:
        print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} HTTPS not available (expected in development)")


def test_cors():
    """Test CORS configuration"""
    print(f"\n{Fore.CYAN}=== Testing CORS ==={Style.RESET_ALL}")
    
    response = requests.get(f"{BASE_URL}/api/v1/vehicles/", headers={
        'Origin': 'https://evil.com'
    })
    
    cors_header = response.headers.get('Access-Control-Allow-Origin')
    
    if cors_header == 'https://evil.com':
        print(f"{Fore.RED}✗{Style.RESET_ALL} CORS allows any origin (security risk)")
    elif cors_header:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} CORS configured: {cors_header}")
    else:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} CORS not allowing untrusted origins")


if __name__ == '__main__':
    print(f"{Fore.YELLOW}GoWheels Security Testing{Style.RESET_ALL}")
    print(f"Testing: {BASE_URL}\n")
    
    test_security_headers()
    test_rate_limiting()
    test_csrf_protection()
    test_hsts()
    test_cors()
    
    print(f"\n{Fore.CYAN}=== Testing Complete ==={Style.RESET_ALL}\n")
