from database import SessionLocal
import os
import datetime
from typing import Dict
from dotenv import load_dotenv
from jose import jwt
from jose.exceptions import JWTError
import random
import string
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
import uuid
from fastapi import status
import models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import datetime
from database import get_db
from cryptography.fernet import Fernet
import redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv('.env')

API_SECRET_KEY = os.getenv("API_SECRET_KEY")
API_SECRET_ALGORITHM = os.getenv("API_SECRET_ALGORITHM")
API_ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES")
FERNET_KEY = os.getenv("FERNET_KEY")


cipher_suite = Fernet(FERNET_KEY)

def validate_email(email: str):
    """
    Validate email address
    :param email: string email address
    """
    if not '@' in email:
        return False
    if not '.' in email:
        return False
    if email.count('@') > 1:
        return False
    if email.count(' ') > 0:
        return False
    return True

def serialize_datetime(obj): 
    """
    Serialize datetime object to string
    :param obj: datetime object
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif obj is None:
        return None
    raise TypeError("Type not serializable") 

def authenticate_user(account_name: str, password: str, db: Session = Depends(get_db)) -> bool:
    """
    Authenticate user
    :param account_name: string account name
    :param password: string password
    :param db: database session
    """
    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()
    password = user.salt+password
    password_check = pwd_context.verify(password, user.password)
    active_check = user.deleted_datetime is None
    if user and password_check and active_check:
        return True
    return False

def create_access_token(data: Dict[str, str], expires_delta: datetime.timedelta):
    """
    Create access token
    :param data: dictionary data
    :param expires_delta: datetime expiration
    """

    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, API_SECRET_KEY, algorithm=API_SECRET_ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=[API_SECRET_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
def salt_generator(size=12, chars=string.ascii_uppercase + string.digits)-> str:
    str_salt = ''.join(random.choice(chars) for _ in range(size))
    return str_salt

def generate_uuid4():
    """Generate a random UUID4 string."""
    return str(uuid.uuid4())

def encrypt_value(original_value: str):
    encrypted_value = cipher_suite.encrypt(original_value.encode())
    return encrypted_value

def decrypt_value(encrypted_value: str):
    decrypted_value = cipher_suite.decrypt(encrypted_value).decode()
    return decrypted_value

def write_pixel():
    pixel_path = "tracking_pixel.gif"
    if not os.path.exists(pixel_path):
        with open(pixel_path, "wb") as f:
            f.write(b"GIF89a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")

def get_redis_connection():
    redis_host = 'redis_service'
    redis_port = 6379
    redis_password = os.getenv("REDIS_PASSWORD")
    r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
    return r

def save_to_redis(key, value):
    r = get_redis_connection()
    r.set(key, value, ex=60*60)

def get_from_redis(key):
    r = get_redis_connection()
    value = r.get(key)
    return value