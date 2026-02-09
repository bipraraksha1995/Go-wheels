from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import random
import string
from .encryption import Cipher
from .crypto_utils import generate_secure_token

class OTP(models.Model):
    phone = models.CharField(max_length=15, db_index=True)
    otp_hash = models.CharField(max_length=64)  # SHA-256 hash
    expires_at = models.DateTimeField(db_index=True)
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} - Expires: {self.expires_at}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone', 'is_used']),
            models.Index(fields=['expires_at']),
        ]


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

import secrets
import string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=20, unique=True, blank=True)
    phone = models.CharField(max_length=15, unique=True)
    pincode = models.CharField(max_length=10)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True)
    blocked = models.BooleanField(default=False)
    api_key = models.CharField(max_length=255, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.unique_id:
            # Generate 4 letters + 4 numbers using secure random
            letters = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(4))
            numbers = ''.join(secrets.choice(string.digits) for _ in range(4))
            self.unique_id = f"{letters}{numbers}"
        
        # Generate API key if not present
        if not self.api_key:
            self.api_key = generate_secure_token(32)
        
        super().save(*args, **kwargs)
    
    def get_phone(self):
        """Get decrypted phone number"""
        try:
            cipher = Cipher()
            return cipher.decrypt(self.phone)
        except:
            return self.phone  # Fallback for unencrypted data
    
    def set_phone(self, phone_number):
        """Set encrypted phone number"""
        cipher = Cipher()
        self.phone = cipher.encrypt(phone_number)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.unique_id}"

class PincodeMapping(models.Model):
    main_pincode = models.CharField(max_length=10)
    nearby_pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('main_pincode', 'nearby_pincode')
    
    def __str__(self):
        return f"{self.main_pincode} → {self.nearby_pincode}"

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
    
    LISTING_TYPES = [
        ('rent', 'Rent'),
        ('sell', 'Sell'),
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
    min_price = models.DecimalField(max_digits=8, decimal_places=2, default=100)  # Keep for backward compatibility
    max_price = models.DecimalField(max_digits=8, decimal_places=2, default=3000)  # Keep for backward compatibility
    price = models.DecimalField(max_digits=8, decimal_places=2)  # Keep for backward compatibility
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
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPES, default='rent')
    promoted = models.BooleanField(default=False)
    sponsored = models.BooleanField(default=False)
    added_by = models.CharField(max_length=50, default='super_admin')
    # Manual cost prediction fields
    manual_maintenance_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    manual_fuel_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    manual_insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Don't encrypt - store as plain text
        super().save(*args, **kwargs)
    
    def get_seller_phone(self):
        """Get seller phone (handle both encrypted and plain text)"""
        if not self.seller_phone:
            return ''
        # If encrypted, try to decrypt, otherwise return placeholder
        if self.seller_phone.startswith('gAAAA') or '==' in self.seller_phone:
            try:
                cipher = Cipher()
                return cipher.decrypt(self.seller_phone)
            except:
                return 'Not Available'
        return self.seller_phone
    
    def get_owner_name(self):
        """Get owner name (handle both encrypted and plain text)"""
        if not self.owner_name:
            return ''
        # If encrypted, try to decrypt, otherwise return placeholder
        if self.owner_name.startswith('gAAAA') or '==' in self.owner_name:
            try:
                cipher = Cipher()
                return cipher.decrypt(self.owner_name)
            except:
                return 'Owner'
        return self.owner_name
    
    def __str__(self):
        return f"{self.brand_name} {self.model_name} ({self.year})"

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicles/seller/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.vehicle}"

class VehicleVideo(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='vehicles/seller/videos/')
    duration = models.FloatField(default=0)  # Duration in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Video for {self.vehicle} ({self.duration}s)"

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
        return f"{self.user.username} - {self.vehicle.brand_name} {self.vehicle.model_name}"

class Chat(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='chats')
    buyer_phone = models.CharField(max_length=15)
    seller_phone = models.CharField(max_length=15)
    last_message = models.TextField(blank=True)
    last_message_time = models.DateTimeField(auto_now=True)
    unread_buyer = models.IntegerField(default=0)
    unread_seller = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('vehicle', 'buyer_phone')
        ordering = ['-last_message_time']
    
    def __str__(self):
        return f"Chat: {self.buyer_phone} <-> {self.seller_phone}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender_phone = models.CharField(max_length=15)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender_phone}: {self.message[:30]}"

class Referral(models.Model):
    referrer_phone = models.CharField(max_length=15)
    referral_code = models.CharField(max_length=10, unique=True)
    referred_phone = models.CharField(max_length=15, blank=True)
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.referrer_phone} - {self.referral_code}"

class Wishlist(models.Model):
    user_phone = models.CharField(max_length=15)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user_phone', 'vehicle')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user_phone} - {self.vehicle}"