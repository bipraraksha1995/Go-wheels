# Database Test Script for GoWheels
# Run with: python manage.py shell < test_database.py

from django.contrib.auth.models import User
from gowheels.models import UserProfile, Vehicle, VehicleImage, AdminGroup, AdminCategory, AdminBrand, AdminModel

print("=" * 60)
print("🗄️ GoWheels Database Test")
print("=" * 60)

# Test 1: Create User
print("\n1️⃣ Creating User...")
user, created = User.objects.get_or_create(
    username='9876543210',
    defaults={'first_name': 'Test User'}
)
print(f"✅ User: {user.username} - {'Created' if created else 'Already exists'}")

# Test 2: Create User Profile
print("\n2️⃣ Creating User Profile...")
profile, created = UserProfile.objects.get_or_create(
    user=user,
    defaults={
        'phone': '9876543210',
        'pincode': '600001'
    }
)
print(f"✅ Profile: {profile.unique_id} - Phone: {profile.phone}")

# Test 3: Create Admin Hierarchy
print("\n3️⃣ Creating Admin Hierarchy...")
group, _ = AdminGroup.objects.get_or_create(name='Vehicles')
print(f"✅ Group: {group.name}")

# Test 4: Create Vehicle
print("\n4️⃣ Creating Vehicle...")
vehicle, created = Vehicle.objects.get_or_create(
    brand_name='Toyota',
    model_name='Camry',
    year=2024,
    defaults={
        'category_name': 'Car',
        'state': 'Tamil Nadu',
        'price': 1500,
        'pricing_type': 'per-day',
        'per_day_price': 1500,
        'per_hour_price': 100,
        'seller_phone': '9876543210',
        'pincode': '600001',
        'approval_status': 'approved',
        'added_by': 'seller',
        'available': True
    }
)
print(f"✅ Vehicle: {vehicle.brand_name} {vehicle.model_name} - ₹{vehicle.price}")

# Test 5: Query Data
print("\n5️⃣ Querying Database...")
total_users = User.objects.count()
total_vehicles = Vehicle.objects.count()
available_vehicles = Vehicle.objects.filter(available=True).count()

print(f"✅ Total Users: {total_users}")
print(f"✅ Total Vehicles: {total_vehicles}")
print(f"✅ Available Vehicles: {available_vehicles}")

# Test 6: Display Recent Vehicles
print("\n6️⃣ Recent Vehicles:")
recent_vehicles = Vehicle.objects.all().order_by('-id')[:5]
for v in recent_vehicles:
    print(f"   • {v.brand_name} {v.model_name} ({v.year}) - ₹{v.price}/{v.pricing_type}")

print("\n" + "=" * 60)
print("✅ Database Test Complete!")
print("=" * 60)
