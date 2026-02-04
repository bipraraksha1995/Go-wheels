@echo off
REM GoWheels Vulnerability Scanning Setup Script (Windows)
REM This script sets up all security scanning tools

setlocal enabledelayedexpansion

echo.
echo 🔍 GoWheels Vulnerability Scanning Setup
echo ==========================================
echo.

REM Check Python
echo 🐍 Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ %PYTHON_VERSION%
echo.

REM Install pip-audit
echo 📦 Installing pip-audit...
pip install pip-audit
if errorlevel 1 (
    echo ✗ Failed to install pip-audit
    exit /b 1
)
echo ✓ pip-audit installed
echo.

REM Install Safety
echo 📦 Installing Safety...
pip install safety
if errorlevel 1 (
    echo ✗ Failed to install Safety
    exit /b 1
)
echo ✓ Safety installed
echo.

REM Install Bandit
echo 📦 Installing Bandit...
pip install bandit
if errorlevel 1 (
    echo ✗ Failed to install Bandit
    exit /b 1
)
echo ✓ Bandit installed
echo.

REM Install pre-commit
echo 📦 Installing pre-commit...
pip install pre-commit
if errorlevel 1 (
    echo ✗ Failed to install pre-commit
    exit /b 1
)
echo ✓ pre-commit installed
echo.

REM Install pre-commit hooks
echo 🔌 Setting up pre-commit hooks...
pre-commit install
if errorlevel 1 (
    echo ✗ Failed to install pre-commit hooks
    exit /b 1
)
echo ✓ pre-commit hooks installed
echo.

REM Create reports directory
echo 📁 Creating reports directory...
if not exist "reports" mkdir reports
echo ✓ reports\ created
echo.

REM Run initial scan
echo 🔍 Running initial vulnerability scan...
echo.

echo    Running pip-audit...
pip-audit > reports\initial-pip-audit.json 2>nul

echo    Running Safety...
safety check --json > reports\initial-safety.json 2>nul

echo    Running Bandit...
bandit -r gowheels\ -f json > reports\initial-bandit.json 2>nul

echo.
echo ✓ Scans complete
echo.

REM Print summary
echo ==========================================
echo ✅ Setup Complete!
echo ==========================================
echo.
echo 📋 What was installed:
echo    • pip-audit (Python dependency scanner)
echo    • Safety (Alternative Python scanner)
echo    • Bandit (Python security analysis)
echo    • pre-commit (Git hook automation)
echo.
echo 📊 Initial scan reports saved to:
echo    • reports\initial-pip-audit.json
echo    • reports\initial-safety.json
echo    • reports\initial-bandit.json
echo.
echo 🚀 Next steps:
echo    1. Review scan reports: dir /b reports\
echo    2. Check for vulnerabilities: pip-audit
echo    3. Test pre-commit hooks: pre-commit run --all-files
echo    4. Read documentation:
echo       • VULNERABILITY_SCANNING_GUIDE.md
echo       • VULNERABILITY_REMEDIATION.md
echo.
echo 🔔 GitHub Actions:
echo    • CI/CD pipeline: .github\workflows\security-scan.yml
echo    • Runs on: Push, PR, Daily schedule
echo    • Results: Artifacts + PR comments
echo.
echo 📝 Configuration files:
echo    • pyproject.toml (pip-audit config)
echo    • .pre-commit-config.yaml (Git hooks)
echo    • .github\workflows\security-scan.yml (CI/CD)
echo.

endlocal
