-- MySQL Database Encryption Setup
-- Enable encryption at rest for GoWheels database

-- 1. Enable encryption for existing tables
ALTER TABLE gowheels_userprofile ENCRYPTION='Y';
ALTER TABLE gowheels_otp ENCRYPTION='Y';
ALTER TABLE gowheels_vehicle ENCRYPTION='Y';
ALTER TABLE gowheels_vehicleimage ENCRYPTION='Y';
ALTER TABLE gowheels_vehiclevideo ENCRYPTION='Y';
ALTER TABLE gowheels_brandimage ENCRYPTION='Y';
ALTER TABLE gowheels_modelimage ENCRYPTION='Y';

-- 2. Create encrypted tablespace
CREATE TABLESPACE gowheels_encrypted
  ADD DATAFILE 'gowheels_encrypted.ibd'
  ENCRYPTION='Y'
  ENGINE=InnoDB;

-- 3. Enable binary log encryption
SET GLOBAL binlog_encryption=ON;

-- 4. Enable redo log encryption
SET GLOBAL innodb_redo_log_encrypt=ON;

-- 5. Enable undo log encryption
SET GLOBAL innodb_undo_log_encrypt=ON;

-- 6. Verify encryption status
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    CREATE_OPTIONS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'gowheels_new'
  AND CREATE_OPTIONS LIKE '%ENCRYPTION%';

-- 7. Add encrypted columns for PII
ALTER TABLE gowheels_userprofile 
  ADD COLUMN phone_encrypted VARCHAR(500) AFTER phone,
  ADD COLUMN email_encrypted VARCHAR(500) AFTER phone_encrypted;

-- 8. Create audit log table
CREATE TABLE gowheels_pii_access_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_accessed_at (accessed_at)
) ENCRYPTION='Y';

-- 9. Create data retention policy table
CREATE TABLE gowheels_data_retention (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    retention_days INT NOT NULL,
    last_cleanup TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENCRYPTION='Y';

-- 10. Insert retention policies
INSERT INTO gowheels_data_retention (table_name, retention_days) VALUES
('gowheels_otp', 1),
('gowheels_pii_access_log', 1095),
('auth_session', 1),
('gowheels_userprofile', 730);

-- 11. Create stored procedure for data cleanup
DELIMITER //
CREATE PROCEDURE cleanup_expired_data()
BEGIN
    -- Delete expired OTPs
    DELETE FROM gowheels_otp 
    WHERE expires_at < NOW();
    
    -- Delete old sessions
    DELETE FROM django_session 
    WHERE expire_date < NOW();
    
    -- Delete old access logs (3 years)
    DELETE FROM gowheels_pii_access_log 
    WHERE accessed_at < DATE_SUB(NOW(), INTERVAL 1095 DAY);
    
    -- Log cleanup
    INSERT INTO gowheels_pii_access_log (user_id, field_name, action)
    VALUES (0, 'system', 'DATA_CLEANUP');
END //
DELIMITER ;

-- 12. Schedule daily cleanup (requires EVENT scheduler)
SET GLOBAL event_scheduler = ON;

CREATE EVENT daily_data_cleanup
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO CALL cleanup_expired_data();

-- 13. Grant minimal permissions
CREATE USER IF NOT EXISTS 'gowheels_app'@'localhost' 
IDENTIFIED BY 'secure_password_here';

GRANT SELECT, INSERT, UPDATE, DELETE 
ON gowheels_new.* 
TO 'gowheels_app'@'localhost';

-- No DROP, ALTER, or admin privileges
FLUSH PRIVILEGES;
