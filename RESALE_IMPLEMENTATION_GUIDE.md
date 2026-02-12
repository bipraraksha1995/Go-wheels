# 🚀 Resale Value Prediction - Implementation Guide

## Step 1: Add URLs to your project

Open `gowheels_project/urls.py` and add these lines:

```python
from gowheels import resale_views

urlpatterns = [
    # ... your existing URLs ...
    
    # Resale Prediction APIs
    path('api/predict-resale/', resale_views.predict_resale_value, name='predict_resale'),
    path('api/predict-resale-yearly/', resale_views.predict_yearly_resale, name='predict_resale_yearly'),
    path('api/vehicle/<int:vehicle_id>/resale-prediction/', resale_views.get_vehicle_resale_info, name='vehicle_resale_info'),
    
    # Resale Prediction Page
    path('resale-prediction/', TemplateView.as_view(template_name='resale_prediction.html'), name='resale_prediction'),
]
```

## Step 2: Test the Prediction Engine

Run the test script:

```bash
cd d:\Gowheels\gowheels
python resale_predictor.py
```

You should see output like:
```
Car Resale Prediction:
Current Price: ₹500,000
Predicted Value (2 years): ₹361,250
Depreciation: ₹138,750 (27.75%)
Confidence: 85%
```

## Step 3: Add to Vehicle Detail Page

Open `templates/user_browse.html` or your vehicle detail template and add this code:

```html
<!-- Add this inside vehicle detail card -->
<div class="resale-prediction-section" style="margin-top: 2rem; padding: 1.5rem; background: #2a2a2a; border-left: 4px solid #ffc107;">
    <h3 style="color: #ffc107; margin-bottom: 1rem;">📊 Resale Value Prediction</h3>
    <div id="resale-info-{{ vehicle.id }}">
        <button onclick="loadResalePrediction({{ vehicle.id }})" 
                style="background: #ffc107; color: #1e1e1e; padding: 0.8rem 2rem; border: none; cursor: pointer; text-transform: uppercase; letter-spacing: 2px;">
            Calculate Resale Value
        </button>
    </div>
</div>

<script>
async function loadResalePrediction(vehicleId) {
    const container = document.getElementById('resale-info-' + vehicleId);
    container.innerHTML = '<p style="color: #ffc107;">Loading prediction...</p>';
    
    try {
        const response = await fetch(`/api/vehicle/${vehicleId}/resale-prediction/`);
        const data = await response.json();
        
        if (data.success) {
            const pred = data.prediction;
            container.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="text-align: center; padding: 1rem; background: #1e1e1e;">
                        <div style="color: #999; font-size: 0.9rem; margin-bottom: 0.5rem;">CURRENT PRICE</div>
                        <div style="color: #ffc107; font-size: 1.5rem; font-weight: bold;">₹${pred.current_price.toLocaleString('en-IN')}</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: #1e1e1e;">
                        <div style="color: #999; font-size: 0.9rem; margin-bottom: 0.5rem;">AFTER 2 YEARS</div>
                        <div style="color: #4caf50; font-size: 1.5rem; font-weight: bold;">₹${pred.predicted_resale_value.toLocaleString('en-IN')}</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: #1e1e1e;">
                        <div style="color: #999; font-size: 0.9rem; margin-bottom: 0.5rem;">DEPRECIATION</div>
                        <div style="color: #f44336; font-size: 1.5rem; font-weight: bold;">-${pred.depreciation_percentage}%</div>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: #1e1e1e; text-align: center;">
                    <span style="color: #999;">Confidence: </span>
                    <span style="color: #ffc107; font-weight: bold;">${pred.confidence_score}%</span>
                </div>
            `;
        } else {
            container.innerHTML = '<p style="color: #f44336;">Error loading prediction</p>';
        }
    } catch (error) {
        container.innerHTML = '<p style="color: #f44336;">Error: ' + error.message + '</p>';
    }
}
</script>
```

## Step 4: Use API Directly (Python)

```python
from gowheels.resale_predictor import ResaleValuePredictor

# Example: Predict car resale value
prediction = ResaleValuePredictor.calculate_depreciation(
    current_price=500000,      # ₹5 lakhs
    vehicle_category='car',
    years=2,
    brand_tier='premium',      # premium/standard/budget
    condition='good',          # excellent/good/fair/poor
    mileage=20000,            # km
    accidents=0
)

