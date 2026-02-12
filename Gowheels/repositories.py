"""
Repository pattern for data access
Separates data access logic from business logic
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from django.db.models import QuerySet, Q


class BaseRepository(ABC):
    """Abstract base repository"""
    
    def __init__(self, model):
        self.model = model
    
    @abstractmethod
    def find_all(self) -> QuerySet:
        pass
    
    @abstractmethod
    def find_by_id(self, id: int):
        pass
    
    @abstractmethod
    def save(self, entity):
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass


class VehicleRepository(BaseRepository):
    """Repository for Vehicle model"""
    
    def find_all(self) -> QuerySet:
        """Get all vehicles"""
        return self.model.objects.select_related(
            'category', 'brand', 'model'
        ).all()
    
    def find_by_id(self, id: int):
        """Find vehicle by ID"""
        try:
            return self.model.objects.select_related(
                'category', 'brand', 'model'
            ).get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def find_by_filters(self, filters: Dict) -> QuerySet:
        """Find vehicles by filters"""
        queryset = self.model.objects.all()
        
        if 'category' in filters:
            queryset = queryset.filter(category__name=filters['category'])
        
        if 'brand' in filters:
            queryset = queryset.filter(brand__name=filters['brand'])
        
        if 'min_price' in filters:
            queryset = queryset.filter(daily_price__gte=filters['min_price'])
        
        if 'max_price' in filters:
            queryset = queryset.filter(daily_price__lte=filters['max_price'])
        
        if 'available' in filters:
            queryset = queryset.filter(is_available=filters['available'])
        
        return queryset
    
    def find_available_by_location(self, pincode: str) -> QuerySet:
        """Find available vehicles by location"""
        return self.model.objects.filter(
            is_available=True,
            pincode=pincode
        )
    
    def save(self, entity):
        """Save vehicle"""
        entity.save()
        return entity
    
    def delete(self, id: int) -> bool:
        """Delete vehicle"""
        try:
            vehicle = self.find_by_id(id)
            if vehicle:
                vehicle.delete()
                return True
        except Exception:
            pass
        return False


class UserRepository(BaseRepository):
    """Repository for User model"""
    
    def find_all(self) -> QuerySet:
        return self.model.objects.all()
    
    def find_by_id(self, id: int):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def find_by_phone(self, phone: str):
        """Find user by phone"""
        try:
            return self.model.objects.get(phone=phone)
        except self.model.DoesNotExist:
            return None
    
    def find_by_email(self, email: str):
        """Find user by email"""
        try:
            return self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            return None
    
    def save(self, entity):
        entity.save()
        return entity
    
    def delete(self, id: int) -> bool:
        try:
            user = self.find_by_id(id)
            if user:
                user.delete()
                return True
        except Exception:
            pass
        return False
