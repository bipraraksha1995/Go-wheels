"""
Encryption module for GoWheels
Provides Fernet-based encryption for sensitive data at rest
"""

import os
from cryptography.fernet import Fernet, InvalidToken
from django.core.exceptions import ImproperlyConfigured


class Cipher:
    """
    Fernet cipher for encrypting/decrypting sensitive data
    Requires ENCRYPTION_KEY in environment (.env file)
    
    Generate key once:
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        print(key.decode())  # Add to .env as ENCRYPTION_KEY
    """
    
    def __init__(self):
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ImproperlyConfigured(
                "ENCRYPTION_KEY not set in environment. "
                "Generate with: from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())"
            )
        try:
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as e:
            raise ImproperlyConfigured(f"Invalid ENCRYPTION_KEY: {e}")
    
    def encrypt(self, plaintext):
        """
        Encrypt plaintext to ciphertext
        
        Args:
            plaintext (str): Plain text to encrypt
            
        Returns:
            str: Encrypted text (base64-encoded)
        """
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)
        
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt(self, ciphertext):
        """
        Decrypt ciphertext to plaintext
        
        Args:
            ciphertext (str): Encrypted text
            
        Returns:
            str: Decrypted plain text
        """
        if not isinstance(ciphertext, str):
            ciphertext = str(ciphertext)
        
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except InvalidToken:
            raise ValueError("Decryption failed: invalid token or corrupted data")
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")


def encrypt_field(plaintext):
    """Convenience function to encrypt a field"""
    cipher = Cipher()
    return cipher.encrypt(plaintext)


def decrypt_field(ciphertext):
    """Convenience function to decrypt a field"""
    cipher = Cipher()
    return cipher.decrypt(ciphertext)
