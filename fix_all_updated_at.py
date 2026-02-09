import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sibi@100#',
    database='gowheels_new'
)

cursor = conn.cursor()

# Get all tables
cursor.execute("SHOW TABLES")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    # Check if updated_at exists
    cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'updated_at'")
    if not cursor.fetchone():
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_at DATETIME DEFAULT NOW() ON UPDATE NOW()")
            print(f"Added updated_at to {table}")
        except Exception as e:
            print(f"Could not add to {table}: {e}")

conn.commit()
cursor.close()
conn.close()

print("Done")
