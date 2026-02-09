@echo off
echo ========================================
echo GoWheels Test Suite Runner
echo ========================================
echo.

echo [1/5] Running Unit Tests...
python manage.py test tests.test_auth --verbosity=2
if %errorlevel% neq 0 (
    echo FAILED: Unit tests failed
    exit /b 1
)
echo PASSED: Unit tests
echo.

echo [2/5] Running Integration Tests...
python manage.py test tests.test_integration --verbosity=2
if %errorlevel% neq 0 (
    echo FAILED: Integration tests failed
    exit /b 1
)
echo PASSED: Integration tests
echo.

echo [3/5] Running Security Scans...
bandit -r gowheels/ -ll
if %errorlevel% neq 0 (
    echo WARNING: Security issues found
)
echo.

echo [4/5] Checking Dependencies...
pip-audit
if %errorlevel% neq 0 (
    echo WARNING: Vulnerable dependencies found
)
echo.

echo [5/5] Generating Coverage Report...
coverage run --source=gowheels manage.py test tests
coverage report --fail-under=70
if %errorlevel% neq 0 (
    echo FAILED: Coverage below 70%%
    exit /b 1
)
echo.

echo ========================================
echo ALL TESTS PASSED!
echo ========================================
coverage html
echo Coverage report: htmlcov\index.html
