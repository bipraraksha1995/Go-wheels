#!/usr/bin/env python
"""
Verify secrets are properly managed and not exposed
"""
import os
import re

def check_gitignore():
    """Verify .env is in .gitignore"""
    print("="*50)
    print("Checking .gitignore")
    print("="*50)
    
    gitignore_path = '.gitignore'
    if not os.path.exists(gitignore_path):
        print("[ERROR] .gitignore not found!")
        return False
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    if '.env' in content:
        print("[OK] .env is in .gitignore")
        return True
    else:
        print("[ERROR] .env NOT in .gitignore - ADD IT NOW!")
        return False

def check_env_example():
    """Verify .env.example exists and has no real secrets"""
    print("\n" + "="*50)
    print("Checking .env.example")
    print("="*50)
    
    if not os.path.exists('.env.example'):
        print("[WARN] .env.example not found (optional)")
        return True
    
    with open('.env.example', 'r') as f:
        content = f.read()
    
    # Check for placeholder values
    if 'your-secret-key-here' in content or 'your-' in content:
        print("[OK] .env.example has placeholder values")
        return True
    else:
        print("[WARN] .env.example might contain real secrets")
        return False

def check_code_for_secrets():
    """Check Python files for hardcoded secrets"""
    print("\n" + "="*50)
    print("Scanning code for hardcoded secrets")
    print("="*50)
    
    patterns = [
        (r'SECRET_KEY\s*=\s*["\'][^"\']{20,}["\']', 'SECRET_KEY'),
        (r'password\s*=\s*["\'][^"\']+["\']', 'password'),
        (r'GOCSPX-[A-Za-z0-9_-]+', 'Google OAuth Secret'),
        (r'sk_live_[A-Za-z0-9]+', 'Stripe Secret Key'),
        (r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']', 'AWS Secret'),
    ]
    
    issues_found = []
    
    for root, dirs, files in os.walk('.'):
        # Skip virtual env and cache
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern, secret_type in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            # Exclude config() calls
                            if 'config(' not in content[max(0, content.find(matches[0])-50):content.find(matches[0])+50]:
                                issues_found.append((filepath, secret_type))
                except:
                    pass
    
    if issues_found:
        print("[ERROR] Potential hardcoded secrets found:")
        for filepath, secret_type in issues_found:
            print(f"  - {filepath}: {secret_type}")
        return False
    else:
        print("[OK] No hardcoded secrets found in Python files")
        return True

def check_env_file():
    """Verify .env file exists and is not empty"""
    print("\n" + "="*50)
    print("Checking .env file")
    print("="*50)
    
    if not os.path.exists('.env'):
        print("[ERROR] .env file not found!")
        print("  Create it with: cp .env.example .env")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    required_vars = ['SECRET_KEY', 'DB_PASSWORD', 'GOOGLE_CLIENT_ID']
    missing = []
    
    for var in required_vars:
        if var not in content:
            missing.append(var)
    
    if missing:
        print(f"[WARN] Missing variables: {', '.join(missing)}")
    else:
        print("[OK] .env file has required variables")
    
    # Check for placeholder values
    if 'your-secret-key-here' in content:
        print("[WARN] .env still has placeholder values - update them!")
    
    return True

def check_decouple_usage():
    """Verify python-decouple is being used"""
    print("\n" + "="*50)
    print("Checking python-decouple usage")
    print("="*50)
    
    settings_file = 'gowheels_project/settings.py'
    if not os.path.exists(settings_file):
        print("[ERROR] settings.py not found")
        return False
    
    with open(settings_file, 'r') as f:
        content = f.read()
    
    if 'from decouple import config' in content:
        print("[OK] Using python-decouple for config")
        return True
    else:
        print("[ERROR] python-decouple not imported in settings.py")
        return False

def main():
    print("="*50)
    print("GoWheels Secrets Security Check")
    print("="*50)
    
    results = []
    results.append(("Gitignore", check_gitignore()))
    results.append(("Env Example", check_env_example()))
    results.append(("Code Scan", check_code_for_secrets()))
    results.append(("Env File", check_env_file()))
    results.append(("Decouple", check_decouple_usage()))
    
    print("\n" + "="*50)
    print("Summary")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {check}")
    
    print(f"\nScore: {passed}/{total}")
    
    if passed == total:
        print("\n[SUCCESS] All security checks passed!")
        print("Your secrets are properly managed.")
    else:
        print("\n[WARNING] Some checks failed.")
        print("Review the issues above and fix them.")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    exit(main())
