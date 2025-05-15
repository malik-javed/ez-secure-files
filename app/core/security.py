from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from . import config
import secrets
import base64
from cryptography.fernet import Fernet
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate a key for Fernet encryption
def get_encryption_key() -> bytes:
    # Use a consistent key derived from the SECRET_KEY
    key = hashlib.sha256(config.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)

# Initialize Fernet cipher
fernet = Fernet(get_encryption_key())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)

def encrypt_url(file_id: str, user_id: str) -> str:
    """Encrypt file ID and user ID to create a secure download URL"""
    data = f"{file_id}:{user_id}:{datetime.utcnow().timestamp()}"
    encrypted_data = fernet.encrypt(data.encode()).decode()
    return base64.urlsafe_b64encode(encrypted_data.encode()).decode()

def decrypt_url(encrypted_url: str) -> Dict[str, Any]:
    """Decrypt the URL to get file ID and authorized user ID"""
    try:
        decoded_url = base64.urlsafe_b64decode(encrypted_url.encode()).decode()
        decrypted_data = fernet.decrypt(decoded_url.encode()).decode()
        file_id, user_id, timestamp = decrypted_data.split(":")
        
        # Check if URL has expired (24 hours)
        url_time = datetime.fromtimestamp(float(timestamp))
        if datetime.utcnow() - url_time > timedelta(hours=24):
            return {"valid": False, "reason": "URL expired"}
            
        return {
            "valid": True,
            "file_id": file_id,
            "user_id": user_id
        }
    except Exception as e:
        return {"valid": False, "reason": str(e)} 