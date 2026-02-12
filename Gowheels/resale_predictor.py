"""
Resale Value Prediction Module
AI-based vehicle depreciation and resale value calculator
"""

from datetime import datetime
from decimal import Decimal


class ResaleValuePredictor:
    """
    Predicts vehicle resale value based on multiple factors
    Uses industry-standard depreciation models
    """
    
    # Depreciation rates by vehicle category (per year)
    DEPRECIATION_RATES = {
        'car': 0.15,      # 15% per year
        'bike': 0.20,     # 20% per year
        'truck': 0.12,    # 12% per year
        'boat': 0.10,     # 10% per year
        'aerial': 0.08,   # 8% per year
        'electric': 0.18  # 18% per year (higher due to battery)
    }
    
    # Brand value retention (multiplier)
    BRAND_FACTORS = {
        'premium': 0.85,   # Premium brands retain 85% value
        'standard': 0.75,  # Standard brands retain 75% value
        'budget': 0.65     # Budget brands retain 65% value
    }
    
    # Condition impact on value
    CONDITION_FACTORS = {
        'excellent': 1.0,
        'good': 0.90,
        'fair': 0.75,
        'poor': 0.50
    }
    
    @staticmethod
    def calculate_depreciation(
        brand: str,
        model: str,
        year: int,
        original_price: float,
        current_price: float,
        kilometers_driven: int,
        fuel_type: str,
        transmission: str,
        city: str,
        owner_count: int,
        accident_history: int,
        vehicle_category: str = 'car',
        prediction_years: int = 2,
        condition: str = 'good'
    ) -> dict:
        """
        Calculate predicted resale value after specified years
        
        Args:
            brand: Vehicle brand name
            model: Vehicle model name
            year: Manufacturing year
            original_price: Original purchase price
            current_price: Current market price
            kilometers_driven: Total kilometers driven
            fuel_type: petrol/diesel/electric/cng
            transmission: manual/automatic
            city: City location
            owner_count: Number of previous owners
            accident_history: Number of accidents
            vehicle_category: Type of vehicle (car, bike, etc.)
            prediction_years: Years for prediction (default 2)
            condition: Vehicle condition
            
        Returns:
            dict with resale predictions and breakdown
        """
        
        # Calculate vehicle age
        from datetime import datetime
        current_year = datetime.now().year
        vehicle_age = current_year - year
        
        # Determine brand tier from brand name
        premium_brands = ['bmw', 'mercedes', 'audi', 'lexus', 'porsche', 'jaguar', 'land rover']
        budget_brands = ['maruti', 'tata', 'datsun', 'renault']
        
        if brand.lower() in premium_brands:
            brand_tier = 'premium'
        elif brand.lower() in budget_brands:
            brand_tier = 'budget'
        else:
            brand_tier = 'standard'
        
        # Get base depreciation rate
        base_rate = ResaleValuePredictor.DEPRECIATION_RATES.get(
            vehicle_category.lower(), 0.15
        )
        
        # Calculate base depreciation
        depreciated_value = current_price
        for yr in range(prediction_years):
            depreciated_value *= (1 - base_rate)
        
        # Apply brand factor
        brand_multiplier = ResaleValuePredictor.BRAND_FACTORS.get(
            brand_tier.lower(), 0.75
        )
        depreciated_value *= brand_multiplier
        
        # Apply condition factor
        condition_multiplier = ResaleValuePredictor.CONDITION_FACTORS.get(
            condition.lower(), 0.90
        )
        depreciated_value *= condition_multiplier
        
        # Kilometers impact (reduce 0.5% per 10,000 km)
        if kilometers_driven > 0:
            km_factor = max(0.6, 1 - (kilometers_driven / 10000) * 0.005)
            depreciated_value *= km_factor
        else:
            km_factor = 1.0
        
        # Accident impact (reduce 5% per accident)
        if accident_history > 0:
            accident_factor = max(0.6, 1 - (accident_history * 0.05))
            depreciated_value *= accident_factor
        else:
            accident_factor = 1.0
        
        # Owner count impact (reduce 3% per owner after first)
        if owner_count > 1:
            owner_factor = max(0.85, 1 - ((owner_count - 1) * 0.03))
            depreciated_value *= owner_factor
        else:
            owner_factor = 1.0
        
        # Fuel type impact
        fuel_factors = {
            'electric': 0.85,  # Higher depreciation
            'diesel': 0.95,
            'petrol': 1.0,
            'cng': 0.92
        }
        fuel_factor = fuel_factors.get(fuel_type.lower(), 1.0)
        depreciated_value *= fuel_factor
        
        # Transmission impact (automatic retains better)
        transmission_factor = 1.05 if transmission.lower() == 'automatic' else 1.0
        depreciated_value *= transmission_factor
        
        # Age impact (additional depreciation for older vehicles)
        if vehicle_age > 5:
            age_factor = max(0.7, 1 - ((vehicle_age - 5) * 0.02))
            depreciated_value *= age_factor
        else:
            age_factor = 1.0
        
        # Calculate depreciation amount
        total_depreciation = current_price - depreciated_value
        depreciation_percentage = (total_depreciation / current_price) * 100
        
        return {
            'vehicle_info': {
                'brand': brand,
                'model': model,
                'year': year,
                'age': vehicle_age,
                'original_price': round(original_price, 2),
                'fuel_type': fuel_type,
                'transmission': transmission,
                'city': city
            },
            'current_price': round(current_price, 2),
            'predicted_resale_value': round(depreciated_value, 2),
            'total_depreciation': round(total_depreciation, 2),
            'depreciation_percentage': round(depreciation_percentage, 2),
            'prediction_years': prediction_years,
            'factors': {
                'base_depreciation_rate': f"{base_rate * 100}%",
                'brand_tier': brand_tier,
                'brand_retention': f"{brand_multiplier * 100}%",
                'condition_impact': f"{condition_multiplier * 100}%",
                'kilometers_impact': f"{km_factor * 100:.1f}%",
                'accident_impact': f"{accident_factor * 100:.1f}%",
                'owner_count_impact': f"{owner_factor * 100:.1f}%",
                'fuel_type_impact': f"{fuel_factor * 100:.1f}%",
                'transmission_impact': f"{transmission_factor * 100:.1f}%",
                'age_impact': f"{age_factor * 100:.1f}%"
            },
            'confidence_score': ResaleValuePredictor._calculate_confidence(
                vehicle_category, brand_tier, condition, kilometers_driven, accident_history, owner_count, vehicle_age
            )
        }
    
    @staticmethod
    def _calculate_confidence(category, brand, condition, km_driven, accidents, owners, age):
        """Calculate prediction confidence score (0-100)"""
        confidence = 90  # Base confidence
        
        # Reduce confidence for high kilometers
        if km_driven > 150000:
            confidence -= 15
        elif km_driven > 100000:
            confidence -= 10
        elif km_driven > 50000:
            confidence -= 5
        
        # Reduce confidence for accidents
        if accidents > 3:
            confidence -= 20
        elif accidents > 1:
            confidence -= 10
        elif accidents > 0:
            confidence -= 5
        
        # Reduce confidence for multiple owners
        if owners > 3:
            confidence -= 10
        elif owners > 2:
            confidence -= 5
        
        # Reduce confidence for poor condition
        if condition == 'poor':
            confidence -= 15
        elif condition == 'fair':
            confidence -= 5
        
        # Reduce confidence for very old vehicles
        if age > 15:
            confidence -= 15
        elif age > 10:
            confidence -= 10
        
        return max(50, min(95, confidence))
    
    @staticmethod
    def predict_yearly_values(
        current_price: float,
        vehicle_category: str,
        years_range: int = 5,
        **kwargs
    ) -> list:
        """
        Predict resale values for multiple years
        
        Returns:
            List of predictions for each year
        """
        predictions = []
        
        for year in range(1, years_range + 1):
            prediction = ResaleValuePredictor.calculate_depreciation(
                current_price=current_price,
                vehicle_category=vehicle_category,
                years=year,
                **kwargs
            )
            predictions.append({
                'year': year,
                'value': prediction['predicted_resale_value'],
                'depreciation': prediction['total_depreciation']
            })
        
        return predictions


