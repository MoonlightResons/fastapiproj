import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from db.models import User, Post
from core.database import get_db
from .schemas import UserRegistration, UserLogin, UserProfile, PostResponse, UserWithPosts
from core.security import verify_password, create_access_token, decode_access_token, get_password_hash


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


EMAIL_HUNTER_API_KEY = 'fb79abfb32d8042d0b5273e47d2a5fbe3f4091f4'
EMAIL_HUNTER_URL = 'https://api.emailhunter.co/v2/email-verifier'


def verify_email(email):
    params = {
        'email': email,
        'api_key': EMAIL_HUNTER_API_KEY
    }

    response = requests.get(EMAIL_HUNTER_URL, params=params)
    data = response.json()

    if 'data' in data and 'status' in data['data']:
        status = data['data']['status']
        if status == 'valid':
            return True
        else:
            return False
    else:
        return False


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    decoded_token = decode_access_token(token)
    if decoded_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication token',
            headers={"WWW-Authenticate": "Bearer"}
        )
    user_id = decoded_token.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication token',
            headers={"WWW-Authenticate": "Bearer"}
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found',
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


@router.post('/auth/register/', response_model=UserProfile, tags=['auth'])
def register(user: UserRegistration, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already taken')

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already taken')

    if not verify_email(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid email address')

    new_user = User(username=user.username, email=user.email, fullname=user.fullname)
    new_user.password = get_password_hash(user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post('/auth/login', tags=['auth'])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    access_token = create_access_token(user.id)
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.get('/auth/profile/{user_id}', response_model=UserWithPosts, tags=['auth'])
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user_info = db.query(User).get(user_id)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    user_posts = [
        PostResponse(
            id=post.id, title=post.title, content=post.content, author=user_info
        )
        for post in user_info.posts
    ]

    user_with_posts = UserWithPosts(user_profile=user_info, user_posts=user_posts)
    return user_with_posts


@router.get('/auth/current_user', response_model=UserWithPosts, tags=['auth'])
def get_logged_in_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_posts = [
        PostResponse(
            id=post.id, title=post.title, content=post.content, author=current_user
        )
        for post in current_user.posts
    ]

    user_with_posts = UserWithPosts(user_profile=current_user, user_posts=user_posts)
    return user_with_posts