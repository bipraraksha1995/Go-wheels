from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Wishlist, Vehicle
import json

def wishlist_page(request):
    return render(request, 'wishlist.html')

def toggle_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_phone = request.session.get('phone')
        vehicle_id = data.get('vehicle_id')
        
        if not user_phone:
            return JsonResponse({'error': 'Not logged in'}, status=401)
        
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            wishlist_item = Wishlist.objects.filter(user_phone=user_phone, vehicle=vehicle).first()
            
            if wishlist_item:
                wishlist_item.delete()
                return JsonResponse({'success': True, 'action': 'removed'})
            else:
                Wishlist.objects.create(user_phone=user_phone, vehicle=vehicle)
                return JsonResponse({'success': True, 'action': 'added'})
        except Vehicle.DoesNotExist:
            return JsonResponse({'error': 'Vehicle not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_wishlist(request):
    user_phone = request.session.get('phone')
    if not user_phone:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    wishlists = Wishlist.objects.filter(user_phone=user_phone).select_related('vehicle')
    vehicles = []
    
    for w in wishlists:
        v = w.vehicle
        vehicles.append({
            'id': v.id,
            'brand_name': v.brand_name,
            'model_name': v.model_name,
            'year': v.year,
            'per_hour_price': str(v.per_hour_price),
            'per_day_price': str(v.per_day_price),
            'pincode': v.pincode,
            'village': v.village,
            'owner_name': v.get_owner_name(),
            'seller_phone': v.get_seller_phone(),
            'images': [img.image.url for img in v.images.all()],
        })
    
    return JsonResponse({'success': True, 'vehicles': vehicles})

def check_wishlist(request):
    user_phone = request.session.get('phone')
    if not user_phone:
        return JsonResponse({'wishlist_ids': []})
    
    wishlist_ids = list(Wishlist.objects.filter(user_phone=user_phone).values_list('vehicle_id', flat=True))
    return JsonResponse({'wishlist_ids': wishlist_ids})
