from django.utils import timezone
from datetime import timedelta
from gowheels.crypto_utils import generate_phone_otp
from gowheels.models import OTP


class OTPService:
    """
    Secure OTP generation and management service
    Uses cryptographically secure random generation
    """
    
    OTP_VALIDITY_MINUTES = 5  # OTP expires in 5 minutes
    
    def generate_otp(self):
        """Generate a secure 6-digit OTP using crypto_utils"""
        return generate_phone_otp()
    
    def send_otp(self, phone, otp=None):
        """
        Generate and send OTP to phone number
        Stores OTP in database with expiration time
        
        Args:
            phone (str): Phone number
            otp (str, optional): Pre-generated OTP. If None, generates new one.
            
        Returns:
            tuple: (success: bool, otp_token: str)
        """
        try:
            # Generate OTP if not provided
            if not otp:
                otp = self.generate_otp()
            
            # Calculate expiration time
            expires_at = timezone.now() + timedelta(minutes=self.OTP_VALIDITY_MINUTES)
            
            # Delete any existing OTPs for this phone (only keep latest)
            OTP.objects.filter(phone=phone).delete()
            
            # Create OTP record
            otp_record = OTP.objects.create(
                phone=phone,
                otp=otp,
                expires_at=expires_at
            )
            
            # Send SMS (demo mode - replace with Twilio/SNS in production)
            success, sid = self._send_sms(phone, otp)
            
            if success:
                return True, otp  # Return OTP for testing (remove in production)
            else:
                otp_record.delete()
                return False, None
                
        except Exception as e:
            print(f"Error sending OTP: {e}")
            return False, None
    
    def _send_sms(self, phone, otp):
        """
        Send SMS with OTP
        In production, integrate with Twilio, AWS SNS, or similar
        
        Args:
            phone (str): Phone number
            otp (str): OTP code
            
        Returns:
            tuple: (success: bool, message_id: str)
        """
        # Demo mode - replace with actual SMS service
        print(f"[SMS] To {phone}: Your GoWheels OTP is {otp}. Valid for {self.OTP_VALIDITY_MINUTES} minutes.")
        return True, "demo_sid"
    
    def verify_otp(self, phone, otp):
        """
        Verify OTP for a phone number
        Checks if OTP exists, matches, and hasn't expired
        
        Args:
            phone (str): Phone number
            otp (str): OTP to verify
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        try:
            # Find the most recent OTP for this phone
            otp_record = OTP.objects.filter(phone=phone).latest('created_at')
            
            # Check if OTP has expired
            if timezone.now() > otp_record.expires_at:
                return False, "OTP expired. Please request a new one."
            
            # Check if OTP matches
            if otp_record.otp != otp:
                return False, "Invalid OTP. Please try again."
            
            # OTP is valid - delete it (single-use)
            otp_record.delete()
            return True, "OTP verified successfully"
            
        except OTP.DoesNotExist:
            return False, "No OTP found for this phone. Request a new one."
        except Exception as e:
            return False, f"Error verifying OTP: {e}"
