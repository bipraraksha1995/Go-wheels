from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Chat, Message, Vehicle
import json

def inbox(request):
    """Show all chats for logged-in user"""
    phone = request.session.get('phone')
    if not phone:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    chats = Chat.objects.filter(Q(buyer_phone=phone) | Q(seller_phone=phone))
    
    chat_list = []
    for chat in chats:
        is_buyer = chat.buyer_phone == phone
        other_phone = chat.seller_phone if is_buyer else chat.buyer_phone
        
        chat_list.append({
            'id': chat.id,
            'vehicle_id': chat.vehicle.id,
            'vehicle_name': f"{chat.vehicle.brand_name} {chat.vehicle.model_name}",
            'other_phone': other_phone,
            'last_message': chat.last_message,
            'last_message_time': chat.last_message_time.strftime('%Y-%m-%d %H:%M'),
            'unread': chat.unread_buyer if is_buyer else chat.unread_seller
        })
    
    return render(request, 'inbox.html', {'chats': chat_list})

def chat_detail(request, chat_id):
    """Show messages in a chat"""
    phone = request.session.get('phone')
    if not phone:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Verify user is part of this chat
    if phone not in [chat.buyer_phone, chat.seller_phone]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Mark messages as read
    is_buyer = chat.buyer_phone == phone
    Message.objects.filter(chat=chat, is_read=False).exclude(sender_phone=phone).update(is_read=True)
    
    if is_buyer:
        chat.unread_buyer = 0
    else:
        chat.unread_seller = 0
    chat.save()
    
    messages = chat.messages.all()
    
    msg_list = [{
        'sender': msg.sender_phone,
        'message': msg.message,
        'time': msg.created_at.strftime('%H:%M'),
        'is_mine': msg.sender_phone == phone
    } for msg in messages]
    
    return render(request, 'chat.html', {
        'chat_id': chat_id,
        'vehicle_name': f"{chat.vehicle.brand_name} {chat.vehicle.model_name}",
        'other_phone': chat.seller_phone if is_buyer else chat.buyer_phone,
        'messages': msg_list
    })

@csrf_exempt
def send_message(request):
    """Send a message"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    phone = request.session.get('phone')
    if not phone:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    data = json.loads(request.body)
    chat_id = data.get('chat_id')
    message_text = data.get('message', '').strip()
    
    if not message_text:
        return JsonResponse({'error': 'Message required'}, status=400)
    
    if chat_id:
        # Existing chat
        chat = get_object_or_404(Chat, id=chat_id)
        if phone not in [chat.buyer_phone, chat.seller_phone]:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
    else:
        # New chat
        vehicle_id = data.get('vehicle_id')
        if not vehicle_id:
            return JsonResponse({'error': 'vehicle_id or chat_id required'}, status=400)
        
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        seller_phone = vehicle.get_seller_phone()
        
        chat, created = Chat.objects.get_or_create(
            vehicle=vehicle,
            buyer_phone=phone,
            defaults={'seller_phone': seller_phone}
        )
    
    # Create message
    Message.objects.create(
        chat=chat,
        sender_phone=phone,
        message=message_text
    )
    
    # Update chat
    chat.last_message = message_text
    if phone == chat.buyer_phone:
        chat.unread_seller += 1
    else:
        chat.unread_buyer += 1
    chat.save()
    
    return JsonResponse({'success': True, 'chat_id': chat.id})

@csrf_exempt
def get_messages(request, chat_id):
    """Get new messages (for polling)"""
    phone = request.session.get('phone')
    if not phone:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    chat = get_object_or_404(Chat, id=chat_id)
    
    if phone not in [chat.buyer_phone, chat.seller_phone]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    messages = chat.messages.all()
    
    msg_list = [{
        'sender': msg.sender_phone,
        'message': msg.message,
        'time': msg.created_at.strftime('%H:%M'),
        'is_mine': msg.sender_phone == phone
    } for msg in messages]
    
    return JsonResponse({'messages': msg_list})
