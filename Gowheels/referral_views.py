from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Referral, UserProfile
import json
import random
import string

def generate_referral_code():
    """Generate unique 6-character referral code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Referral.objects.filter(referral_code=code).exists():
            return code

def referral_page(request):
    """Show referral dashboard"""
    phone = request.session.get('phone')
    if not phone:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    # Get or create referral code
    referral = Referral.objects.filter(referrer_phone=phone, referred_phone='').first()
    if not referral:
        referral = Referral.objects.create(
            referrer_phone=phone,
            referral_code=generate_referral_code()
        )
    
    # Get referrals made by this user
    referrals = Referral.objects.filter(referrer_phone=phone).exclude(referred_phone='')
    total_rewards = sum(r.reward_amount for r in referrals)
    
    return render(request, 'referral.html', {
        'referral_code': referral.referral_code,
        'total_referrals': referrals.count(),
        'total_rewards': total_rewards,
        'referrals': referrals
    })

@csrf_exempt
def apply_referral(request):
    """Apply referral code during registration"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    data = json.loads(request.body)
    phone = data.get('phone')
    code = data.get('code', '').upper()
    
    if not phone or not code:
        return JsonResponse({'error': 'Phone and code required'}, status=400)
    
    # Check if code exists
    referral = Referral.objects.filter(referral_code=code, referred_phone='').first()
    if not referral:
        return JsonResponse({'error': 'Invalid referral code'}, status=400)
    
    # Check if user already used a referral
    if Referral.objects.filter(referred_phone=phone).exists():
        return JsonResponse({'error': 'Already used a referral code'}, status=400)
    
    # Create new referral entry for the referred user
    Referral.objects.create(
        referrer_phone=referral.referrer_phone,
        referral_code=generate_referral_code(),
        referred_phone=phone,
        reward_amount=50  # ₹50 reward
    )
    
    return JsonResponse({'success': True, 'reward': 50})

@csrf_exempt
def get_referral_stats(request):
    """Get referral statistics"""
    phone = request.session.get('phone')
    if not phone:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    referrals = Referral.objects.filter(referrer_phone=phone).exclude(referred_phone='')
    total_rewards = sum(r.reward_amount for r in referrals)
    
    return JsonResponse({
        'total_referrals': referrals.count(),
        'total_rewards': float(total_rewards),
        'referrals': [{
            'phone': r.referred_phone,
            'reward': float(r.reward_amount),
            'date': r.created_at.strftime('%Y-%m-%d')
        } for r in referrals]
    })
