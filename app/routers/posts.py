from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
    PostsResponse,
)

from app.services import posts as post_service

router = APIRouter(tags=["posts"])


@router.post("/posts", response_model=PostResponse, status_code=201)
def create_post(data: PostCreate, db: Session = Depends(get_db)):
    return post_service.create_post(db, data)


@router.get("/posts", response_model=PostsResponse)
def get_posts(db: Session = Depends(get_db)):
    return {"result": post_service.list_posts(db)}


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = post_service.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.patch("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    post = post_service.update_post(db, post_id, data)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    if not post_service.delete_post(db, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return None
