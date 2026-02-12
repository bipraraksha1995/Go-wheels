"""
Add these URLs to your main urls.py
"""

from django.urls import path
from gowheels import resale_views

urlpatterns = [
    # ... existing URLs ...
    
    # Resale Value Prediction APIs
    path('api/predict-resale/', resale_views.predict_resale_value, name='predict_resale'),
    path('api/predict-resale-yearly/', resale_views.predict_yearly_resale, name='predict_resale_yearly'),
    path('api/vehicle/<int:vehicle_id>/resale-prediction/', resale_views.get_vehicle_resale_info, name='vehicle_resale_info'),
]
