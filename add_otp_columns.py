import pymysql
from datetime import datetime

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sibi@100#',
    database='gowheels_new'
)

cursor = conn.cursor()

# Add missing columns
try:
    cursor.execute("ALTER TABLE gowheels_otp ADD COLUMN created_at DATETIME DEFAULT NOW()")
    print("Added created_at column")
except:
    print("created_at already exists")

try:
    cursor.execute("ALTER TABLE gowheels_otp ADD COLUMN updated_at DATETIME DEFAULT NOW() ON UPDATE NOW()")
    print("Added updated_at column")
except:
    print("updated_at already exists")

try:
    cursor.execute("ALTER TABLE gowheels_otp ADD COLUMN expires_at DATETIME DEFAULT NOW()")
    print("Added expires_at column")
except:
    print("expires_at already exists")

conn.commit()
cursor.close()
conn.close()

print("Done")
