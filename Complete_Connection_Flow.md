# GoWheels Complete Connection Flow

## 1. Project Architecture Flow

```
Frontend (HTML/JS) → Django URLs → Views → Models → Database
                                    ↓
                              Templates ← Context Data
```

## 2. Database Connection Flow

### Step 1: Environment Configuration
```
.env file → settings.py → Database Configuration
```

**File: `.env`**
```
DB_NAME=gowheels_new
DB_USER=root
DB_PASSWORD=sibi@100#
DB_HOST=localhost
DB_PORT=3306
```

**File: `settings.py`**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

### Step 2: ORM Connection
```
Python Models → Django ORM → MySQL Database
```

**File: `models.py`**
```python
class Vehicle(models.Model):
    brand_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
# Converts to SQL Table:
# CREATE TABLE gowheels_vehicle (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     brand_name VARCHAR(50),
#     price DECIMAL(8,2)
# );
```

## 3. API Request Flow

### Frontend → Backend API Flow
```
1. User Action (Click/Submit)
2. JavaScript AJAX/Fetch Call
3. HTTP Request to Django URL
4. URL Router matches pattern
5. View function executes
6. Database query via ORM
7. JSON response returned
8. Frontend updates UI
```

### Example: User Registration Flow
```
register.html → JavaScript → POST /register/ → register_view() → UserProfile.objects.create() → MySQL → JSON Response
```

**Frontend Code:**
```javascript
fetch('/register/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if(data.success) {
        alert('Registration successful');
    }
});
```

**Backend Code (views.py):**
```python
@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        
        # Database operation
        UserProfile.objects.create(
            user=user,
            phone=phone,
            pincode=pincode
        )
        
        return JsonResponse({'success': True})
```

## 4. URL Routing Flow

### Main Project URLs
```
gowheels_project/urls.py → gowheels/urls.py → views.py functions
```

**File: `gowheels_project/urls.py`**
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gowheels.urls')),
]
```

**File: `gowheels/urls.py`**
```python
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('api/vehicles/', api_views.api_vehicles, name='api_vehicles'),
]
```

## 5. Authentication Flow

### User Authentication Process
```
1. User enters phone number
2. Frontend calls /check-phone/ API
3. Backend checks UserProfile.objects.filter(phone=phone).exists()
4. If exists → Login flow, else → Registration flow
5. OTP verification (demo: 123456)
6. Session creation: request.session['user_id'] = user.id
7. Redirect to dashboard
```

### Session Management
```python
# Login
request.session['user_id'] = user.id
request.session['phone'] = phone

# Check Authentication
user_id = request.session.get('user_id')
if user_id:
    # User is logged in
```

## 6. File Upload Flow

### Image Upload Process
```
HTML Form → Multipart Data → Django View → File Storage → Database Path
```

**Frontend:**
```html
<input type="file" name="vehicle_images" multiple>
```

**Backend:**
```python
if 'vehicle_images' in request.FILES:
    for img in request.FILES.getlist('vehicle_images'):
        VehicleImage.objects.create(vehicle=vehicle, image=img)
```

**Storage Path:**
```
media/vehicles/seller/image.jpg
```

## 7. Complete API Connection Flow

### 32+ API Endpoints Connection
```
Frontend AJAX → URL Pattern → View Function → ORM Query → Database → JSON Response
```

**Example API Flows:**

1. **Phone Check API:**
```
JavaScript → POST /check-phone/ → check_phone() → UserProfile.objects.filter() → MySQL → {'exists': true/false}
```

2. **Vehicle Listing API:**
```
JavaScript → GET /get-vehicles/ → get_vehicles() → Vehicle.objects.filter() → MySQL → {'vehicles': [...]}
```

3. **Add Vehicle API:**
```
Form Submit → POST /add-vehicle/ → add_vehicle() → Vehicle.objects.create() → MySQL → {'success': true}
```

## 8. Database Relationships Flow

### Model Relationships
```
User (Django Auth) ←→ UserProfile (One-to-One)
Vehicle ←→ VehicleImage (One-to-Many)
BrandImage ←→ ModelImage (One-to-Many via brand field)
Vehicle ←→ VehicleClick (One-to-Many)
```

### Foreign Key Connections
```python
# UserProfile connects to User
user = models.OneToOneField(User, on_delete=models.CASCADE)

# VehicleImage connects to Vehicle
vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

# ModelImage connects to BrandImage
brand = models.ForeignKey(BrandImage, on_delete=models.CASCADE)
```

## 9. Static Files Flow

### CSS/JS Loading
```
templates/base.html → {% load static %} → static/css/style.css → Browser
```

**Settings Configuration:**
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 10. Template Rendering Flow

### Django Template System
```
View Function → Context Data → Template → Rendered HTML → Browser
```

**Example:**
```python
def home(request):
    user_logged_in = request.session.get('user_id') is not None
    return render(request, 'home.html', {'user_logged_in': user_logged_in})
```

## 11. Error Handling Flow

### Exception Management
```
Try-Catch Blocks → Error Logging → JSON Error Response → Frontend Error Display
```

**Example:**
```python
try:
    user_profile = UserProfile.objects.get(phone=phone)
    return JsonResponse({'success': True})
except UserProfile.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'User not found'})
except Exception as e:
    return JsonResponse({'success': False, 'error': str(e)})
```

## 12. Migration Flow

### Database Schema Updates
```
Model Changes → makemigrations → Migration Files → migrate → Database Schema Update
```

**Commands:**
```bash
python manage.py makemigrations
python manage.py migrate
```

## 13. Admin Interface Flow

### Django Admin Connection
```
admin.py Registration → Django Admin Interface → Database CRUD Operations
```

**File: `admin.py`**
```python
from django.contrib import admin
from .models import Vehicle, UserProfile

admin.site.register(Vehicle)
admin.site.register(UserProfile)
```

## 14. Production Deployment Flow

### Server Setup
```
Code → Git Repository → Server → Virtual Environment → Dependencies → Database Setup → Static Files → WSGI Server
```

This complete flow shows how every component in your GoWheels project connects from frontend user actions to database operations and back to the user interface.