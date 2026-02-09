-- Update OTP table for production 2FA
-- Run this SQL directly on your database

-- Step 1: Backup existing OTP table
CREATE TABLE gowheels_otp_backup AS SELECT * FROM gowheels_otp;

-- Step 2: Drop old table
DROP TABLE IF EXISTS gowheels_otp;

-- Step 3: Create new secure OTP table
CREATE TABLE gowheels_otp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(15) NOT NULL,
    otp_hash VARCHAR(64) NOT NULL,
    expires_at DATETIME NOT NULL,
    attempts INT DEFAULT 0,
    is_used BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_phone_used (phone, is_used),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Done! Your OTP table is now production-ready
