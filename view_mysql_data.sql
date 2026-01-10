-- View all your database data
USE gowheels_new;

-- Show all tables
SHOW TABLES;

-- View Users
SELECT * FROM gowheels_userprofile;

-- View Vehicles
SELECT id, brand_name, model_name, year, price, seller_phone, available 
FROM gowheels_vehicle;

-- View User details with auth_user
SELECT 
    up.id,
    up.phone,
    au.first_name,
    up.unique_id,
    up.pincode,
    up.blocked
FROM gowheels_userprofile up
JOIN auth_user au ON up.user_id = au.id;

-- Count records in each table
SELECT 'Users' as table_name, COUNT(*) as count FROM gowheels_userprofile
UNION ALL
SELECT 'Vehicles', COUNT(*) FROM gowheels_vehicle
UNION ALL
SELECT 'Vehicle Images', COUNT(*) FROM gowheels_vehicleimage
UNION ALL
SELECT 'Brand Images', COUNT(*) FROM gowheels_brandimage;

-- Your current data
SELECT 'Current Vehicle Data:' as info;
SELECT 
    CONCAT('ID: ', id, ' | ', brand_name, ' ', model_name, ' | Year: ', year, ' | Price: ₹', price, ' | Seller: ', seller_phone) as vehicle_info
FROM gowheels_vehicle;