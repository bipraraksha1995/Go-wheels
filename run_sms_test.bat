@echo off
echo ============================================================
echo SMS DIAGNOSTIC TOOL - GoWheels
echo ============================================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python first.
    pause
    exit /b 1
)

echo.
echo Running SMS diagnostic...
echo.

python diagnose_sms.py

echo.
echo ============================================================
echo.
echo If SMS is not working:
echo 1. Check the error messages above
echo 2. Read SMS_FIX_SUMMARY.md for solutions
echo 3. Use console OTP as fallback (always shown in terminal)
echo.
echo ============================================================
pause
