# GoWheels Project Structure

## Root Directory Structure
```
d:\Gowheels/
├── gowheels/                    # Main Django App
├── gowheels_project/            # Django Project Settings
├── media/                       # User Uploaded Files
├── static/                      # Static Files (CSS, JS)
├── templates/                   # HTML Templates
├── .env                         # Environment Variables
├── create_database.py           # Database Creation Script
├── manage.py                    # Django Management Script
└── requirements.txt             # Python Dependencies
```

## Detailed Project Structure

### 1. Main Django App (`gowheels/`)
```
gowheels/
├── management/
│   └── commands/
│       ├── __init__.py
│       └── clear_admin_data.py     # Custom Django Command
├── migrations/                     # Database Migrations
│   ├── 0001_initial.py
│   ├── 0002_auto_20251220_1308.py
│   ├── 0003_userprofile_booking.py
│   ├── 0004_brandimage_modelimage.py
│   ├── 0005_vehicle_seller_phone_vehicleimage.py
│   ├── 0006_vehicle_added_by_vehicle_approval_status.py
│   ├── 0007_vehicle_daily_end_range_vehicle_daily_start_range_and_more.py
│   ├── 0008_brandimage_name_modelimage_name.py
│   ├── 0009_modelimage_brand.py
│   ├── 0010_vehicle_pincode.py
│   ├── 0011_vehicleclick.py
│   ├── 0012_category_update_relationships.py
│   ├── 0013_vehicle_unit_type.py
│   ├── 0014_adminbrand_admingroup_adminmodel_admincategory_and_more.py
│   ├── 0015_vehicle_owner_name_vehicle_village.py
│   ├── 0016_vehicle_per_day_price_vehicle_per_hour_price.py
│   └── 0017_userprofile_blocked.py
├── __init__.py
├── admin.py                        # Django Admin Configuration
├── api_views.py                    # API View Functions
├── apps.py                         # App Configuration
├── models.py                       # Database Models
├── urls.py                         # URL Routing
└── views.py                        # View Functions (32+ APIs)
```

### 2. Project Settings (`gowheels_project/`)
```
gowheels_project/
├── static/                         # Project Static Files
│   ├── css/
│   └── js/
├── templates/                      # Project Templates
├── __init__.py
├── settings.py                     # Django Settings & Configuration
├── urls.py                         # Main URL Configuration
└── wsgi.py                         # WSGI Configuration
```

### 3. Media Files (`media/`)
```
media/
├── brands/                         # Brand Images
├── categories/                     # Category Images
├── models/                         # Model Images
└── vehicles/                       # Vehicle Images
    └── seller/                     # Seller Vehicle Images
```

### 4. Static Files (`static/`)
```
static/
├── css/
│   ├── login.css                   # Login Page Styles
│   └── style.css                   # Main Stylesheet
└── js/
    ├── admin-login.js              # Admin Login JavaScript
    ├── api-examples.js             # API Integration Examples
    ├── login.js                    # Login Functionality
    └── main.js                     # Main JavaScript Functions
```

### 5. Templates (`templates/`)
```
templates/
├── add_brands_models_form.html     # Brand/Model Management
├── add_model_to_brand.html         # Model Addition Form
├── home.html                       # Homepage
├── login.html                      # User Login Page
├── phone_check.html                # Phone Verification
├── register.html                   # User Registration
├── seller_dashboard.html           # Seller Dashboard
├── seller_vehicles.html            # Seller Vehicle Management
├── super_admin_categories.html     # Admin Category Management
├── super_admin_login.html          # Admin Login
└── user_browse_categories.html     # User Category Browser
```

## Key Files Description

### Core Application Files
- **models.py**: Database models (Vehicle, UserProfile, BrandImage, ModelImage, etc.)
- **views.py**: 48 API endpoints and view functions
- **urls.py**: URL routing configuration
- **settings.py**: Django configuration with MySQL database setup
- **api_views.py**: Additional API view functions

### Configuration Files
- **.env**: Environment variables (database credentials, secret keys)
- **requirements.txt**: Python package dependencies
- **manage.py**: Django management commands

### Database Files
- **create_database.py**: Script to create MySQL database
- **migrations/**: Database schema changes and updates

## Technology Stack

### Backend
- **Framework**: Django 4.x
- **Database**: MySQL with Django ORM
- **Authentication**: Session-based with OTP verification
- **API**: REST APIs with JSON responses

### Frontend
- **HTML5**: Template structure
- **CSS3**: Styling and responsive design
- **JavaScript**: AJAX/Fetch API for backend communication
- **Bootstrap**: UI framework (if used)

### File Storage
- **Media Files**: User uploads (images, documents)
- **Static Files**: CSS, JavaScript, images

## Database Models
- **Vehicle**: Main vehicle information
- **UserProfile**: User account details
- **BrandImage**: Vehicle brand images
- **ModelImage**: Vehicle model images
- **VehicleImage**: Individual vehicle photos
- **VehicleClick**: User interaction tracking

## API Endpoints (32+)
- Authentication APIs (login, register, OTP)
- Vehicle Management APIs (CRUD operations)
- User Management APIs (profile, bookings)
- Admin APIs (user management, approvals)
- File Upload APIs (images, documents)

This structure follows Django best practices with clear separation of concerns and modular organization.