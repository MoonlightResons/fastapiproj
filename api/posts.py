
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.models import Post, User
from core.database import get_db
from .schemas import PostCreate, PostUpdate, PostResponse, LikedPostResponse
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


@router.post('/posts/{post_id}/like', tags=['post_likes'])
def like_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    if current_user.id == post.author.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You cannot like your own post')
    if current_user in post.liked_by:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post already liked")
    post.liked_by.append(current_user)
    db.commit()
    return {"message": "Post liked"}


@router.post('/posts/{post_id}/dislike', tags=['post_likes'])
def dislike_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    if current_user.id == post.author.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You cannot dislike your own post')
    if not post.liked_by:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There are no likes on this post to dislike")
    if current_user not in post.liked_by:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only dislike a post that you have liked")

    post.liked_by.remove(current_user)
    db.commit()
    return {"message": "Post disliked"}


@router.get('/liked-posts', response_model=LikedPostResponse, tags=['post_likes'])
def liked_posts(current_user: User = Depends(get_current_user)):
    liked_posts = current_user.liked_posts
    return {'liked_posts': liked_posts}


@router.post('/posts/{posts_id}/favorite', tags=['favorite_post'])
def favorite_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    if current_user in post.liked_by:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post already favorited")
    post.favorited_by.append(current_user)
    db.commit()
    return {"message": "Post Favorited"}


@router.post('/posts/{post_id}/unfavorite', tags=['favorite_post'])
def unfavorite_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    if not post.favorited_by:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There are no favorite on this post to unfavorite")
    if current_user not in post.favorited_by:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only unfavorite a post that you have favorite")

    post.favorited_by.remove(current_user)
    db.commit()
    return {"message": "Post Unfavorited"}


@router.get('/favorite-posts', tags=['favorite_post'])
def favorite_posts(current_user: User = Depends(get_current_user)):
    favorite_posts = current_user.favorite_posts
    return {'favorite_posts': favorite_posts}

