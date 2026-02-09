from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Vehicle, UserProfile, BrandImage, ModelImage, VehicleImage, Pincode, PromotionSettings, VehiclePromotion
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
import json

# Try to import VehicleClick, handle if migration not run yet
try:
    from .models import VehicleClick
    VEHICLE_CLICK_AVAILABLE = True
except ImportError:
    VEHICLE_CLICK_AVAILABLE = False

def home(request):
    user_logged_in = request.session.get('user_id') is not None
    return render(request, 'home.html', {'user_logged_in': user_logged_in})

def phone_check(request):
    return render(request, 'phone_check.html')

@csrf_exempt
def check_phone(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            
            if not phone:
                return JsonResponse({'error': 'Phone number required'})
            
            exists = UserProfile.objects.filter(phone=phone).exists()
            return JsonResponse({'exists': exists})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Invalid request method'})

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            phone = request.POST.get('phone')
            name = request.POST.get('name')
            pincode = request.POST.get('pincode')
            
            # Check if phone already exists
            if UserProfile.objects.filter(phone=phone).exists():
                return JsonResponse({'success': False, 'error': 'Phone number already registered'})
            
            # Create user
            user = User.objects.create_user(
                username=phone,
                first_name=name
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone=phone,
                pincode=pincode
            )
            
            return JsonResponse({'success': True, 'message': 'Registration successful'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        try:
            phone = request.POST.get('phone')
            otp = request.POST.get('otp')
            
            # Check if user exists
            try:
                user_profile = UserProfile.objects.get(phone=phone)
                user = user_profile.user
                
                # Check if user is blocked
                if user_profile.blocked:
                    return JsonResponse({'success': False, 'error': 'Your account has been blocked. Please contact support.'})
                
                # Simple OTP verification (in production, use proper OTP service)
                if otp == '123456':  # Demo OTP
                    # Login successful
                    request.session['user_id'] = user.id
                    request.session['phone'] = phone
                    request.session['unique_id'] = user_profile.unique_id
                    return JsonResponse({
                        'success': True, 
                        'message': 'Login successful',
                        'unique_id': user_profile.unique_id
                    })
                else:
                    return JsonResponse({'success': False, 'error': 'Invalid OTP'})
                    
            except UserProfile.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Phone number not registered'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'login.html')

def super_admin(request):
    return render(request, 'super_admin.html')

def super_admin_login(request):
    if request.method == 'POST':
        try:
            phone = request.POST.get('phone')
            otp = request.POST.get('otp')
            
            # Authorized super admin phone numbers
            authorized_phones = ['9876543210', '+919876543210', '8765432109', '+918765432109']
            
            # Check if phone is authorized
            if phone not in authorized_phones:
                return JsonResponse({'success': False, 'error': 'Unauthorized phone number'})
            
            # Simple OTP verification (in production, use proper OTP service)
            if otp == '123456':  # Super Admin OTP
                # Login successful
                request.session['super_admin_logged_in'] = True
                request.session['super_admin_phone'] = phone
                return JsonResponse({'success': True, 'message': 'Super Admin login successful'})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid OTP'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'super_admin_login.html')

def super_admin_panel(request):
    # Check if super admin is logged in
    if not request.session.get('super_admin_logged_in'):
        return redirect('/super-admin-login/')
    
    # Redirect to category management page
    return redirect('/super-admin-categories/')

def add_vehicle(request):
    # Check if super admin is logged in
    if not request.session.get('super_admin_logged_in'):
        return redirect('/super-admin-login/')
        
    if request.method == 'POST':
        try:
            # Handle brand images from the new upload system
            if 'brandImageInput' in request.FILES:
                # Get the selected category and brand name from form data
                selected_category = request.POST.get('selected_brand_category', 'car')
                brand_name = request.POST.get('brand_name', 'Brand Name')
                BrandImage.objects.create(
                    category=selected_category, 
                    name=brand_name,
                    image=request.FILES['brandImageInput']
                )
            
            # Handle model images from the new upload system
            if 'modelImageInput' in request.FILES:
                selected_category = request.POST.get('selected_model_category', 'car')
                model_name = request.POST.get('model_name', 'Model Name')
                brand_id = request.POST.get('selected_brand_for_model')  # Get selected brand ID
                
                brand_instance = None
                if brand_id and brand_id.startswith('temp_'):
                    # Handle temporary brand (from entered name)
                    brand_name = brand_id.replace('temp_car_', '').replace('temp_bike_', '').replace('temp_truck_', '')
                    # Find or create brand with this name and category
                    brand_instance, created = BrandImage.objects.get_or_create(
                        name=brand_name,
                        category=selected_category
                    )
                elif brand_id:
                    try:
                        brand_instance = BrandImage.objects.get(id=brand_id)
                    except BrandImage.DoesNotExist:
                        pass
                
                for img in request.FILES.getlist('modelImageInput'):
                    ModelImage.objects.create(
                        category=selected_category, 
                        name=model_name,
                        brand=brand_instance,
                        image=img
                    )
            
            # Handle single brand images for each category (legacy support)
            if 'car_brand_image' in request.FILES:
                BrandImage.objects.create(category='car', image=request.FILES['car_brand_image'])
            
            if 'bike_brand_image' in request.FILES:
                BrandImage.objects.create(category='bike', image=request.FILES['bike_brand_image'])
            
            if 'truck_brand_image' in request.FILES:
                BrandImage.objects.create(category='truck', image=request.FILES['truck_brand_image'])
            
            # Handle multiple model images for each category (legacy support)
            if 'car_model_images' in request.FILES:
                for img in request.FILES.getlist('car_model_images'):
                    ModelImage.objects.create(category='car', image=img)
            
            if 'bike_model_images' in request.FILES:
                for img in request.FILES.getlist('bike_model_images'):
                    ModelImage.objects.create(category='bike', image=img)
            
            if 'truck_model_images' in request.FILES:
                for img in request.FILES.getlist('truck_model_images'):
                    ModelImage.objects.create(category='truck', image=img)
            
            # Create vehicle with approved status for super admin
            vehicle = Vehicle(
                category_name=request.POST.get('category_name', 'General'),
                brand_name=request.POST.get('brand_name', 'Brand'),
                model_name=request.POST.get('model_name', 'Model'),
                year=int(request.POST.get('year')),
                state=request.POST.get('state'),
                hourly_start_range=float(request.POST.get('hourly_start_range', 100)),
                hourly_end_range=float(request.POST.get('hourly_end_range', 3000)),
                daily_start_range=float(request.POST.get('daily_start_range', 100)),
                daily_end_range=float(request.POST.get('daily_end_range', 3000)),
                min_price=float(request.POST.get('hourly_start_range', 100)),  # Set to hourly start for compatibility
                max_price=float(request.POST.get('hourly_end_range', 3000)),  # Set to hourly end for compatibility
                price=float(request.POST.get('hourly_start_range', 100)),  # Set default price
                pricing_type='per-hour',  # Set default pricing type
                approval_status='approved',
                added_by='super_admin'
            )
            vehicle.save()
            
            return JsonResponse({'success': True, 'message': 'Vehicle and images added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get vehicle statistics
    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(available=True).count()
    pending_vehicles = Vehicle.objects.filter(approval_status='pending').count()
    
    return render(request, 'add_vehicle_new.html', {
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'pending_vehicles': pending_vehicles
    })

def browse_vehicles(request):
    vehicles = Vehicle.objects.filter(available=True, approval_status='approved')
    
    # Get all Super Admin added categories (type group1, group2, group3) with images
    categories = BrandImage.objects.filter(
        category__in=['group1', 'group2', 'group3']
    ).exclude(image='brands/default.jpg').values('id', 'category', 'name', 'image').distinct()
    
    # Convert to JSON for JavaScript
    import json
    categories_data = json.dumps([{
        'id': cat['id'], 
        'name': cat['name'], 
        'image': f"/media/{cat['image']}"
    } for cat in categories if cat['image']])
    
    return render(request, 'browse_vehicles_fixed.html', {
        'vehicles': vehicles,
        'categories_data': categories_data
    })

def logout_view(request):
    request.session.flush()
    return redirect('/')

def add_categories(request):
    # Check if super admin is logged in
    if not request.session.get('super_admin_logged_in'):
        return redirect('/super-admin-login/')
    
    # Redirect to new multi-step vehicle addition
    return redirect('/add-vehicle-step1/')

def add_vehicle_step1(request):
    if not request.session.get('super_admin_logged_in'):
        return redirect('/super-admin-login/')
    return render(request, 'category_management.html')

def save_category_only(request):
    if request.method == 'POST':
        try:
            category_type = request.POST.get('category_type')
            category_name = request.POST.get('category_name')
            
            if 'category_image' in request.FILES:
                BrandImage.objects.create(
                    category=category_type.lower(),
                    name=category_name,
                    image=request.FILES['category_image']
                )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def get_added_categories(request):
    try:
        categories = BrandImage.objects.filter(category__in=['a', 'b', 'c']).values('category', 'name', 'image').distinct()
        categories_data = [{
            'type': cat['category'].upper(),
            'name': cat['name'],
            'image': f"/media/{cat['image']}"
        } for cat in categories]
        return JsonResponse({'categories': categories_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def add_brands_models(request):
    if not request.session.get('super_admin_logged_in'):
        return redirect('/super-admin-login/')
    return render(request, 'add_vehicle_step2.html')

def add_vehicle_step2(request):
    if not request.session.get('super_admin_logged_in'):
        return redirect('/super-admin-login/')
    return render(request, 'add_vehicle_step2.html')

def submit_vehicle(request):
    if request.method == 'POST':
        try:
            category_type = request.POST.get('category_type')
            category_name = request.POST.get('category_name')
            price_per_hour = float(request.POST.get('price_per_hour'))
            price_per_day = float(request.POST.get('price_per_day'))
            
            # Save category image
            if 'category_image' in request.FILES:
                BrandImage.objects.create(
                    category=category_type.lower(),
                    name=category_name,
                    image=request.FILES['category_image']
                )
            
            # Save brand images
            if 'brand_images' in request.FILES:
                for img in request.FILES.getlist('brand_images'):
                    BrandImage.objects.create(
                        category=category_type.lower(),
                        name=f'{category_name}_brand',
                        image=img
                    )
            
            # Save model images
            if 'model_images' in request.FILES:
                for img in request.FILES.getlist('model_images'):
                    ModelImage.objects.create(
                        category=category_type.lower(),
                        name=f'{category_name}_model',
                        image=img
                    )
            
            # Create vehicle
            Vehicle.objects.create(
                category_name=category_name,
                brand_name=f'{category_name}_brand',
                model_name=f'{category_name}_model',
                year=2024,
                state='All States',
                price=price_per_hour,
                pricing_type='per-hour',
                hourly_start_range=price_per_hour,
                hourly_end_range=price_per_hour,
                daily_start_range=price_per_day,
                daily_end_range=price_per_day,
                approval_status='approved',
                added_by='super_admin',
                available=True
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def get_all_vehicles(request):
    try:
        # Check if super admin is logged in
        if not request.session.get('super_admin_logged_in'):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
            
        vehicles = Vehicle.objects.filter(added_by='super_admin').order_by('-id')
        vehicles_data = []
        for vehicle in vehicles:
            vehicles_data.append({
                'id': vehicle.id,
                'category_name': vehicle.category_name,
                'brand_name': vehicle.brand_name,
                'model_name': vehicle.model_name,
                'year': vehicle.year,
                'price': str(vehicle.price),
                'pricing_type': vehicle.pricing_type.replace('per-', '')
            })
        return JsonResponse({'vehicles': vehicles_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def save_category(request):
    if request.method == 'POST':
        try:
            category_type = request.POST.get('category_type')
            category_name = request.POST.get('category_name')
            
            # Handle multiple category images
            if 'category_images' in request.FILES:
                for img in request.FILES.getlist('category_images'):
                    BrandImage.objects.create(
                        category=category_type.lower(),
                        name=category_name,
                        image=img
                    )
            
            return JsonResponse({'success': True, 'message': f'Category {category_type} saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def user_categories(request):
    # Redirect directly to browse categories page
    return redirect('/user-browse-categories/')

def user_dashboard(request):
    # Redirect directly to browse categories page
    return redirect('/user-browse-categories/')

def add_brands(request):
    if request.method == 'POST':
        try:
            # Handle car brand images
            if 'car_brand_images' in request.FILES:
                for img in request.FILES.getlist('car_brand_images'):
                    BrandImage.objects.create(category='car', image=img)
            
            # Handle bike brand images
            if 'bike_brand_images' in request.FILES:
                for img in request.FILES.getlist('bike_brand_images'):
                    BrandImage.objects.create(category='bike', image=img)
            
            # Handle truck brand images
            if 'truck_brand_images' in request.FILES:
                for img in request.FILES.getlist('truck_brand_images'):
                    BrandImage.objects.create(category='truck', image=img)
            
            return JsonResponse({'success': True, 'message': 'Brand images uploaded successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'add_brands.html')

def seller_form(request):
    if request.method == 'POST':
        try:
            # Get brand and model names from IDs
            brand_id = request.POST.get('selected_brand')
            model_id = request.POST.get('selected_model')
            
            brand_name = 'Unknown Brand'
            model_name = 'Unknown Model'
            
            try:
                if brand_id:
                    brand = BrandImage.objects.get(id=brand_id)
                    brand_name = brand.name
            except BrandImage.DoesNotExist:
                pass
                
            try:
                if model_id:
                    model = ModelImage.objects.get(id=model_id)
                    model_name = model.name
            except ModelImage.DoesNotExist:
                pass
            
            # Handle pricing - use hourly as default, daily as secondary
            hourly_price = request.POST.get('hourly_price')
            daily_price = request.POST.get('daily_price')
            
            price = float(hourly_price) if hourly_price else float(daily_price)
            pricing_type = 'per-hour' if hourly_price else 'per-day'
            
            # Create vehicle
            vehicle = Vehicle(
                category_name=request.POST.get('selected_category'),
                brand_name=brand_name,
                model_name=model_name,
                year=int(request.POST.get('year')),
                state=request.POST.get('state'),
                price=price,
                pricing_type=pricing_type,
                seller_phone=request.POST.get('phone'),
                pincode=request.POST.get('pincode'),
                approval_status='approved',
                added_by='seller',
                available=True
            )
            
            # Set hourly and daily prices if both are provided
            if hourly_price:
                vehicle.hourly_start_range = float(hourly_price)
                vehicle.hourly_end_range = float(hourly_price)
            if daily_price:
                vehicle.daily_start_range = float(daily_price)
                vehicle.daily_end_range = float(daily_price)
            
            vehicle.save()
            
            # Handle 5 vehicle images
            if 'vehicle_images' in request.FILES:
                for img in request.FILES.getlist('vehicle_images'):
                    VehicleImage.objects.create(vehicle=vehicle, image=img)
            
            return JsonResponse({'success': True, 'message': 'Vehicle listed successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get brand and model images for template
    car_brand_images = list(BrandImage.objects.filter(category='car').values_list('image', flat=True))
    bike_brand_images = list(BrandImage.objects.filter(category='bike').values_list('image', flat=True))
    truck_brand_images = list(BrandImage.objects.filter(category='truck').values_list('image', flat=True))
    
    car_model_images = list(ModelImage.objects.filter(category='car').values_list('image', flat=True))
    bike_model_images = list(ModelImage.objects.filter(category='bike').values_list('image', flat=True))
    truck_model_images = list(ModelImage.objects.filter(category='truck').values_list('image', flat=True))
    
    import json
    return render(request, 'seller_form.html', {
        'car_brand_images': json.dumps([f'/media/{img}' for img in car_brand_images]),
        'bike_brand_images': json.dumps([f'/media/{img}' for img in bike_brand_images]),
        'truck_brand_images': json.dumps([f'/media/{img}' for img in truck_brand_images]),
        'car_model_images': json.dumps([f'/media/{img}' for img in car_model_images]),
        'bike_model_images': json.dumps([f'/media/{img}' for img in bike_model_images]),
        'truck_model_images': json.dumps([f'/media/{img}' for img in truck_model_images])
    })

def get_vehicles(request):
    vehicles_data = []
    try:
        category_name = str(request.GET.get('cat', ''))
        brand_name = str(request.GET.get('br', '')) 
        model_name = str(request.GET.get('mod', ''))
        pincode = str(request.GET.get('pincode', ''))
        radius_km = int(request.GET.get('radius', 10))  # Default 10km radius
        
        vehicles = Vehicle.objects.filter(available=True, approval_status='approved')
        
        if category_name:
            vehicles = vehicles.filter(category_name__iexact=category_name)
        if brand_name:
            vehicles = vehicles.filter(brand_name__iexact=brand_name)
        if model_name:
            vehicles = vehicles.filter(model_name__iexact=model_name)
        if pincode:
            # Distance-based search using Haversine formula
            try:
                nearby_pincodes = Pincode.get_nearby_pincodes(pincode, radius_km)
                vehicles = vehicles.filter(pincode__in=nearby_pincodes)
            except Exception:
                # Fallback to simple numeric range if GPS data not available
                try:
                    base_pincode = int(pincode)
                    range_size = 10
                    min_pincode = base_pincode - range_size
                    max_pincode = base_pincode + range_size
                    vehicles = vehicles.filter(
                        pincode__gte=str(min_pincode),
                        pincode__lte=str(max_pincode)
                    )
                except (ValueError, TypeError):
                    vehicles = vehicles.filter(pincode__exact=pincode)
        
        for vehicle in vehicles:
            try:
                vehicle_images = []
                for img in vehicle.images.all():
                    vehicle_images.append('/media/' + str(img.image))
                
                vehicles_data.append({
                    'id': int(vehicle.id),
                    'category_name': str(vehicle.category_name),
                    'brand_name': str(vehicle.brand_name),
                    'model_name': str(vehicle.model_name),
                    'year': int(vehicle.year),
                    'price': str(vehicle.price),
                    'per_day_price': str(vehicle.per_day_price or 0),
                    'per_hour_price': str(vehicle.per_hour_price or 0),
                    'pricing_type': str(vehicle.pricing_type),
                    'unit_type': str(vehicle.unit_type or 'unit_price'),
                    'seller_phone': str(vehicle.seller_phone or ''),
                    'pincode': str(vehicle.pincode or ''),
                    'village': str(vehicle.village or ''),
                    'owner_name': str(vehicle.owner_name or ''),
                    'images': vehicle_images
                })
            except:
                continue
                
    except:
        pass
        
    return JsonResponse({'vehicles': vehicles_data})

def create_state_admin(request):
    return render(request, 'create_state_admin.html')

def state_admin(request):
    return render(request, 'state_admin.html')

def state_admin_panel(request):
    # Get state admin vehicle statistics
    pending_count = Vehicle.objects.filter(added_by='state_admin', approval_status='pending').count()
    approved_count = Vehicle.objects.filter(added_by='state_admin', approval_status='approved').count()
    rejected_count = Vehicle.objects.filter(added_by='state_admin', approval_status='rejected').count()
    
    return render(request, 'state_admin_panel.html', {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count
    })

def state_admin_add_vehicle(request):
    if request.method == 'POST':
        try:
            # Handle brand images
            if 'car_brand_image' in request.FILES:
                BrandImage.objects.create(category='car', image=request.FILES['car_brand_image'])
            if 'bike_brand_image' in request.FILES:
                BrandImage.objects.create(category='bike', image=request.FILES['bike_brand_image'])
            if 'truck_brand_image' in request.FILES:
                BrandImage.objects.create(category='truck', image=request.FILES['truck_brand_image'])
            
            # Handle model images
            if 'car_model_images' in request.FILES:
                for img in request.FILES.getlist('car_model_images'):
                    ModelImage.objects.create(category='car', image=img)
            if 'bike_model_images' in request.FILES:
                for img in request.FILES.getlist('bike_model_images'):
                    ModelImage.objects.create(category='bike', image=img)
            if 'truck_model_images' in request.FILES:
                for img in request.FILES.getlist('truck_model_images'):
                    ModelImage.objects.create(category='truck', image=img)
            
            # Create vehicle with pending approval
            vehicle = Vehicle(
                category_name=request.POST.get('category_name', 'General'),
                brand_name=request.POST.get('brand_name', 'Brand'),
                model_name=request.POST.get('model_name', 'Model'),
                year=int(request.POST.get('year')),
                state=request.POST.get('state'),
                price=float(request.POST.get('price')),
                pricing_type=request.POST.get('pricing_type'),
                approval_status='pending',
                added_by='state_admin',
                available=False
            )
            vehicle.save()
            
            return JsonResponse({'success': True, 'message': 'Vehicle submitted for Super Admin approval'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get state admin vehicle statistics
    pending_count = Vehicle.objects.filter(added_by='state_admin', approval_status='pending').count()
    approved_count = Vehicle.objects.filter(added_by='state_admin', approval_status='approved').count()
    rejected_count = Vehicle.objects.filter(added_by='state_admin', approval_status='rejected').count()
    
    return render(request, 'state_admin_add_vehicle.html', {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count
    })

def search_vehicles(request):
    try:
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'vehicles': []})
        
        vehicles = Vehicle.objects.filter(
            Q(brand_name__icontains=query) |
            Q(model_name__icontains=query) |
            Q(category_name__icontains=query) |
            Q(year__icontains=query) |
            Q(state__icontains=query)
        ).order_by('-id')
        
        vehicles_data = []
        for vehicle in vehicles:
            vehicles_data.append({
                'id': vehicle.id,
                'category_name': vehicle.category_name,
                'brand_name': vehicle.brand_name,
                'model_name': vehicle.model_name,
                'year': vehicle.year,
                'state': vehicle.state,
                'price': str(vehicle.price),
                'pricing_type': vehicle.pricing_type,
                'available': vehicle.available
            })
        
        return JsonResponse({'vehicles': vehicles_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_pending_approvals(request):
    try:
        # Only show vehicles added by state_admin that are pending
        vehicles = Vehicle.objects.filter(
            approval_status='pending', 
            added_by='state_admin'
        ).order_by('-id')
        
        vehicles_data = []
        for vehicle in vehicles:
            vehicles_data.append({
                'id': vehicle.id,
                'category_name': vehicle.category_name,
                'brand_name': vehicle.brand_name,
                'model_name': vehicle.model_name,
                'year': vehicle.year,
                'state': vehicle.state,
                'price': str(vehicle.price),
                'pricing_type': vehicle.pricing_type
            })
        
        return JsonResponse({'vehicles': vehicles_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def approve_vehicle(request, vehicle_id):
    if request.method == 'POST':
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            vehicle.approval_status = 'approved'
            vehicle.available = True
            vehicle.save()
            return JsonResponse({'success': True})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

def reject_vehicle(request, vehicle_id):
    if request.method == 'POST':
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            vehicle.approval_status = 'rejected'
            vehicle.available = False
            vehicle.save()
            return JsonResponse({'success': True})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

def get_state_admin_vehicles(request):
    try:
        # Only show vehicles added by state_admin
        vehicles = Vehicle.objects.filter(added_by='state_admin').order_by('-id')
        
        vehicles_data = []
        for vehicle in vehicles:
            vehicles_data.append({
                'id': vehicle.id,
                'category_name': vehicle.category_name,
                'brand_name': vehicle.brand_name,
                'model_name': vehicle.model_name,
                'year': vehicle.year,
                'state': vehicle.state,
                'price': str(vehicle.price),
                'pricing_type': vehicle.pricing_type,
                'approval_status': vehicle.approval_status
            })
        
        return JsonResponse({'vehicles': vehicles_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def delete_vehicle(request, vehicle_id):
    if request.method == 'POST':
        try:
            # Check if super admin is logged in
            if request.session.get('super_admin_logged_in'):
                vehicle = Vehicle.objects.get(id=vehicle_id, added_by='super_admin')
            else:
                # Allow sellers to delete their own vehicles
                user_phone = request.session.get('phone')
                if not user_phone:
                    return JsonResponse({'success': False, 'error': 'Not authenticated'})
                
                # Try to find vehicle by seller_phone OR added_by='seller' with matching session
                try:
                    vehicle = Vehicle.objects.get(id=vehicle_id, seller_phone=user_phone)
                except Vehicle.DoesNotExist:
                    # Fallback: check if it's a seller vehicle and user is authenticated
                    vehicle = Vehicle.objects.get(id=vehicle_id, added_by='seller')
            
            # Delete related images first
            vehicle.images.all().delete()
            vehicle.delete()
            return JsonResponse({'success': True, 'message': 'Vehicle deleted successfully'})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found or not authorized'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def edit_vehicle(request, vehicle_id):
    try:
        # Check if user owns this vehicle
        user_phone = request.session.get('phone')
        if not user_phone:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
            
        vehicle = Vehicle.objects.get(id=vehicle_id, seller_phone=user_phone)
        
        if request.method == 'POST':
            try:
                vehicle.year = int(request.POST.get('year', vehicle.year))
                
                # Update pricing fields
                per_hour_price = request.POST.get('per_hour_price')
                per_day_price = request.POST.get('per_day_price')
                
                if per_hour_price:
                    vehicle.per_hour_price = float(per_hour_price)
                    vehicle.hourly_start_range = float(per_hour_price)
                    vehicle.hourly_end_range = float(per_hour_price)
                    
                if per_day_price:
                    vehicle.per_day_price = float(per_day_price)
                    vehicle.daily_start_range = float(per_day_price)
                    vehicle.daily_end_range = float(per_day_price)
                
                # Update main price field based on what's provided
                if per_hour_price:
                    vehicle.price = float(per_hour_price)
                    vehicle.pricing_type = 'per-hour'
                elif per_day_price:
                    vehicle.price = float(per_day_price)
                    vehicle.pricing_type = 'per-day'
                
                vehicle.pincode = request.POST.get('pincode', vehicle.pincode)
                vehicle.village = request.POST.get('village', vehicle.village)
                vehicle.save()
                
                return JsonResponse({'success': True, 'message': 'Vehicle updated successfully'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return render(request, 'edit_vehicle.html', {'vehicle': vehicle})
    except Vehicle.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Vehicle not found or not authorized'})

def seller_dashboard_form(request):
    if request.method == 'POST':
        try:
            category = str(request.POST.get('selected_category', ''))
            brand_name = str(request.POST.get('selected_brand', ''))
            model_name = str(request.POST.get('selected_model', ''))
            
            hourly_price = request.POST.get('hourly_price')
            daily_price = request.POST.get('daily_price')
            unit_value = request.POST.get('unit_value')
            
            # Set default price based on what's provided
            price = 0
            pricing_type = 'per-hour'
            
            if hourly_price:
                price = float(hourly_price)
                pricing_type = 'per-hour'
            elif daily_price:
                price = float(daily_price)
                pricing_type = 'per-day'
            elif unit_value:
                price = float(unit_value)
                pricing_type = 'per-hour'  # Default
            
            vehicle = Vehicle(
                category_name=category,
                brand_name=brand_name,
                model_name=model_name,
                year=int(request.POST.get('year')),
                state='India',
                price=price,
                pricing_type=pricing_type,
                unit_type=str(request.POST.get('unit_type', 'unit_price')),
                seller_phone=str(request.session.get('phone', '')),
                pincode=str(request.POST.get('pincode', '')),
                village=str(request.POST.get('village', '')),
                owner_name=str(request.POST.get('owner_name', '')),
                approval_status='approved',
                added_by='seller',
                available=True
            )
            
            # Set per hour and per day prices
            if hourly_price:
                vehicle.per_hour_price = float(hourly_price)
                vehicle.hourly_start_range = float(hourly_price)
                vehicle.hourly_end_range = float(hourly_price)
            else:
                vehicle.per_hour_price = 0
                
            if daily_price:
                vehicle.per_day_price = float(daily_price)
                vehicle.daily_start_range = float(daily_price)
                vehicle.daily_end_range = float(daily_price)
            else:
                vehicle.per_day_price = 0
            
            vehicle.save()
            
            if 'vehicle_images' in request.FILES:
                for img in request.FILES.getlist('vehicle_images'):
                    VehicleImage.objects.create(vehicle=vehicle, image=img)
            
            return JsonResponse({'success': True, 'message': 'Vehicle listed successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def seller_dashboard(request):
    # Get user data from session
    user_id = request.session.get('user_id')
    user_phone = request.session.get('phone', '')
    user_name = ''
    user_pincode = ''
    user_village = ''
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            user_name = f"{user.first_name}".strip()
            user_pincode = user_profile.pincode or ''
            # Add village field if exists in UserProfile model
            user_village = getattr(user_profile, 'village', '')
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            pass
    
    return render(request, 'seller_dashboard.html', {
        'user_name': user_name,
        'user_phone': user_phone,
        'user_pincode': user_pincode,
        'user_village': user_village
    })

@csrf_exempt
def track_vehicle_click(request):
    if request.method == 'POST':
        try:
            if not VEHICLE_CLICK_AVAILABLE:
                return JsonResponse({'success': False, 'error': 'Click tracking not available'})
                
            data = json.loads(request.body)
            seller_phone = data.get('seller_phone')
            buyer_phone = data.get('buyer_phone')
            buyer_name = data.get('buyer_name', 'Anonymous')
            
            # Find vehicle by seller phone
            vehicle = Vehicle.objects.filter(seller_phone=seller_phone).first()
            if vehicle:
                VehicleClick.objects.create(
                    vehicle=vehicle,
                    buyer_phone=buyer_phone,
                    buyer_name=buyer_name
                )
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'error': 'Vehicle not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_seller_vehicles(request):
    try:
        user_phone = request.session.get('phone', '')
        
        # Get all vehicles for current seller (approved, pending, rejected)
        if VEHICLE_CLICK_AVAILABLE:
            vehicles = Vehicle.objects.filter(
                seller_phone=user_phone
            ).annotate(
                click_count=Count('clicks')
            ).order_by('-id')
        else:
            vehicles = Vehicle.objects.filter(
                seller_phone=user_phone
            ).order_by('-id')
        
        total_count = vehicles.count()
        active_count = vehicles.filter(available=True).count()
        
        vehicles_data = []
        for vehicle in vehicles:
            # Get vehicle images
            vehicle_images = [f'/media/{img.image}' for img in vehicle.images.all()]
            
            vehicle_data = {
                'id': vehicle.id,
                'category_name': vehicle.category_name,
                'brand_name': vehicle.brand_name,
                'model_name': vehicle.model_name,
                'year': vehicle.year,
                'state': vehicle.state,
                'price': str(vehicle.price),
                'pricing_type': vehicle.pricing_type,
                'per_hour_price': str(vehicle.per_hour_price),
                'per_day_price': str(vehicle.per_day_price),
                'pincode': vehicle.pincode or '',
                'village': vehicle.village or '',
                'owner_name': vehicle.owner_name or '',
                'available': vehicle.available,
                'approval_status': vehicle.approval_status,
                'click_count': 0,
                'recent_clicks': [],
                'images': vehicle_images
            }
            
            if VEHICLE_CLICK_AVAILABLE:
                # Get recent clicks for this vehicle
                recent_clicks = VehicleClick.objects.filter(vehicle=vehicle).order_by('-clicked_at')[:5]
                clicks_data = [{
                    'buyer_name': click.buyer_name,
                    'buyer_phone': click.buyer_phone,
                    'clicked_at': click.clicked_at.strftime('%Y-%m-%d %H:%M')
                } for click in recent_clicks]
                
                vehicle_data['click_count'] = getattr(vehicle, 'click_count', 0)
                vehicle_data['recent_clicks'] = clicks_data
            
            vehicles_data.append(vehicle_data)
        
        return JsonResponse({
            'vehicles': vehicles_data,
            'total': total_count,
            'active': active_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def toggle_vehicle_status(request, vehicle_id):
    if request.method == 'POST':
        try:
            # Check if user owns this vehicle
            user_phone = request.session.get('phone')
            if not user_phone:
                return JsonResponse({'success': False, 'error': 'Not authenticated'})
            
            vehicle = Vehicle.objects.get(id=vehicle_id, seller_phone=user_phone)
            vehicle.available = not vehicle.available
            vehicle.save()
            return JsonResponse({'success': True, 'available': vehicle.available})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found or not authorized'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_brand_images(request):
    try:
        brands = {}
        
        # Get all Super Admin categories (not brands)
        categories = BrandImage.objects.filter(
            category__in=['group1', 'group2', 'group3']
        ).exclude(
            name__endswith='_brand'
        ).exclude(
            name__endswith='_model'
        ).exclude(image='brands/default.jpg')
        
        for category in categories:
            category_id = str(category.id)
            brands[category_id] = []
            
            # Get brands that belong to the same category type and have '_brand' suffix
            category_brands = BrandImage.objects.filter(
                category=category.category,
                name__endswith='_brand'
            ).exclude(image='brands/default.jpg')
            
            for brand in category_brands:
                if brand.image:
                    brands[category_id].append({
                        'id': brand.id, 
                        'name': brand.name or 'Brand', 
                        'image': f'/media/{brand.image}'
                    })
        
        return JsonResponse({'brands': brands})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_model_images(request):
    try:
        # Get model images by category with IDs (including Super Admin categories)
        car_models = ModelImage.objects.filter(category__in=['car', 'group1']).exclude(image='models/default.jpg')
        bike_models = ModelImage.objects.filter(category__in=['bike', 'group2']).exclude(image='models/default.jpg')
        truck_models = ModelImage.objects.filter(category__in=['truck', 'group3']).exclude(image='models/default.jpg')
        
        model_images = {
            'car': [f'/media/{img.image}' for img in car_models if img.image],
            'bike': [f'/media/{img.image}' for img in bike_models if img.image],
            'truck': [f'/media/{img.image}' for img in truck_models if img.image]
        }
        
        model_ids = {
            'car': [img.id for img in car_models if img.image],
            'bike': [img.id for img in bike_models if img.image],
            'truck': [img.id for img in truck_models if img.image]
        }
        
        models = {
            'car': [{'id': model.id, 'name': model.name, 'image': f'/media/{model.image}'} for model in car_models if model.image],
            'bike': [{'id': model.id, 'name': model.name, 'image': f'/media/{model.image}'} for model in bike_models if model.image],
            'truck': [{'id': model.id, 'name': model.name, 'image': f'/media/{model.image}'} for model in truck_models if model.image]
        }
        
        return JsonResponse({'images': model_images, 'ids': model_ids, 'models': models})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def delete_brand_image(request, image_id):
    if request.method == 'POST':
        try:
            brand_image = BrandImage.objects.get(id=image_id)
            brand_image.delete()
            
            # Also delete related vehicles that use this brand
            Vehicle.objects.filter(brand_name=brand_image.name).delete()
            
            return JsonResponse({'success': True})
        except BrandImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_model_image(request, image_id):
    if request.method == 'POST':
        try:
            model_image = ModelImage.objects.get(id=image_id)
            model_image.delete()
            return JsonResponse({'success': True})
        except ModelImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_models_for_brand(request, brand_name):
    models_data = []
    try:
        from .models import AdminModel, AdminBrand
        brand_name = str(brand_name)
        models = AdminModel.objects.filter(brand__name__iexact=brand_name)
        for model in models:
            if model.image:
                models_data.append({
                    'id': str(model.id), 
                    'name': str(model.name), 
                    'image': '/media/' + str(model.image)
                })
    except:
        pass
    return JsonResponse({'models': models_data})

def get_state_admin_vehicle_status(request):
    """Get vehicle approval status for state admin - only their own vehicles"""
    try:
        # Only show vehicles added by state_admin
        vehicles = Vehicle.objects.filter(added_by='state_admin').order_by('-id')
        
        vehicles_data = []
        for vehicle in vehicles:
            vehicles_data.append({
                'id': vehicle.id,
                'category_name': vehicle.category_name,
                'brand_name': vehicle.brand_name,
                'model_name': vehicle.model_name,
                'year': vehicle.year,
                'state': vehicle.state,
                'price': str(vehicle.price),
                'pricing_type': vehicle.pricing_type,
                'approval_status': vehicle.approval_status,
                'available': vehicle.available,
                'created_at': str(vehicle.id)
            })
        
        return JsonResponse({'vehicles': vehicles_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def super_admin_logout(request):
    request.session.pop('super_admin_logged_in', None)
    request.session.pop('super_admin_phone', None)
    return redirect('/super-admin-login/')

@csrf_exempt
def update_profile(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({'success': False, 'error': 'Not authenticated'})
            
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            
            # Update User model
            user.first_name = request.POST.get('name', '').strip()
            user.save()
            
            # Update UserProfile model
            phone = request.POST.get('phone', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            
            if phone:
                user_profile.phone = phone
                request.session['phone'] = phone  # Update session
            if pincode:
                user_profile.pincode = pincode
            
            user_profile.save()
            
            return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User profile not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def super_admin_categories(request):
    if not request.session.get('super_admin_logged_in'):
        return redirect('/super-admin-login/')
    return render(request, 'super_admin_categories.html')

@csrf_exempt
def set_promotion_prices(request):
    if request.method == 'POST':
        try:
            if not request.session.get('super_admin_logged_in'):
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            promote_price = float(request.POST.get('promote_price', 50))
            sponsor_price = float(request.POST.get('sponsor_price', 100))
            
            settings, created = PromotionSettings.objects.get_or_create(id=1)
            settings.promote_price_per_day = promote_price
            settings.sponsor_price_per_day = sponsor_price
            settings.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def get_promotion_prices(request):
    try:
        settings = PromotionSettings.objects.first()
        if settings:
            return JsonResponse({
                'promote_price': str(settings.promote_price_per_day),
                'sponsor_price': str(settings.sponsor_price_per_day)
            })
        return JsonResponse({'promote_price': '50', 'sponsor_price': '100'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def promote_vehicle(request, vehicle_id):
    if request.method == 'POST':
        try:
            user_phone = request.session.get('phone')
            if not user_phone:
                return JsonResponse({'success': False, 'error': 'Not authenticated'})
            
            vehicle = Vehicle.objects.get(id=vehicle_id, seller_phone=user_phone)
            days = int(request.POST.get('days', 1))
            promotion_type = request.POST.get('type', 'promote')
            
            settings = PromotionSettings.objects.first()
            if not settings:
                settings = PromotionSettings.objects.create()
            
            if promotion_type == 'promote':
                amount = settings.promote_price_per_day * days
            else:
                amount = settings.sponsor_price_per_day * days
            
            VehiclePromotion.objects.create(
                vehicle=vehicle,
                promotion_type=promotion_type,
                days=days,
                amount_paid=amount
            )
            
            return JsonResponse({
                'success': True, 
                'amount': str(amount),
                'message': f'Vehicle {promotion_type}d for {days} days - ₹{amount}'
            })
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def add_category_api(request):
    if request.method == 'POST':
        try:
            if not request.session.get('super_admin_logged_in'):
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            from .models import Category
            
            category_type = request.POST.get('category_type')
            category_name = request.POST.get('category_name')
            
            # Check if category name already exists for this type
            if Category.objects.filter(type=category_type, name=category_name).exists():
                return JsonResponse({'success': False, 'error': 'This category name already exists for this type'})
            
            if 'category_image' in request.FILES:
                Category.objects.create(
                    type=category_type,
                    name=category_name,
                    image=request.FILES['category_image']
                )
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Image is required'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_categories_api(request):
    try:
        import os
        from django.conf import settings
        from .models import Category
        
        categories = Category.objects.all().order_by('type', 'name')
        
        categories_data = []
        for cat in categories:
            if cat.image:
                image_path = os.path.join(settings.MEDIA_ROOT, str(cat.image))
                if os.path.exists(image_path):
                    categories_data.append({
                        'id': cat.id,
                        'type': cat.type,
                        'name': cat.name,
                        'image': f'/media/{cat.image}'
                    })
        
        return JsonResponse({'categories': categories_data})
    except Exception as e:
        return JsonResponse({'categories': []}, status=200)

@csrf_exempt
def delete_category_api(request, category_id):
    if request.method == 'POST':
        try:
            if not request.session.get('super_admin_logged_in'):
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            from .models import Category
            category = Category.objects.get(id=category_id)
            category.delete()
            return JsonResponse({'success': True})
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Category not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def edit_category_api(request, category_id):
    if request.method == 'POST':
        try:
            if not request.session.get('super_admin_logged_in'):
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            from .models import Category
            category = Category.objects.get(id=category_id)
            new_name = request.POST.get('category_name')
            
            # Check if new name already exists for this type
            if Category.objects.filter(type=category.type, name=new_name).exclude(id=category_id).exists():
                return JsonResponse({'success': False, 'error': 'This category name already exists for this type'})
            
            category.name = new_name
            category.save()
            return JsonResponse({'success': True})
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Category not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def add_brands_models_form(request):
    if not request.session.get('super_admin_logged_in'):
        return redirect('/super-admin-login/')
    return render(request, 'add_brands_models_form.html')

def add_model_to_brand(request):
    if not request.session.get('super_admin_logged_in'):
        return redirect('/super-admin-login/')
    return render(request, 'add_model_to_brand.html')

@csrf_exempt
def add_brands_models_api(request):
    if request.method == 'POST':
        try:
            if not request.session.get('super_admin_logged_in'):
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            from .models import Category
            
            category_id = request.POST.get('category_id')
            brand_name = request.POST.get('brand_name', '').strip()
            model_name = request.POST.get('model_name', '').strip()
            
            # Get the category instance
            try:
                category_instance = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Category not found'})
            
            brand_instance = None
            
            # Handle brand images - create brand linked to specific category
            if 'brand_images' in request.FILES:
                for img in request.FILES.getlist('brand_images'):
                    brand_instance = BrandImage.objects.create(
                        category_ref=category_instance,
                        name=brand_name,
                        image=img
                    )
                    break  # Use the first brand created for linking models
            
            # Handle model images - link to the specific brand instance
            if 'model_images' in request.FILES and brand_instance:
                for img in request.FILES.getlist('model_images'):
                    ModelImage.objects.create(
                        name=model_name,
                        brand=brand_instance,
                        image=img
                    )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def add_model_to_brand_api(request):
    if request.method == 'POST':
        try:
            if not request.session.get('super_admin_logged_in'):
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            brand_id = request.POST.get('brand_id')
            model_name = request.POST.get('model_name', '').strip()
            
            # Get the brand instance
            try:
                brand_instance = BrandImage.objects.get(id=brand_id)
            except BrandImage.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Brand not found'})
            
            # Handle model images - link to the specific brand instance
            if 'model_images' in request.FILES:
                for img in request.FILES.getlist('model_images'):
                    ModelImage.objects.create(
                        name=model_name,
                        brand=brand_instance,
                        image=img
                    )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_brands_for_category(request, category_name):
    brands_data = []
    try:
        from .models import AdminBrand, AdminCategory
        category_name = str(category_name)
        brands = AdminBrand.objects.filter(category__name__iexact=category_name)
        for brand in brands:
            if brand.image:
                brands_data.append({
                    'id': str(brand.id),
                    'name': str(brand.name),
                    'image': '/media/' + str(brand.image)
                })
    except:
        pass
    return JsonResponse({'brands': brands_data})

@csrf_exempt
def get_user_profile_api(request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
        
        return JsonResponse({
            'success': True,
            'name': f"{user.first_name}".strip() or 'Not Available',
            'phone': user_profile.phone or 'Not Available',
            'pincode': user_profile.pincode or 'Not Available',
            'unique_id': user_profile.unique_id or 'Not Available'
        })
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'User profile not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def save_admin_data(request):
    if request.method == 'POST':
        try:
            from .models import AdminGroup, AdminCategory, AdminBrand, AdminModel
            
            data_type = request.POST.get('type')
            name = request.POST.get('name')
            image = request.FILES.get('image')
            group_name = request.POST.get('group_name', '')
            category_name = request.POST.get('category_name', '')
            brand_name = request.POST.get('brand_name', '')
            
            if data_type == 'group':
                # Check if group already exists
                if AdminGroup.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'error': 'Group name already exists'})
                AdminGroup.objects.get_or_create(name=name)
                return JsonResponse({'success': True})
                
            elif data_type == 'category':
                group, created = AdminGroup.objects.get_or_create(name=group_name)
                AdminCategory.objects.create(
                    name=name,
                    image=image,
                    group=group
                )
                return JsonResponse({'success': True})
                
            elif data_type == 'brand':
                group = AdminGroup.objects.get(name=group_name)
                category = AdminCategory.objects.get(name=category_name, group=group)
                AdminBrand.objects.create(
                    name=name,
                    image=image,
                    category=category
                )
                return JsonResponse({'success': True})
                
            elif data_type == 'model':
                group = AdminGroup.objects.get(name=group_name)
                category = AdminCategory.objects.get(name=category_name, group=group)
                brand = AdminBrand.objects.get(name=brand_name, category=category)
                AdminModel.objects.create(
                    name=name,
                    image=image,
                    brand=brand
                )
                return JsonResponse({'success': True})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def get_admin_groups(request):
    try:
        from .models import AdminGroup
        groups = AdminGroup.objects.all().values_list('name', flat=True)
        return JsonResponse({'success': True, 'groups': list(groups)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_all_admin_data(request):
    try:
        from .models import AdminGroup, AdminCategory, AdminBrand, AdminModel
        
        # Get all groups first
        all_groups = AdminGroup.objects.all()
        
        categories = {}
        for group in all_groups:
            categories[group.name] = []
            # Get categories for this group
            group_categories = AdminCategory.objects.filter(group=group)
            for category in group_categories:
                categories[group.name].append({
                    'name': category.name,
                    'image': f'/media/{category.image}' if category.image else ''
                })
        
        brands = {}
        for brand in AdminBrand.objects.all():
            key = f"{brand.category.group.name}_{brand.category.name}"
            if key not in brands:
                brands[key] = []
            brands[key].append({
                'name': brand.name,
                'image': f'/media/{brand.image}' if brand.image else ''
            })
        
        models = {}
        for model in AdminModel.objects.all():
            key = f"{model.brand.category.group.name}_{model.brand.category.name}_{model.brand.name}"
            if key not in models:
                models[key] = []
            models[key].append({
                'name': model.name,
                'image': f'/media/{model.image}' if model.image else ''
            })
        
        return JsonResponse({
            'success': True,
            'categories': categories,
            'brands': brands,
            'models': models
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def user_browse_categories(request):
    return render(request, 'user_browse_categories.html')

@csrf_exempt
def get_all_users_api(request):
    try:
        if not request.session.get('super_admin_logged_in'):
            return JsonResponse({'success': False, 'error': 'Unauthorized'})
        
        users = UserProfile.objects.all().order_by('-id')
        users_data = []
        
        for user_profile in users:
            user = user_profile.user
            users_data.append({
                'id': user.id,
                'name': f"{user.first_name}".strip() or 'Not provided',
                'phone': user_profile.phone or 'Not provided',
                'pincode': user_profile.pincode or 'Not provided',
                'unique_id': user_profile.unique_id or 'Not provided',
                'blocked': user_profile.blocked
            })
        
        return JsonResponse({'success': True, 'users': users_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
def seller_vehicles(request):
    return render(request, 'seller_vehicles.html')

@csrf_exempt
def get_user_details_api(request, user_id):
    try:
        if not request.session.get('super_admin_logged_in'):
            return JsonResponse({'success': False, 'error': 'Unauthorized'})
        
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
        
        # Get user's vehicles (seller vehicles)
        vehicles = Vehicle.objects.filter(seller_phone=user_profile.phone, added_by='seller').order_by('-id')
        vehicles_data = []
        
        for vehicle in vehicles:
            vehicle_images = [f'/media/{img.image}' for img in vehicle.images.all()]
            vehicles_data.append({
                'id': vehicle.id,
                'category_name': vehicle.category_name,
                'brand_name': vehicle.brand_name,
                'model_name': vehicle.model_name,
                'year': vehicle.year,
                'price': str(vehicle.price),
                'pricing_type': vehicle.pricing_type,
                'available': vehicle.available,
                'approval_status': vehicle.approval_status,
                'pincode': vehicle.pincode or 'Not provided',
                'village': vehicle.village or 'Not provided',
                'owner_name': vehicle.owner_name or 'Not provided',
                'images': vehicle_images
            })
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'name': f"{user.first_name}".strip() or 'Not provided',
                'phone': user_profile.phone or 'Not provided',
                'pincode': user_profile.pincode or 'Not provided',
                'unique_id': user_profile.unique_id or 'Not provided'
            },
            'vehicles': vehicles_data
        })
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def block_user_vehicle(request, vehicle_id):
    if request.method == 'POST':
        try:
            if not request.session.get('super_admin_logged_in'):
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            vehicle = Vehicle.objects.get(id=vehicle_id)
            vehicle.available = False
            vehicle.save()
            return JsonResponse({'success': True, 'message': 'Vehicle blocked successfully'})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_user_vehicle(request, vehicle_id):
    if request.method == 'POST':
        try:
            if not request.session.get('super_admin_logged_in'):
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            vehicle = Vehicle.objects.get(id=vehicle_id)
            vehicle.delete()
            return JsonResponse({'success': True, 'message': 'Vehicle deleted successfully'})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def block_user(request, user_id):
    if request.method == 'POST':
        try:
            if not request.session.get('super_admin_logged_in'):
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            user_profile.blocked = not user_profile.blocked
            user_profile.save()
            
            action = 'blocked' if user_profile.blocked else 'unblocked'
            return JsonResponse({'success': True, 'blocked': user_profile.blocked, 'message': f'User {action} successfully'})
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})