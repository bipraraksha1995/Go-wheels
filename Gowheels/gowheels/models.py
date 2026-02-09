from django.db import models
from django.contrib.auth.models import User
import math
from datetime import datetime, timedelta

class PromotionSettings(models.Model):
    promote_price_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=50)
    sponsor_price_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Promote: ₹{self.promote_price_per_day}/day, Sponsor: ₹{self.sponsor_price_per_day}/day"

class VehiclePromotion(models.Model):
    PROMOTION_TYPES = [
        ('promote', 'Promote'),
        ('sponsor', 'Sponsor'),
    ]
    
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='promotions')
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
    days = models.IntegerField()
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.days)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.vehicle} - {self.promotion_type} for {self.days} days"

class Pincode(models.Model):
    code = models.CharField(max_length=6, unique=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.city}, {self.state}"
    
    @staticmethod
    def haversine_distance(lat1, lng1, lat2, lng2):
        R = 6371
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    @classmethod
    def get_nearby_pincodes(cls, pincode, radius_km=10):
        try:
            base = cls.objects.get(code=pincode)
            nearby_pincodes = []
            for pc in cls.objects.all():
                distance = cls.haversine_distance(
                    base.latitude, base.longitude,
                    pc.latitude, pc.longitude
                )
                if distance <= radius_km:
                    nearby_pincodes.append(pc.code)
            return nearby_pincodes
        except cls.DoesNotExist:
            return [pincode]

class AdminGroup(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class AdminCategory(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/')
    group = models.ForeignKey(AdminGroup, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.group.name} - {self.name}"

class AdminBrand(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='brands/')
    category = models.ForeignKey(AdminCategory, on_delete=models.CASCADE, related_name='brands')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class AdminModel(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='models/')
    brand = models.ForeignKey(AdminBrand, on_delete=models.CASCADE, related_name='models')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.brand.name} - {self.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=20, unique=True, blank=True)
    phone = models.CharField(max_length=15, unique=True)
    pincode = models.CharField(max_length=10)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True)
    blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.unique_id:
            import random
            import string
            # Generate 4 letters + 4 numbers
            letters = ''.join(random.choices(string.ascii_uppercase, k=4))
            numbers = ''.join(random.choices(string.digits, k=4))
            self.unique_id = f"{letters}{numbers}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.unique_id}"

class Category(models.Model):
    TYPE_CHOICES = [
        ('group1', 'Group 1'),
        ('group2', 'Group 2'),
        ('group3', 'Group 3'),
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    image = models.ImageField(upload_to='categories/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.type})"

class VehicleClick(models.Model):
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='clicks')
    buyer_phone = models.CharField(max_length=15)
    buyer_name = models.CharField(max_length=100, blank=True)
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.buyer_name} clicked {self.vehicle}"

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('suv', 'SUV'),
    ]
    
    PRICING_TYPES = [
        ('per-hour', 'Per Hour'),
        ('per-day', 'Per Day'),
    ]
    
    UNIT_TYPES = [
        ('unit_price', 'Unit Price'),
        ('square_feet', 'Square Feet'),
        ('cubic_feet', 'Cubic Feet'),
    ]
    
    APPROVAL_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    category_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    year = models.IntegerField()
    state = models.CharField(max_length=50)
    hourly_start_range = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    hourly_end_range = models.DecimalField(max_digits=8, decimal_places=2, default=3000)
    daily_start_range = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    daily_end_range = models.DecimalField(max_digits=8, decimal_places=2, default=3000)
    per_day_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    per_hour_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    min_price = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    max_price = models.DecimalField(max_digits=8, decimal_places=2, default=3000)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES, default='unit_price')
    category_image = models.ImageField(upload_to='vehicles/category/', blank=True)
    brand_image = models.ImageField(upload_to='vehicles/brand/', blank=True)
    model_image = models.ImageField(upload_to='vehicles/model/', blank=True)
    seller_phone = models.CharField(max_length=15, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    village = models.CharField(max_length=100, blank=True)
    owner_name = models.CharField(max_length=100, blank=True)
    available = models.BooleanField(default=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    added_by = models.CharField(max_length=50, default='super_admin')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.brand_name} {self.model_name} ({self.year})"

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicles/seller/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.vehicle}"

class BrandImage(models.Model):
    CATEGORY_CHOICES = [
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('truck', 'Truck'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    category_ref = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='brands', null=True, blank=True)
    name = models.CharField(max_length=100, default='Brand Name')
    image = models.ImageField(upload_to='brands/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class ModelImage(models.Model):
    CATEGORY_CHOICES = [
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('truck', 'Truck'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    brand = models.ForeignKey(BrandImage, on_delete=models.CASCADE, related_name='models', null=True, blank=True)
    name = models.CharField(max_length=100, default='Model Name')
    image = models.ImageField(upload_to='models/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.vehicle.name}"