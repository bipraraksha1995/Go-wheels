# 🗄️ GoWheels - SQL Server Configuration Guide

## Overview
This guide explains how to migrate GoWheels from MySQL to Microsoft SQL Server.

---

## 📋 Prerequisites

### 1. Install SQL Server
- Download: [SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
- Or use existing SQL Server instance

### 2. Install ODBC Driver
- Download: [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- Windows: Run installer
- Linux: Follow Microsoft documentation

---

## 🚀 Setup Instructions

### Step 1: Install Required Packages
```bash
pip install -r requirements_sqlserver.txt
```

### Step 2: Configure Environment Variables
Copy `.env.sqlserver` to `.env` and update:
```env
DB_NAME=gowheels_db
DB_USER=sa
DB_PASSWORD=YourStrongPassword123!
DB_HOST=localhost
DB_PORT=1433
```

### Step 3: Create Database in SQL Server
```sql
-- Open SQL Server Management Studio (SSMS) or Azure Data Studio
-- Run this query:

CREATE DATABASE gowheels_db;
GO

USE gowheels_db;
GO
```

### Step 4: Update Django Settings
Replace `gowheels_project/settings.py` with `settings_sqlserver.py`:
```bash
# Backup current settings
copy gowheels_project\settings.py gowheels_project\settings_mysql_backup.py

# Use SQL Server settings
copy settings_sqlserver.py gowheels_project\settings.py
```

### Step 5: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 7: Run Server
```bash
python manage.py runserver
```

---

## 🔧 Configuration Details

### Database Settings (settings_sqlserver.py)
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'gowheels_db',
        'USER': 'sa',
        'PASSWORD': 'YourPassword',
        'HOST': 'localhost',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes'
        },
    }
}
```

---

## 📊 Database Comparison

| Feature | MySQL | SQL Server |
|---------|-------|------------|
| Engine | `django.db.backends.mysql` | `mssql` |
| Port | 3306 | 1433 |
| Package | `mysqlclient` | `mssql-django` |
| Driver | MySQL Connector | ODBC Driver 17 |

---

## 🔄 Migration from MySQL to SQL Server

### Option 1: Fresh Start (Recommended for Development)
1. Install SQL Server packages
2. Update settings to SQL Server
3. Run migrations
4. Manually re-enter data or use fixtures

### Option 2: Data Migration (Production)
1. Export data from MySQL:
```bash
python manage.py dumpdata > data_backup.json
```

2. Switch to SQL Server configuration

3. Import data:
```bash
python manage.py loaddata data_backup.json
```

---

## ✅ Verification

### Test Database Connection
```bash
python manage.py dbshell
```

### Check Migrations
```bash
python manage.py showmigrations
```

### Run Tests
```bash
python manage.py test
```

---

## 🐛 Troubleshooting

### Error: "ODBC Driver not found"
**Solution:** Install ODBC Driver 17 for SQL Server

### Error: "Login failed for user 'sa'"
**Solution:** 
1. Enable SQL Server Authentication
2. Check password in .env file
3. Verify SQL Server is running

### Error: "Cannot connect to server"
**Solution:**
1. Check SQL Server is running
2. Verify port 1433 is open
3. Check firewall settings

### Error: "TLS/SSL connection error"
**Solution:** Add `TrustServerCertificate=yes` in OPTIONS

---

## 📝 Notes

- **No code changes required** - Django ORM handles database differences
- **Models remain the same** - Only configuration changes
- **All features work** - Authentication, file uploads, etc.
- **Performance** - SQL Server optimized for Windows environments

---

## 🔐 Security Recommendations

1. **Strong Password:** Use complex password for SQL Server
2. **Firewall:** Restrict port 1433 access
3. **SSL/TLS:** Enable encrypted connections in production
4. **Backup:** Regular database backups
5. **User Permissions:** Create separate user instead of 'sa'

---

## 📞 Support

For issues or questions:
- Check Django documentation: https://docs.djangoproject.com/
- mssql-django docs: https://github.com/microsoft/mssql-django
- SQL Server docs: https://docs.microsoft.com/sql/

---

## ✨ Summary

**What Changed:**
- Database engine: MySQL → SQL Server
- Python package: mysqlclient → mssql-django
- Configuration: Updated settings.py and .env

**What Stayed Same:**
- All Python code (models, views, urls)
- Templates and static files
- Business logic
- API endpoints

**Result:** GoWheels now runs on SQL Server! 🎉
