from django.contrib import admin
from .models import Vehicle, Booking

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'brand_name', 'category_name', 'price', 'pricing_type', 'year', 'state', 'available']
    list_filter = ['category_name', 'available', 'brand_name', 'pricing_type', 'year']
    search_fields = ['model_name', 'brand_name', 'category_name']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle', 'start_time', 'end_time', 'status', 'total_price']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'vehicle__model_name']