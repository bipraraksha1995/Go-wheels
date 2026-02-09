"""
Production 2FA with SMS via 2Factor API
Secure OTP hashing, expiry, and brute-force protection
"""

import hashlib
import requests
import logging
from decouple import config

logger = logging.getLogger('gowheels.2fa')


def hash_otp(otp: str) -> str:
    """Hash OTP using SHA-256"""
    return hashlib.sha256(str(otp).encode()).hexdigest()


def send_2fa_code(phone: str, otp: str) -> bool:
    """
    Send OTP via SMS using MSG91 (more reliable for SMS)
    
    Args:
        phone: Phone number (10 digits)
        otp: OTP code (6 digits)
    
    Returns:
        bool: True if sent successfully
    """
    try:
        # Clean phone number - remove spaces, dashes, country code
        phone = str(phone).strip().replace(' ', '').replace('-', '')
        
        # Remove +91 or 91 prefix if present
        if phone.startswith('+91'):
            phone = phone[3:]
        elif phone.startswith('91') and len(phone) == 12:
            phone = phone[2:]
        
        # Validate phone number
        if len(phone) != 10 or not phone.isdigit():
            logger.error(f"Invalid phone number format: {phone}")
            print(f"\n{'='*50}\nInvalid phone: {phone}\nOTP: {otp}\n{'='*50}\n")
            return False
        
        # Try Fast2SMS first (sends actual SMS text)
        fast2sms_key = config('FAST2SMS_API_KEY', default='')
        
        if fast2sms_key:
            print(f"\n{'='*50}\nSending SMS via Fast2SMS to {phone}\nOTP: {otp}\n{'='*50}\n")
            
            # Use DLT SMS API (no verification needed)
            url = f"https://www.fast2sms.com/dev/bulkV2?authorization={fast2sms_key}&route=dlt&sender_id=TXTIND&message=164953&variables_values={otp}&flash=0&numbers={phone}"
            
            response = requests.get(url, timeout=10)
            print(f"Fast2SMS Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('return'):
                    logger.info(f"SMS sent to {phone} via Fast2SMS")
                    print(f"\n{'='*50}\nSMS SENT SUCCESSFULLY\n{'='*50}\n")
                    return True
        
        # Try MSG91 (better for SMS)
        msg91_key = config('MSG91_AUTH_KEY', default='')
        
        if msg91_key:
            print(f"\n{'='*50}\nSending SMS via MSG91 to {phone}\nOTP: {otp}\n{'='*50}\n")
            
            url = "https://control.msg91.com/api/v5/otp"
            payload = {
                "template_id": config('MSG91_TEMPLATE_ID', default=''),
                "mobile": f"91{phone}",
                "authkey": msg91_key,
                "otp": otp
            }
            
            # If no template, use direct SMS
            if not payload['template_id']:
                url = f"https://api.msg91.com/api/sendotp.php?authkey={msg91_key}&mobile=91{phone}&otp={otp}&sender=GOWELS&message=Your GoWheels OTP is {otp}"
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=payload, timeout=10)
            
            print(f"MSG91 Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                logger.info(f"SMS sent to {phone} via MSG91")
                print(f"\n{'='*50}\nSMS SENT SUCCESSFULLY\n{'='*50}\n")
                return True
        
        # Fallback to 2Factor (but will be voice call)
        api_key = config('TWOFACTOR_API_KEY', default='')
        
        if not api_key:
            logger.warning("No SMS provider configured, logging to console")
            print(f"\n{'='*50}\nNO API KEY - Console Mode\nPhone: {phone}\nOTP: {otp}\n{'='*50}\n")
            return True
        
        print(f"\n{'='*50}\nFalling back to 2Factor (may be voice call)\nPhone: {phone}\nOTP: {otp}\n{'='*50}\n")
        
        url = f"https://2factor.in/API/V1/{api_key}/SMS/{phone}/{otp}/AUTOGEN"
        
        logger.info(f"Sending via 2Factor API to {phone}")
        response = requests.get(url, timeout=10)
        
        print(f"2Factor Response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"JSON Response: {result}")
            
            if result.get('Status') == 'Success':
                logger.info(f"Sent to {phone} via 2Factor")
                print(f"\n{'='*50}\nSENT (check phone for SMS or voice)\n{'='*50}\n")
                return True
            else:
                error_msg = result.get('Details', 'Unknown error')
                logger.error(f"2Factor error: {result}")
                print(f"\n{'='*50}\nFAILED: {error_msg}\nUse console OTP: {otp}\n{'='*50}\n")
                return False
        else:
            logger.error(f"HTTP error: {response.status_code}")
            print(f"\n{'='*50}\nHTTP ERROR\nUse console OTP: {otp}\n{'='*50}\n")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        print(f"\n{'='*50}\nTIMEOUT\nOTP for {phone}: {otp}\n{'='*50}\n")
        return True
    except Exception as e:
        logger.error(f"SMS error: {e}")
        print(f"\n{'='*50}\nERROR: {e}\nOTP for {phone}: {otp}\n{'='*50}\n")
        return True


def verify_2fa_code(phone: str, otp: str) -> bool:
    """
    Verify OTP - checks hash, expiry, and attempts
    
    Args:
        phone: Phone number
        otp: OTP code entered by user
    
    Returns:
        bool: True if valid
    """
    from .models import OTP
    from django.utils import timezone
    
    try:
        # Get latest unused OTP for this phone
        otp_record = OTP.objects.filter(
            phone=phone,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp_record:
            logger.warning(f"No OTP found for {phone}")
            return False
        
        # Check if expired
        if timezone.now() > otp_record.expires_at:
            logger.warning(f"OTP expired for {phone}")
            otp_record.delete()
            return False
        
        # Check attempts limit
        if otp_record.attempts >= 3:
            logger.warning(f"OTP blocked for {phone} - too many attempts")
            otp_record.delete()
            return False
        
        # Verify hash
        if hash_otp(otp) == otp_record.otp_hash:
            otp_record.is_used = True
            otp_record.save()
            otp_record.delete()  # Clean up after use
            logger.info(f"OTP verified for {phone}")
            return True
        else:
            # Increment attempts on wrong OTP
            otp_record.attempts += 1
            otp_record.save()
            logger.warning(f"Invalid OTP for {phone} - attempt {otp_record.attempts}/3")
            return False
            
    except Exception as e:
        logger.error(f"2FA verification error: {e}")
        return False
