from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from core.database import get_db
from db.models import User

SECRET_KEY = "asflregkerke;1241tfew"
ALGORIHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).get(username)
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authentificate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(user_id: int, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORIHM)
    return encoded_jwt


def decode_acccess_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORIHM])
        return decoded_token
    except JWTError:
        return None
