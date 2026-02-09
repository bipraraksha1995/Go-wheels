from django.contrib import admin
from .models import *

@admin.register(PincodeMapping)
class PincodeMappingAdmin(admin.ModelAdmin):
    list_display = ('main_pincode', 'nearby_pincode', 'created_at')
    list_filter = ('main_pincode', 'created_at')
    search_fields = ('main_pincode', 'nearby_pincode')
    ordering = ('main_pincode', 'nearby_pincode')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('phone', 'user', 'unique_id', 'pincode', 'blocked')
    list_filter = ('blocked',)
    search_fields = ('phone', 'user__first_name', 'unique_id', 'pincode')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'model_name', 'year', 'pincode', 'seller_phone', 'available', 'approval_status')
    list_filter = ('available', 'approval_status', 'added_by', 'category_name')
    search_fields = ('brand_name', 'model_name', 'seller_phone', 'pincode')

@admin.register(AdminGroup)
class AdminGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(AdminCategory)
class AdminCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'created_at')
    list_filter = ('group',)

@admin.register(AdminBrand)
class AdminBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category__group',)

@admin.register(AdminModel)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'created_at')
    list_filter = ('brand__category__group',)