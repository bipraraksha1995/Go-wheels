# Manual Cost Prediction Feature

## Overview
Sellers can now manually enter cost prediction values when listing vehicles for sale. If manual values are provided, they will be displayed to buyers. Otherwise, the system automatically calculates cost predictions.

## Changes Made

### 1. Database Changes (`models.py`)

Added three new optional fields to the Vehicle model:
- `manual_maintenance_cost` - Decimal field for 2-year maintenance cost
- `manual_fuel_cost` - Decimal field for 2-year fuel cost
- `manual_insurance_cost` - Decimal field for 2-year insurance cost

All fields are nullable and optional (null=True, blank=True).

### 2. Backend Changes (`views.py`)

#### Updated `seller_dashboard_form` function:
- Captures manual cost prediction values from the form
- Saves them to the vehicle record if provided
- Handles empty/invalid values gracefully

#### Updated `get_vehicles` function:
- Returns manual cost prediction values in the API response
- Includes fields: `manual_maintenance_cost`, `manual_fuel_cost`, `manual_insurance_cost`

### 3. Frontend Changes

#### Seller Dashboard (`seller_dashboard.html`)
**Already Present:**
- Cost prediction input fields in the "Sell" section
- Fields for Maintenance, Fuel Cost, and Insurance (all optional)
- Clean UI with blue background section

**Updated:**
- Form submission now sends manual cost values to backend
- Values are only sent if the listing type is "sell"

#### User Browse Page (`user_browse_categories.html`)

**Updated `calculateCostPrediction` function:**
- Now accepts vehicle object as parameter
- Checks if manual values are provided
- Uses manual values if available, otherwise calculates automatically
- Returns `isManual` flag to indicate data source

**Updated Display:**
- Shows "✏️ Seller Provided" badge when manual values are used
- Shows "🤖 Auto-Calculated" badge when values are calculated
- Badge appears next to "📊 2-Year Ownership Cost" title

## How It Works

### For Sellers:

1. **Select Listing Type:** Choose "💰 Sell"
2. **Enter Selling Price:** Required field
3. **Optional Cost Prediction:**
   - Enter Maintenance cost (2 years)
   - Enter Fuel cost (2 years)
   - Enter Insurance cost (2 years)
4. **Submit:** Values are saved with the vehicle

### For Buyers:

1. **View Vehicle:** Browse vehicles for sale
2. **See Cost Prediction:**
   - If seller provided values: Shows "✏️ Seller Provided"
   - If auto-calculated: Shows "🤖 Auto-Calculated"
3. **Make Decision:** Use cost information to evaluate purchase

## Auto-Calculation Formula

When manual values are NOT provided, the system calculates:

**Maintenance (2 years):**
- Base: 4% of vehicle price
- Age Factor: +5% per year of vehicle age
- Formula: `price × 0.04 × (1 + vehicleAge × 0.05)`

**Fuel Cost (2 years):**
- Assumes: 10,000 km/year, 15 km/l, ₹100/liter
- Formula: `(10,000 × 2 / 15) × 100 = ₹133,333`

**Insurance (2 years):**
- Rate: 2.5% of vehicle price per year
- Formula: `price × 0.025 × 2`

**Total Ownership Cost:**
- Sum of: Vehicle Price + Maintenance + Fuel + Insurance

## Benefits

✅ **Flexibility:** Sellers can provide accurate costs based on their knowledge
✅ **Transparency:** Buyers see if values are seller-provided or calculated
✅ **Fallback:** System automatically calculates if seller doesn't provide values
✅ **Optional:** Sellers are not forced to enter manual values
✅ **Trust:** Badge system builds buyer confidence

## Database Migration

Migration file created: `0009_vehicle_manual_fuel_cost_and_more.py`

Applied successfully with:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Testing Checklist

- [ ] Add vehicle for SELL without manual costs → Verify auto-calculation works
- [ ] Add vehicle for SELL with manual costs → Verify manual values are saved
- [ ] View vehicle with manual costs → Verify "✏️ Seller Provided" badge shows
- [ ] View vehicle with auto costs → Verify "🤖 Auto-Calculated" badge shows
- [ ] Add vehicle for RENT → Verify no cost prediction section appears
- [ ] Edit existing vehicle → Verify manual costs can be updated
- [ ] Check API response → Verify manual cost fields are included

## Future Enhancements

- Allow sellers to edit manual cost values after listing
- Add validation for reasonable cost ranges
- Show breakdown of how auto-calculation works
- Add more cost factors (registration, parking, etc.)
- Historical cost tracking and trends