# Example usage
if __name__ == "__main__":
    # Example 1: Car resale prediction with all fields
    car_prediction = ResaleValuePredictor.calculate_depreciation(
        brand='Honda',
        model='City',
        year=2020,
        original_price=1200000,
        current_price=900000,
        kilometers_driven=35000,
        fuel_type='petrol',
        transmission='automatic',
        city='Mumbai',
        owner_count=1,
        accident_history=0,
        vehicle_category='car',
        prediction_years=2,
        condition='good'
    )
    
    print("Car Resale Prediction:")
    print(f"Vehicle: {car_prediction['vehicle_info']['brand']} {car_prediction['vehicle_info']['model']} ({car_prediction['vehicle_info']['year']})")
    print(f"Age: {car_prediction['vehicle_info']['age']} years")
    print(f"Original Price: ₹{car_prediction['vehicle_info']['original_price']:,.0f}")
    print(f"Current Price: ₹{car_prediction['current_price']:,.0f}")
    print(f"Predicted Value (2 years): ₹{car_prediction['predicted_resale_value']:,.0f}")
    print(f"Depreciation: ₹{car_prediction['total_depreciation']:,.0f} ({car_prediction['depreciation_percentage']}%)")
    print(f"Confidence: {car_prediction['confidence_score']}%")
    print(f"Brand Tier: {car_prediction['factors']['brand_tier']}")
    print()
    
    # Example 2: Bike resale prediction
    bike_prediction = ResaleValuePredictor.calculate_depreciation(
        brand='Royal Enfield',
        model='Classic 350',
        year=2021,
        original_price=180000,
        current_price=150000,
        kilometers_driven=12000,
        fuel_type='petrol',
        transmission='manual',
        city='Bangalore',
        owner_count=1,
        accident_history=0,
        vehicle_category='bike',
        prediction_years=2,
        condition='excellent'
    )
    
    print("Bike Resale Prediction:")
    print(f"Vehicle: {bike_prediction['vehicle_info']['brand']} {bike_prediction['vehicle_info']['model']}")
    print(f"Current Price: ₹{bike_prediction['current_price']:,.0f}")
    print(f"Predicted Value (2 years): ₹{bike_prediction['predicted_resale_value']:,.0f}")
    print(f"Depreciation: ₹{bike_prediction['total_depreciation']:,.0f} ({bike_prediction['depreciation_percentage']}%)")
    print(f"Confidence: {bike_prediction['confidence_score']}%")
