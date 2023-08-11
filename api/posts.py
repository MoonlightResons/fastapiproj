from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from .schemas import PostCreate, UserProfile
from db.models import Post, User
from fastapi import Security
from .auth import get_current_user

router = APIRouter()


@router.post("/post/create", status_code=status.HTTP_201_CREATED, tags=['posts'])
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not registered")

    new_post = Post(title=post.title, content=post.content, author_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"status": "The create successfuly", "post": new_post}