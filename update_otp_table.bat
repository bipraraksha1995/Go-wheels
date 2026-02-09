@echo off
echo Updating OTP table for production 2FA...
echo.

REM Update database using MySQL command line
mysql -u root -p"sibi@100#" gowheels_new -e "CREATE TABLE IF NOT EXISTS gowheels_otp_backup AS SELECT * FROM gowheels_otp;"
mysql -u root -p"sibi@100#" gowheels_new -e "DROP TABLE IF EXISTS gowheels_otp;"
mysql -u root -p"sibi@100#" gowheels_new -e "CREATE TABLE gowheels_otp (id INT AUTO_INCREMENT PRIMARY KEY, phone VARCHAR(15) NOT NULL, otp_hash VARCHAR(64) NOT NULL, expires_at DATETIME NOT NULL, attempts INT DEFAULT 0, is_used BOOLEAN DEFAULT FALSE, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, INDEX idx_phone_used (phone, is_used), INDEX idx_expires (expires_at)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"

echo.
echo ✅ OTP table updated successfully!
echo.
echo Next steps:
echo 1. Test login: python manage.py runserver
echo 2. Go to http://localhost:8000/login/
echo 3. Enter phone number and receive SMS OTP
echo.
pause
