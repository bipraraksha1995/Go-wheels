-- Create Pincode table manually
USE gowheels_db;

-- Create the table
CREATE TABLE IF NOT EXISTS gowheels_pincode (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(6) UNIQUE NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO gowheels_pincode (code, city, state, latitude, longitude, created_at) VALUES
('110001', 'New Delhi', 'Delhi', 28.6139, 77.2090, NOW()),
('110002', 'New Delhi', 'Delhi', 28.6304, 77.2177, NOW()),
('110003', 'New Delhi', 'Delhi', 28.6692, 77.2265, NOW()),
('110005', 'New Delhi', 'Delhi', 28.6328, 77.2197, NOW()),
('400001', 'Mumbai', 'Maharashtra', 18.9322, 72.8264, NOW()),
('400002', 'Mumbai', 'Maharashtra', 18.9388, 72.8356, NOW()),
('400003', 'Mumbai', 'Maharashtra', 18.9067, 72.8147, NOW()),
('560001', 'Bangalore', 'Karnataka', 12.9716, 77.5946, NOW()),
('560002', 'Bangalore', 'Karnataka', 12.9698, 77.6205, NOW()),
('560003', 'Bangalore', 'Karnataka', 12.9539, 77.6309, NOW());

-- Verify data
SELECT COUNT(*) as total_pincodes FROM gowheels_pincode;
SELECT * FROM gowheels_pincode LIMIT 5;