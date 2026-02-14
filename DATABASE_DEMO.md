# 📊 Database Operations Demo - GoWheels

## ✅ What I Can Demonstrate

### 1️⃣ **Create Operations (INSERT)**

```python
# Django Shell Example
python manage.py shell

# Create User
from django.contrib.auth.models import User
from gowheels.models import UserProfile, Vehicle

# Insert User
user = User.objects.create(
    username='9876543210',
    first_name='John Doe'
)

# Insert User Profile
profile = UserProfile.objects.create(
    user=user,
    phone='9876543210',
    pincode='600001'
)

# Insert Vehicle
vehicle = Vehicle.objects.create(
    category_name='Car',
    brand_name='Toyota',
    model_name='Camry',
    year=2024,
    state='Tamil Nadu',
    price=1500,
    pricing_type='per-day',
    seller_phone='9876543210',
    pincode='600001',
    approval_status='approved',
    available=True
)
```

### 2️⃣ **Read Operations (SELECT)**

```python
# Get all vehicles
vehicles = Vehicle.objects.all()

# Filter vehicles
cars = Vehicle.objects.filter(category_name='Car')
available = Vehicle.objects.filter(available=True)

# Get specific vehicle
vehicle = Vehicle.objects.get(id=1)

# Count records
total_vehicles = Vehicle.objects.count()
```

### 3️⃣ **Update Operations (UPDATE)**

```python
# Update single record
vehicle = Vehicle.objects.get(id=1)
vehicle.price = 2000
vehicle.save()

# Bulk update
Vehicle.objects.filter(category_name='Car').update(available=True)
```

### 4️⃣ **Delete Operations (DELETE)**

```python
# Delete single record
vehicle = Vehicle.objects.get(id=1)
vehicle.delete()

# Bulk delete
Vehicle.objects.filter(available=False).delete()
```

### 5️⃣ **Complex Queries (JOIN, AGGREGATE)**

```python
from django.db.models import Count, Avg

# Count vehicles by category
Vehicle.objects.values('category_name').annotate(count=Count('id'))

# Average price
Vehicle.objects.aggregate(avg_price=Avg('price'))

# Filter with multiple conditions
Vehicle.objects.filter(
    category_name='Car',
    available=True,
    price__lte=2000
)
```

## 🗄️ Database Models

### User Management
- **User** - Django auth user
- **UserProfile** - Extended user info (phone, pincode, unique_id)

### Vehicle Management
- **Vehicle** - Vehicle listings
- **VehicleImage** - Vehicle photos
- **VehicleVideo** - Vehicle videos

### Admin Hierarchy
- **AdminGroup** → **AdminCategory** → **AdminBrand** → **AdminModel**

### Features
- **Chat** & **Message** - Messaging system
- **Wishlist** - Saved vehicles
- **Referral** - Referral program
- **OTP** - Authentication codes

## 📝 SQL Equivalent

### Django ORM vs SQL

| Django ORM | SQL Equivalent |
|------------|----------------|
| `Vehicle.objects.all()` | `SELECT * FROM vehicle` |
| `Vehicle.objects.filter(price__lte=2000)` | `SELECT * FROM vehicle WHERE price <= 2000` |
| `Vehicle.objects.create(...)` | `INSERT INTO vehicle VALUES (...)` |
| `vehicle.save()` | `UPDATE vehicle SET ... WHERE id=...` |
| `vehicle.delete()` | `DELETE FROM vehicle WHERE id=...` |

## 🎯 Key Features

### 1. **ORM (Object-Relational Mapping)**
- Write Python code instead of SQL
- Database-agnostic (works with MySQL, SQL Server, PostgreSQL)
- Automatic SQL generation
- Protection against SQL injection

### 2. **Migrations**
- Version control for database schema
- Automatic table creation
- Schema changes tracked

### 3. **Relationships**
- One-to-One: User ↔ UserProfile
- One-to-Many: Vehicle → VehicleImage
- Many-to-Many: (if needed)

### 4. **Transactions**
```python
from django.db import transaction

with transaction.atomic():
    user = User.objects.create(...)
    profile = UserProfile.objects.create(user=user, ...)
    # Both succeed or both fail
```

## 🚀 Live Demo Commands

### Start Django Shell
```bash
python manage.py shell
```

### Quick Test
```python
# Import models
from gowheels.models import Vehicle

# Count vehicles
print(f"Total Vehicles: {Vehicle.objects.count()}")

# Get recent vehicles
for v in Vehicle.objects.all()[:5]:
    print(f"{v.brand_name} {v.model_name} - ₹{v.price}")
```

## 📊 Database Statistics

```python
from django.contrib.auth.models import User
from gowheels.models import Vehicle, UserProfile

# Get counts
users = User.objects.count()
vehicles = Vehicle.objects.count()
available = Vehicle.objects.filter(available=True).count()

print(f"Users: {users}")
print(f"Vehicles: {vehicles}")
print(f"Available: {available}")
```

## ✅ What This Demonstrates

1. **CRUD Operations** - Create, Read, Update, Delete
2. **Complex Queries** - Filtering, aggregation, joins
3. **Database Relationships** - Foreign keys, one-to-many
4. **ORM Proficiency** - Django ORM expertise
5. **SQL Knowledge** - Understanding of database concepts
6. **Data Modeling** - Proper schema design

## 🎓 Skills Shown

- ✅ Database design and modeling
- ✅ ORM (Object-Relational Mapping)
- ✅ SQL query optimization
- ✅ Data relationships
- ✅ Transaction management
- ✅ Database migrations
- ✅ Multi-database support (MySQL, SQL Server)

---

**Status:** Ready to demonstrate database operations ✅  
**Note:** Requires database server running (MySQL or SQL Server)
