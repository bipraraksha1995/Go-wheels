@echo off
echo ========================================
echo GoWheels - SQL Server Setup
echo ========================================
echo.

echo Step 1: Installing SQL Server packages...
pip install mssql-django pyodbc
echo.

echo Step 2: Backing up current settings...
copy gowheels_project\settings.py gowheels_project\settings_mysql_backup.py
echo.

echo Step 3: Applying SQL Server settings...
copy settings_sqlserver.py gowheels_project\settings.py
echo.

echo Step 4: Copying environment file...
copy .env.sqlserver .env
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Update .env file with your SQL Server credentials
echo 2. Create database in SQL Server: CREATE DATABASE gowheels_db;
echo 3. Run: python manage.py migrate
echo 4. Run: python manage.py runserver
echo.
pause
