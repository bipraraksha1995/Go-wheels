#!/bin/bash
# GoWheels Day 1 Critical Security Remediation
# Execute this script immediately to fix critical security issues

set -e  # Exit on error

echo "=========================================="
echo "GoWheels Day 1 Security Remediation"
echo "=========================================="
echo ""

# Step 1: Vulnerability Scanning
echo "Step 1: Scanning for vulnerabilities..."
echo "------------------------------------------"

# Install scanners
pip install pip-audit safety

# Run pip-audit
echo "Running pip-audit..."
pip-audit --format json --output pip-audit-report.json || true
pip-audit

# Run safety check
echo "Running safety check..."
safety check --json --output safety-report.json || true
safety check

# Fix vulnerabilities
echo "Fixing vulnerabilities..."
pip-audit --fix || true

echo "✅ Vulnerability scan complete. Review reports: pip-audit-report.json, safety-report.json"
echo ""

# Step 2: Secrets Scanning
echo "Step 2: Scanning for secrets..."
echo "------------------------------------------"

# Check if gitleaks is installed
if ! command -v gitleaks &> /dev/null; then
    echo "⚠️  gitleaks not installed. Download from: https://github.com/gitleaks/gitleaks/releases"
    echo "   For now, using grep to find potential secrets..."
    
    # Basic secret detection
    echo "Checking for potential secrets in .env..."
    if [ -f ".env" ]; then
        echo "Found .env file - MUST rotate these secrets:"
        grep -E "(SECRET_KEY|PASSWORD|TOKEN|API_KEY)" .env || true
    fi
else
    echo "Running gitleaks..."
    gitleaks detect --source . --report-path gitleaks-report.json --verbose || true
fi

echo ""
echo "⚠️  CRITICAL: Rotate ALL secrets found above!"
echo "   1. Generate new secrets"
echo "   2. Update .env file"
echo "   3. Restart application"
echo "   4. Revoke old credentials"
echo ""

# Step 3: Update .gitignore
echo "Step 3: Securing .gitignore..."
echo "------------------------------------------"

if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "✅ Added .env to .gitignore"
else
    echo "✅ .env already in .gitignore"
fi

# Add other sensitive files
cat >> .gitignore << 'EOF'

# Security
*.pem
*.key
*.p12
*.pfx
secrets/
credentials/
*-report.json
gitleaks-report.json
pip-audit-report.json
safety-report.json
EOF

echo "✅ Updated .gitignore"
echo ""

# Step 4: Verify HTTPS Configuration
echo "Step 4: Verifying HTTPS configuration..."
echo "------------------------------------------"

# Check settings.py for HTTPS enforcement
if grep -q "SECURE_SSL_REDIRECT = True" gowheels_project/settings.py; then
    echo "✅ HTTPS redirect enabled"
else
    echo "⚠️  HTTPS redirect NOT enabled"
    echo "   Add to settings.py:"
    echo "   SECURE_SSL_REDIRECT = True"
fi

if grep -q "SECURE_HSTS_SECONDS" gowheels_project/settings.py; then
    echo "✅ HSTS configured"
else
    echo "⚠️  HSTS NOT configured"
    echo "   Add to settings.py:"
    echo "   SECURE_HSTS_SECONDS = 31536000"
fi

echo ""

# Step 5: Verify Secure Cookies
echo "Step 5: Verifying secure cookie configuration..."
echo "------------------------------------------"

if grep -q "SESSION_COOKIE_SECURE = True" gowheels_project/settings.py; then
    echo "✅ Secure session cookies enabled"
else
    echo "⚠️  Secure session cookies NOT enabled"
fi

if grep -q "SESSION_COOKIE_HTTPONLY = True" gowheels_project/settings.py; then
    echo "✅ HttpOnly session cookies enabled"
else
    echo "⚠️  HttpOnly session cookies NOT enabled"
fi

if grep -q "SESSION_COOKIE_SAMESITE = 'Strict'" gowheels_project/settings.py; then
    echo "✅ SameSite session cookies enabled"
else
    echo "⚠️  SameSite session cookies NOT enabled"
fi

echo ""

# Step 6: Check for SQL Injection Vulnerabilities
echo "Step 6: Checking for SQL injection vulnerabilities..."
echo "------------------------------------------"

# Search for raw SQL queries
echo "Searching for raw SQL queries..."
if grep -r "cursor.execute" gowheels/ --include="*.py" | grep -v ".pyc"; then
    echo "⚠️  Found raw SQL queries - review for SQL injection"
else
    echo "✅ No raw SQL queries found"
fi

# Search for string formatting in queries
if grep -r "\.execute.*%" gowheels/ --include="*.py" | grep -v ".pyc"; then
    echo "⚠️  Found string formatting in queries - potential SQL injection"
else
    echo "✅ No string formatting in queries"
fi

echo ""

# Step 7: Summary and Next Steps
echo "=========================================="
echo "Day 1 Remediation Summary"
echo "=========================================="
echo ""
echo "Completed:"
echo "  ✅ Vulnerability scan"
echo "  ✅ Secrets scan"
echo "  ✅ .gitignore updated"
echo "  ✅ Security configuration verified"
echo "  ✅ SQL injection check"
echo ""
echo "IMMEDIATE ACTIONS REQUIRED:"
echo "  1. Review vulnerability reports"
echo "  2. Rotate ALL secrets in .env"
echo "  3. Obtain SSL certificate (certbot)"
echo "  4. Configure Nginx with TLS"
echo "  5. Test HTTPS redirect"
echo ""
echo "Generated Reports:"
echo "  - pip-audit-report.json"
echo "  - safety-report.json"
echo "  - gitleaks-report.json (if gitleaks installed)"
echo ""
echo "Next: Run Day 2 remediation (TLS setup)"
echo "=========================================="
