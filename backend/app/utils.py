import hashlib
import hmac
import os
from datetime import datetime, timedelta
from jose import jwt

from app import config


def hash_password(password: str):
    salt = os.urandom(config.SALT_LENGTH)
    return salt + hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)


def check_password(password_hashed, password):
    salt = password_hashed[:config.SALT_LENGTH]
    pw = password_hashed[config.SALT_LENGTH:]
    return hmac.compare_digest(
        pw,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )


def create_token(data: dict, expires):
    d = data.copy()
    if expires:
        expire = datetime.utcnow() + expires
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    d.update({"exp": expire})
    return jwt.encode(d, config.SECRET_KEY, algorithm=config.TOKEN_ALGORITHM)
