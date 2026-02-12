"""
Service layer for GoWheels
Implements business logic using OOP principles
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet


class BaseService(ABC):
    """Abstract base class for all services"""
    
    @abstractmethod
    def get_all(self) -> QuerySet:
        """Get all records"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: int):
        """Get record by ID"""
        pass
    
    @abstractmethod
    def create(self, data: dict):
        """Create new record"""
        pass
    
    @abstractmethod
    def update(self, id: int, data: dict):
        """Update existing record"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete record"""
        pass


class VehicleService(BaseService):
    """Service for vehicle-related operations"""
    
    def __init__(self, model):
        self.model = model
    
    def get_all(self) -> QuerySet:
        """Get all vehicles"""
        return self.model.objects.all()
    
    def get_by_id(self, id: int):
        """Get vehicle by ID"""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def get_by_category(self, category: str) -> QuerySet:
        """Get vehicles by category"""
        return self.model.objects.filter(category__name=category)
    
    def get_available(self) -> QuerySet:
        """Get available vehicles"""
        return self.model.objects.filter(is_available=True)
    
    def search(self, query: str) -> QuerySet:
        """Search vehicles"""
        return self.model.objects.filter(
            models.Q(brand__icontains=query) |
            models.Q(model__icontains=query) |
            models.Q(description__icontains=query)
        )
    
    def create(self, data: dict):
        """Create new vehicle"""
        return self.model.objects.create(**data)
    
    def update(self, id: int, data: dict):
        """Update vehicle"""
        vehicle = self.get_by_id(id)
        if vehicle:
            for key, value in data.items():
                setattr(vehicle, key, value)
            vehicle.save()
            return vehicle
        return None
    
    def delete(self, id: int) -> bool:
        """Delete vehicle"""
        vehicle = self.get_by_id(id)
        if vehicle:
            vehicle.delete()
            return True
        return False
    
    def calculate_rental_price(self, vehicle_id: int, days: int) -> float:
        """Calculate rental price"""
        vehicle = self.get_by_id(vehicle_id)
        if vehicle:
            return vehicle.daily_price * days
        return 0.0


class UserService(BaseService):
    """Service for user-related operations"""
    
    def __init__(self, model):
        self.model = model
    
    def get_all(self) -> QuerySet:
        return self.model.objects.all()
    
    def get_by_id(self, id: int):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def get_by_phone(self, phone: str):
        """Get user by phone number"""
        try:
            return self.model.objects.get(phone=phone)
        except self.model.DoesNotExist:
            return None
    
    def create(self, data: dict):
        return self.model.objects.create(**data)
    
    def update(self, id: int, data: dict):
        user = self.get_by_id(id)
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            user.save()
            return user
        return None
    
    def delete(self, id: int) -> bool:
        user = self.get_by_id(id)
        if user:
            user.delete()
            return True
        return False
    
    def block_user(self, id: int) -> bool:
        """Block user"""
        user = self.get_by_id(id)
        if user:
            user.is_blocked = True
            user.save()
            return True
        return False
    
    def unblock_user(self, id: int) -> bool:
        """Unblock user"""
        user = self.get_by_id(id)
        if user:
            user.is_blocked = False
            user.save()
            return True
        return False


class BookingService:
    """Service for booking operations"""
    
    def __init__(self, booking_model, vehicle_service: VehicleService):
        self.model = booking_model
        self.vehicle_service = vehicle_service
    
    def create_booking(self, user_id: int, vehicle_id: int, 
                       start_date, end_date) -> dict:
        """Create new booking"""
        vehicle = self.vehicle_service.get_by_id(vehicle_id)
        
        if not vehicle:
            return {"success": False, "error": "Vehicle not found"}
        
        if not vehicle.is_available:
            return {"success": False, "error": "Vehicle not available"}
        
        # Calculate days and price
        days = (end_date - start_date).days
        total_price = self.vehicle_service.calculate_rental_price(
            vehicle_id, days
        )
        
        # Create booking
        booking = self.model.objects.create(
            user_id=user_id,
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='pending'
        )
        
        # Mark vehicle as unavailable
        vehicle.is_available = False
        vehicle.save()
        
        return {
            "success": True,
            "booking": booking,
            "total_price": total_price
        }
    
    def cancel_booking(self, booking_id: int) -> bool:
        """Cancel booking"""
        try:
            booking = self.model.objects.get(id=booking_id)
            booking.status = 'cancelled'
            booking.save()
            
            # Make vehicle available again
            vehicle = booking.vehicle
            vehicle.is_available = True
            vehicle.save()
            
            return True
        except self.model.DoesNotExist:
            return False


class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self):
        self.sms_provider = None
        self.email_provider = None
    
    def send_sms(self, phone: str, message: str) -> bool:
        """Send SMS notification"""
        # Implement SMS sending logic
        pass
    
    def send_email(self, email: str, subject: str, message: str) -> bool:
        """Send email notification"""
        # Implement email sending logic
        pass
    
    def send_booking_confirmation(self, booking) -> bool:
        """Send booking confirmation"""
        message = f"Booking confirmed! Vehicle: {booking.vehicle.model}"
        return self.send_sms(booking.user.phone, message)
