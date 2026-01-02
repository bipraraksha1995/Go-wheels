import pymysql
from decouple import config

try:
    # Connect to MySQL server (without specifying database)
    connection = pymysql.connect(
        host=config('DB_HOST', default='localhost'),
        user=config('DB_USER', default='root'),
        password=config('DB_PASSWORD', default='sibi@100#'),
        port=int(config('DB_PORT', default='3306'))
    )
    
    cursor = connection.cursor()
    
    # Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS gowheels_new")
    print("Database 'gowheels_new' created successfully!")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")