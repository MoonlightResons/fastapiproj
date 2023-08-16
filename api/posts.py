
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.models import Post, User
from core.database import get_db
from .schemas import PostCreate, PostUpdate, PostResponse, PostDelete
from .auth import get_current_user

router = APIRouter()


@router.get('/posts/', response_model=list[PostResponse], tags=['posts'])
def post_list(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts


@router.post('/posts/create', response_model=PostResponse, tags=['posts'])
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = Post(title=post.title, content=post.content, author_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get('/posts/{post_id}', response_model=PostResponse, tags=['posts'])
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    return post


@router.put('/posts/{post_id}', response_model=PostResponse, tags=['posts'])
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_post = db.query(Post).filter(Post.id == post_id, Post.author_id == current_user.id).first()

    if existing_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or you don't have permission to update it")

    existing_post.title = post.title
    existing_post.content = post.content
    db.commit()
    db.refresh(existing_post)
    return existing_post


@router.delete('/posts/{post_id}', response_model=PostResponse, tags=['posts'])
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_post = db.query(Post).filter(Post.id == post_id, Post.author_id == current_user.id).first()

    if existing_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or you don't have permission to delete it")

    db.delete(existing_post)
    db.commit()

    return existing_post
