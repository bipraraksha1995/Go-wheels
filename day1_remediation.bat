@echo off
REM GoWheels Day 1 Critical Security Remediation (Windows)
REM Execute this script immediately to fix critical security issues

echo ==========================================
echo GoWheels Day 1 Security Remediation
echo ==========================================
echo.

REM Step 1: Vulnerability Scanning
echo Step 1: Scanning for vulnerabilities...
echo ------------------------------------------

pip install pip-audit safety

echo Running pip-audit...
pip-audit --format json --output pip-audit-report.json
pip-audit

echo Running safety check...
safety check --json --output safety-report.json
safety check

echo Fixing vulnerabilities...
pip-audit --fix

echo Done: Vulnerability scan complete
echo.

REM Step 2: Secrets Scanning
echo Step 2: Scanning for secrets...
echo ------------------------------------------

echo Checking for potential secrets in .env...
if exist .env (
    echo Found .env file - MUST rotate these secrets:
    findstr /I "SECRET_KEY PASSWORD TOKEN API_KEY" .env
)

echo.
echo WARNING: Rotate ALL secrets found above!
echo   1. Generate new secrets
echo   2. Update .env file
echo   3. Restart application
echo   4. Revoke old credentials
echo.

REM Step 3: Update .gitignore
echo Step 3: Securing .gitignore...
echo ------------------------------------------

findstr /C:".env" .gitignore >nul 2>&1
if errorlevel 1 (
    echo .env>> .gitignore
    echo Added .env to .gitignore
) else (
    echo .env already in .gitignore
)

REM Add other sensitive files
echo.>> .gitignore
echo # Security>> .gitignore
echo *.pem>> .gitignore
echo *.key>> .gitignore
echo *-report.json>> .gitignore

echo Updated .gitignore
echo.

REM Step 4: Summary
echo ==========================================
echo Day 1 Remediation Summary
echo ==========================================
echo.
echo Completed:
echo   [X] Vulnerability scan
echo   [X] Secrets scan
echo   [X] .gitignore updated
echo.
echo IMMEDIATE ACTIONS REQUIRED:
echo   1. Review vulnerability reports
echo   2. Rotate ALL secrets in .env
echo   3. Obtain SSL certificate
echo   4. Configure reverse proxy with TLS
echo   5. Test HTTPS redirect
echo.
echo Generated Reports:
echo   - pip-audit-report.json
echo   - safety-report.json
echo.
echo Next: Run Day 2 remediation (TLS setup)
echo ==========================================

pause
