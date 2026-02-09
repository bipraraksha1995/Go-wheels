-- GoWheels Database Schema
-- MySQL Database Structure

CREATE DATABASE IF NOT EXISTS gowheels_new;
USE gowheels_new;

-- 1. Django Auth User Table (Built-in)
-- auth_user table is created by Django automatically

-- 2. Admin Group Table
CREATE TABLE gowheels_admingroup (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. Admin Category Table
CREATE TABLE gowheels_admincategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(100) NOT NULL,
    group_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES gowheels_admingroup(id) ON DELETE CASCADE
);

-- 4. Admin Brand Table
CREATE TABLE gowheels_adminbrand (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES gowheels_admincategory(id) ON DELETE CASCADE
);

-- 5. Admin Model Table
CREATE TABLE gowheels_adminmodel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(100) NOT NULL,
    brand_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES gowheels_adminbrand(id) ON DELETE CASCADE
);

-- 6. User Profile Table
CREATE TABLE gowheels_userprofile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    unique_id VARCHAR(20) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL UNIQUE,
    pincode VARCHAR(10) NOT NULL,
    profile_photo VARCHAR(100),
    blocked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- 7. Pincode Mapping Table
CREATE TABLE gowheels_pincodemapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    main_pincode VARCHAR(10) NOT NULL,
    nearby_pincode VARCHAR(10) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_pincode_mapping (main_pincode, nearby_pincode)
);

-- 8. Category Table
CREATE TABLE gowheels_category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    image VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9. Vehicle Table (Main Table)
CREATE TABLE gowheels_vehicle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    brand_name VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    state VARCHAR(50) NOT NULL,
    hourly_start_range DECIMAL(8,2) NOT NULL DEFAULT 100.00,
    hourly_end_range DECIMAL(8,2) NOT NULL DEFAULT 3000.00,
    daily_start_range DECIMAL(8,2) NOT NULL DEFAULT 100.00,
    daily_end_range DECIMAL(8,2) NOT NULL DEFAULT 3000.00,
    per_day_price DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    per_hour_price DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    min_price DECIMAL(8,2) NOT NULL DEFAULT 100.00,
    max_price DECIMAL(8,2) NOT NULL DEFAULT 3000.00,
    price DECIMAL(8,2) NOT NULL,
    pricing_type VARCHAR(20) NOT NULL,
    unit_type VARCHAR(20) NOT NULL DEFAULT 'unit_price',
    category_image VARCHAR(100),
    brand_image VARCHAR(100),
    model_image VARCHAR(100),
    seller_phone VARCHAR(15),
    pincode VARCHAR(10),
    village VARCHAR(100),
    owner_name VARCHAR(100),
    available BOOLEAN NOT NULL DEFAULT TRUE,
    approval_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    added_by VARCHAR(50) NOT NULL DEFAULT 'super_admin',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 10. Vehicle Image Table
CREATE TABLE gowheels_vehicleimage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    image VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES gowheels_vehicle(id) ON DELETE CASCADE
);

-- 11. Vehicle Video Table
CREATE TABLE gowheels_vehiclevideo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    video VARCHAR(100) NOT NULL,
    duration FLOAT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES gowheels_vehicle(id) ON DELETE CASCADE
);

-- 12. Brand Image Table
CREATE TABLE gowheels_brandimage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(20) NOT NULL,
    category_ref_id INT,
    name VARCHAR(100) NOT NULL DEFAULT 'Brand Name',
    image VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_ref_id) REFERENCES gowheels_category(id) ON DELETE CASCADE
);

-- 13. Model Image Table
CREATE TABLE gowheels_modelimage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(20) NOT NULL,
    brand_id INT,
    name VARCHAR(100) NOT NULL DEFAULT 'Model Name',
    image VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES gowheels_brandimage(id) ON DELETE CASCADE
);

-- 14. Vehicle Click Table
CREATE TABLE gowheels_vehicleclick (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    buyer_phone VARCHAR(15) NOT NULL,
    buyer_name VARCHAR(100),
    clicked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES gowheels_vehicle(id) ON DELETE CASCADE
);

-- 15. Booking Table
CREATE TABLE gowheels_booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES gowheels_vehicle(id) ON DELETE CASCADE
);

-- Create Indexes for Performance
CREATE INDEX idx_vehicle_available ON gowheels_vehicle(available);
CREATE INDEX idx_vehicle_approval ON gowheels_vehicle(approval_status);
CREATE INDEX idx_vehicle_seller ON gowheels_vehicle(seller_phone);
CREATE INDEX idx_vehicle_pincode ON gowheels_vehicle(pincode);
CREATE INDEX idx_userprofile_phone ON gowheels_userprofile(phone);
CREATE INDEX idx_vehicleclick_vehicle ON gowheels_vehicleclick(vehicle_id);