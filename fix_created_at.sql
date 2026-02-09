-- Fix created_at field to have default value
ALTER TABLE gowheels_pincodemapping 
MODIFY COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
