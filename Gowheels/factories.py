"""
Factory patterns for creating objects
Implements Factory and Abstract Factory patterns
"""

from abc import ABC, abstractmethod


class NotificationFactory:
    """Factory for creating notification senders"""
    
    @staticmethod
    def create_notification_sender(provider: str):
        """Create notification sender based on provider"""
        if provider == '2factor':
            return TwoFactorSMSSender()
        elif provider == 'fast2sms':
            return Fast2SMSSender()
        elif provider == 'msg91':
            return MSG91Sender()
        else:
            raise ValueError(f"Unknown provider: {provider}")


class SMSSender(ABC):
    """Abstract SMS sender"""
    
    @abstractmethod
    def send(self, phone: str, message: str) -> bool:
        pass


class TwoFactorSMSSender(SMSSender):
    """2Factor SMS implementation"""
    
    def send(self, phone: str, message: str) -> bool:
        # Implement 2Factor API call
        print(f"Sending via 2Factor to {phone}: {message}")
        return True


class Fast2SMSSender(SMSSender):
    """Fast2SMS implementation"""
    
    def send(self, phone: str, message: str) -> bool:
        # Implement Fast2SMS API call
        print(f"Sending via Fast2SMS to {phone}: {message}")
        return True


class MSG91Sender(SMSSender):
    """MSG91 implementation"""
    
    def send(self, phone: str, message: str) -> bool:
        # Implement MSG91 API call
        print(f"Sending via MSG91 to {phone}: {message}")
        return True


class VehicleFactory:
    """Factory for creating different vehicle types"""
    
    @staticmethod
    def create_vehicle(vehicle_type: str, **kwargs):
        """Create vehicle based on type"""
        if vehicle_type == 'car':
            return Car(**kwargs)
        elif vehicle_type == 'bike':
            return Bike(**kwargs)
        elif vehicle_type == 'truck':
            return Truck(**kwargs)
        elif vehicle_type == 'boat':
            return Boat(**kwargs)
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")


class Vehicle(ABC):
    """Abstract vehicle class"""
    
    def __init__(self, brand, model, price):
        self.brand = brand
        self.model = model
        self.price = price
    
    @abstractmethod
    def get_category(self) -> str:
        pass
    
    @abstractmethod
    def calculate_rental(self, days: int) -> float:
        pass


class Car(Vehicle):
    """Car implementation"""
    
    def get_category(self) -> str:
        return "Car"
    
    def calculate_rental(self, days: int) -> float:
        # Cars have standard pricing
        return self.price * days


class Bike(Vehicle):
    """Bike implementation"""
    
    def get_category(self) -> str:
        return "Bike"
    
    def calculate_rental(self, days: int) -> float:
        # Bikes have discounted pricing for longer rentals
        if days > 7:
            return self.price * days * 0.9
        return self.price * days


class Truck(Vehicle):
    """Truck implementation"""
    
    def get_category(self) -> str:
        return "Truck"
    
    def calculate_rental(self, days: int) -> float:
        # Trucks have premium pricing
        return self.price * days * 1.2


class Boat(Vehicle):
    """Boat implementation"""
    
    def get_category(self) -> str:
        return "Boat"
    
    def calculate_rental(self, days: int) -> float:
        # Boats have seasonal pricing
        return self.price * days * 1.5


class PaymentFactory:
    """Factory for payment processors"""
    
    @staticmethod
    def create_payment_processor(method: str):
        """Create payment processor"""
        if method == 'upi':
            return UPIPayment()
        elif method == 'card':
            return CardPayment()
        elif method == 'wallet':
            return WalletPayment()
        else:
            raise ValueError(f"Unknown payment method: {method}")


class PaymentProcessor(ABC):
    """Abstract payment processor"""
    
    @abstractmethod
    def process_payment(self, amount: float, details: dict) -> bool:
        pass


class UPIPayment(PaymentProcessor):
    """UPI payment implementation"""
    
    def process_payment(self, amount: float, details: dict) -> bool:
        print(f"Processing UPI payment of ₹{amount}")
        return True


class CardPayment(PaymentProcessor):
    """Card payment implementation"""
    
    def process_payment(self, amount: float, details: dict) -> bool:
        print(f"Processing card payment of ₹{amount}")
        return True


class WalletPayment(PaymentProcessor):
    """Wallet payment implementation"""
    
    def process_payment(self, amount: float, details: dict) -> bool:
        print(f"Processing wallet payment of ₹{amount}")
        return True
