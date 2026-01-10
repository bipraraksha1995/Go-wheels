#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('d:/Gowheels')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gowheels_project.settings')
django.setup()

from gowheels.models import *
from django.contrib.auth.models import User

def show_data():
    print("=" * 60)
    print("GOWHEELS DATABASE DATA")
    print("=" * 60)
    
    # Users
    print("\n1. USERS:")
    users = UserProfile.objects.all()
    for user in users:
        print(f"   ID: {user.id} | Phone: {user.phone} | Name: {user.user.first_name} | Unique ID: {user.unique_id}")
    
    # Vehicles
    print(f"\n2. VEHICLES ({Vehicle.objects.count()} total):")
    vehicles = Vehicle.objects.all()[:10]  # Show first 10
    for v in vehicles:
        print(f"   ID: {v.id} | {v.brand_name} {v.model_name} | Year: {v.year} | Price: ₹{v.price} | Seller: {v.seller_phone}")
    
    # Vehicle Images
    print(f"\n3. VEHICLE IMAGES ({VehicleImage.objects.count()} total):")
    images = VehicleImage.objects.all()[:5]
    for img in images:
        print(f"   Vehicle ID: {img.vehicle_id} | Image: {img.image}")
    
    # Brand Images
    print(f"\n4. BRAND IMAGES ({BrandImage.objects.count()} total):")
    brands = BrandImage.objects.all()[:5]
    for brand in brands:
        print(f"   ID: {brand.id} | Name: {brand.name} | Category: {brand.category}")
    
    # Model Images
    print(f"\n5. MODEL IMAGES ({ModelImage.objects.count()} total):")
    models = ModelImage.objects.all()[:5]
    for model in models:
        print(f"   ID: {model.id} | Name: {model.name} | Category: {model.category}")
    
    # Admin Groups
    print(f"\n6. ADMIN GROUPS ({AdminGroup.objects.count()} total):")
    groups = AdminGroup.objects.all()
    for group in groups:
        print(f"   ID: {group.id} | Name: {group.name}")
    
    # Categories
    print(f"\n7. CATEGORIES ({Category.objects.count()} total):")
    categories = Category.objects.all()
    for cat in categories:
        print(f"   ID: {cat.id} | Name: {cat.name} | Type: {cat.type}")
    
    print("\n" + "=" * 60)
    print("DATABASE SUMMARY:")
    print(f"Users: {UserProfile.objects.count()}")
    print(f"Vehicles: {Vehicle.objects.count()}")
    print(f"Vehicle Images: {VehicleImage.objects.count()}")
    print(f"Brand Images: {BrandImage.objects.count()}")
    print(f"Model Images: {ModelImage.objects.count()}")
    print(f"Admin Groups: {AdminGroup.objects.count()}")
    print(f"Categories: {Category.objects.count()}")
    print("=" * 60)

if __name__ == "__main__":
    show_data()