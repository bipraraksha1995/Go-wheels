from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_vehicles(request):
    if request.method == 'GET':
        vehicles = Vehicle.objects.all().values()
        return JsonResponse({'vehicles': list(vehicles)})
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        vehicle = Vehicle.objects.create(**data)
        return JsonResponse({'success': True, 'id': vehicle.id})

@csrf_exempt
def api_user_profile(request, user_id):
    try:
        profile = UserProfile.objects.get(user_id=user_id)
        return JsonResponse({
            'name': profile.name,
            'phone': profile.phone,
            'pincode': profile.pincode
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)