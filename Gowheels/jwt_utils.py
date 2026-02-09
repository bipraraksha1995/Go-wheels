"""JWT Token Manager - Minimal implementation"""
import jwt
import datetime
from django.conf import settings

class JWTTokenManager:
    @staticmethod
    def generate_token(user_id, expiry_hours=24):
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except:
            return None