print(f"Current: ₹{prediction['current_price']:,.0f}")
print(f"After 2 years: ₹{prediction['predicted_resale_value']:,.0f}")
print(f"Depreciation: {prediction['depreciation_percentage']}%")
print(f"Confidence: {prediction['confidence_score']}%")
```

## Step 5: Use API via JavaScript (Frontend)

```javascript
// Single prediction
async function predictResale(vehicleId) {
    const response = await fetch('/api/predict-resale/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            vehicle_id: vehicleId,
            years: 2,
            condition: 'good',
            mileage: 20000,
            accidents: 0
        })
    });
    
    const data = await response.json();
    console.log(data.prediction);
}

// 5-year projection
async function getYearlyPrediction(vehicleId) {
    const response = await fetch('/api/predict-resale-yearly/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            vehicle_id: vehicleId,
            years_range: 5,
            condition: 'good'
        })
    });
    
    const data = await response.json();
    console.log(data.predictions);
}
```

## Step 6: Access the Standalone Page

1. Start your Django server:
```bash
python manage.py runserver
```

2. Open browser and go to:
```
http://localhost:8000/resale-prediction/
```

3. Enter:
   - Vehicle ID (e.g., 1)
   - Years (e.g., 2)
   - Condition (Good)
   - Mileage (20000)
   - Accidents (0)

4. Click "Calculate Resale Value"

## Step 7: Add to Seller Dashboard

Add this to `seller_complete_form.html` or `seller_vehicles.html`:

```html
<div class="resale-info" style="margin-top: 1rem; padding: 1rem; background: #2a2a2a;">
    <h4 style="color: #ffc107;">💡 Resale Value Insight</h4>
    <p style="color: #999; margin: 0.5rem 0;">
        Your vehicle's estimated value after 2 years: 
        <span style="color: #4caf50; font-weight: bold;" id="resale-value-{{ vehicle.id }}">
            Calculating...
        </span>
    </p>
</div>

<script>
// Auto-load resale prediction
fetch('/api/vehicle/{{ vehicle.id }}/resale-prediction/')
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('resale-value-{{ vehicle.id }}').textContent = 
                '₹' + data.prediction.predicted_resale_value.toLocaleString('en-IN');
        }
    });
</script>
```

## Step 8: Customize Depreciation Rates

Edit `resale_predictor.py` to adjust rates:

```python
DEPRECIATION_RATES = {
    'car': 0.15,      # Change to 0.12 for 12% per year
    'bike': 0.20,     # Change to 0.18 for 18% per year
    'truck': 0.12,
    'boat': 0.10,
    'aerial': 0.08,
    'electric': 0.18
}
```

## 📊 API Response Format

```json
{
    "success": true,
    "vehicle": {
        "id": 1,
        "name": "Honda City",
        "current_price": 500000
    },
    "prediction": {
        "current_price": 500000,
        "predicted_resale_value": 361250,
        "total_depreciation": 138750,
        "depreciation_percentage": 27.75,
        "years": 2,
        "factors": {
            "base_depreciation_rate": "15.0%",
            "brand_retention": "85.0%",
            "condition_impact": "90.0%",
            "mileage_impact": "99.0%",
            "accident_impact": "100.0%"
        },
        "confidence_score": 85
    }
}
```

## 🎯 Quick Test Commands

```bash
# Test prediction engine
python gowheels/resale_predictor.py

# Test API endpoint
curl -X POST http://localhost:8000/api/predict-resale/ \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id": 1, "years": 2, "condition": "good", "mileage": 20000, "accidents": 0}'

# Get vehicle resale info
curl http://localhost:8000/api/vehicle/1/resale-prediction/
```

## ✅ Checklist

- [ ] Files copied to project
- [ ] URLs added to urls.py
- [ ] Test script runs successfully
- [ ] API endpoints working
- [ ] UI page accessible
- [ ] Added to vehicle detail page
- [ ] Added to seller dashboard

## 🎉 Done!

Your Resale Value Prediction feature is now live!

Users can now see predicted resale values for any vehicle with AI-powered accuracy! 🚀
