-- Import Pincode Data from CSV to MySQL
USE gowheels_new;

-- Create Pincode Location Table (if not exists)
CREATE TABLE IF NOT EXISTS gowheels_pincodelocation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pincode VARCHAR(10) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Method 1: Load data from CSV file
-- Place your CSV file in MySQL secure directory or use --local-infile
LOAD DATA INFILE 'path/to/your/pincode.csv'
INTO TABLE gowheels_pincodelocation
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(pincode, city, state, latitude, longitude);

-- Method 2: Manual INSERT for sample data
INSERT INTO gowheels_pincodelocation (pincode, city, state, latitude, longitude) VALUES
('110001', 'New Delhi', 'Delhi', 28.6139, 77.2090),
('110002', 'New Delhi', 'Delhi', 28.6304, 77.2177),
('110003', 'New Delhi', 'Delhi', 28.6692, 77.2265),
('400001', 'Mumbai', 'Maharashtra', 18.9322, 72.8264),
('400002', 'Mumbai', 'Maharashtra', 18.9388, 72.8356),
('560001', 'Bangalore', 'Karnataka', 12.9716, 77.5946),
('560002', 'Bangalore', 'Karnataka', 12.9698, 77.6205),
('600001', 'Chennai', 'Tamil Nadu', 13.0827, 80.2707),
('700001', 'Kolkata', 'West Bengal', 22.5726, 88.3639),
('500001', 'Hyderabad', 'Telangana', 17.3850, 78.4867);

-- Method 3: Bulk insert using CSV format
-- Create temporary table for bulk operations
CREATE TEMPORARY TABLE temp_pincode (
    pincode VARCHAR(10),
    city VARCHAR(100),
    state VARCHAR(50),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8)
);

-- Insert CSV data into temp table
INSERT INTO temp_pincode VALUES
('110001', 'New Delhi', 'Delhi', 28.6139, 77.2090),
('110002', 'New Delhi', 'Delhi', 28.6304, 77.2177),
('110003', 'New Delhi', 'Delhi', 28.6692, 77.2265),
('400001', 'Mumbai', 'Maharashtra', 18.9322, 72.8264),
('400002', 'Mumbai', 'Maharashtra', 18.9388, 72.8356);

-- Transfer from temp to main table
INSERT INTO gowheels_pincodelocation (pincode, city, state, latitude, longitude)
SELECT pincode, city, state, latitude, longitude FROM temp_pincode;

-- Verify data
SELECT COUNT(*) as total_pincodes FROM gowheels_pincodelocation;
SELECT * FROM gowheels_pincodelocation LIMIT 10;

-- Create index for faster searches
CREATE INDEX idx_pincode ON gowheels_pincodelocation(pincode);
CREATE INDEX idx_city_state ON gowheels_pincodelocation(city, state);