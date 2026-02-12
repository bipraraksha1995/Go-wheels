"""
Resale Value Prediction Views
API endpoints for vehicle resale value predictions
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .resale_predictor import ResaleValuePredictor
from .models import Vehicle


@csrf_exempt
@require_http_methods(["POST"])
def predict_resale_value(request):
    """
    API endpoint to predict vehicle resale value
    
    POST /api/predict-resale/
    {
        "vehicle_id": 123,
        "years": 2,
        "condition": "good",
        "mileage": 20000,
        "accidents": 0
    }
    """
    try:
        data = json.loads(request.body)
        vehicle_id = data.get('vehicle_id')
        years = data.get('years', 2)
        condition = data.get('condition', 'good')
        mileage = data.get('mileage', 0)
        accidents = data.get('accidents', 0)
        
        # Get vehicle details
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Vehicle not found'
            }, status=404)
        
        # Determine brand tier based on price
        if vehicle.price > 1000000:
            brand_tier = 'premium'
        elif vehicle.price > 300000:
            brand_tier = 'standard'
        else:
            brand_tier = 'budget'
        
        # Calculate prediction
        prediction = ResaleValuePredictor.calculate_depreciation(
            current_price=float(vehicle.price),
            vehicle_category=vehicle.category.name.lower() if vehicle.category else 'car',
            years=years,
            brand_tier=brand_tier,
            condition=condition,
            mileage=mileage,
            accidents=accidents
        )
        
        return JsonResponse({
            'success': True,
            'vehicle': {
                'id': vehicle.id,
                'name': f"{vehicle.brand.name} {vehicle.model.name}" if vehicle.brand and vehicle.model else vehicle.title,
                'current_price': vehicle.price
            },
            'prediction': prediction
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def predict_yearly_resale(request):
    """
    API endpoint to get multi-year resale predictions
    
    POST /api/predict-resale-yearly/
    {
        "vehicle_id": 123,
        "years_range": 5,
        "condition": "good"
    }
    """
    try:
        data = json.loads(request.body)
        vehicle_id = data.get('vehicle_id')
        years_range = data.get('years_range', 5)
        condition = data.get('condition', 'good')
        
        # Get vehicle details
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Vehicle not found'
            }, status=404)
        
        # Determine brand tier
        if vehicle.price > 1000000:
            brand_tier = 'premium'
        elif vehicle.price > 300000:
            brand_tier = 'standard'
        else:
            brand_tier = 'budget'
        
        # Get yearly predictions
        predictions = ResaleValuePredictor.predict_yearly_values(
            current_price=float(vehicle.price),
            vehicle_category=vehicle.category.name.lower() if vehicle.category else 'car',
            years_range=years_range,
            brand_tier=brand_tier,
            condition=condition
        )
        
        return JsonResponse({
            'success': True,
            'vehicle': {
                'id': vehicle.id,
                'name': f"{vehicle.brand.name} {vehicle.model.name}" if vehicle.brand and vehicle.model else vehicle.title,
                'current_price': vehicle.price
            },
            'predictions': predictions
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_vehicle_resale_info(request, vehicle_id):
    """
    Get resale prediction for a specific vehicle (GET request)
    
    GET /api/vehicle/{vehicle_id}/resale-prediction/
    """
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        # Determine brand tier
        if vehicle.price > 1000000:
            brand_tier = 'premium'
        elif vehicle.price > 300000:
            brand_tier = 'standard'
        else:
            brand_tier = 'budget'
        
        # Calculate 2-year prediction (default)
        prediction = ResaleValuePredictor.calculate_depreciation(
            current_price=float(vehicle.price),
            vehicle_category=vehicle.category.name.lower() if vehicle.category else 'car',
            years=2,
            brand_tier=brand_tier,
            condition='good'
        )
        
        return JsonResponse({
            'success': True,
            'vehicle': {
                'id': vehicle.id,
                'name': f"{vehicle.brand.name} {vehicle.model.name}" if vehicle.brand and vehicle.model else vehicle.title,
                'current_price': vehicle.price,
                'category': vehicle.category.name if vehicle.category else 'Unknown'
            },
            'prediction': prediction
        })
        
    except Vehicle.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Vehicle not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
