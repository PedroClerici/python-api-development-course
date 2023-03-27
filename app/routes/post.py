from fastapi import Depends, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/post", tags=["Posts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_posts(payload: schemas.PostCreate, db: Session = Depends(get_db),
                 user: models.User = Depends(oauth2.get_current_user)):

    new_post = models.Post(owner_id=user.id, **payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # Gets every post from the posts table
    posts = db.query(models.Post).all()
    return posts


@router.get("/latest", response_model=schemas.Post)
def get_latest_post(db: Session = Depends(get_db)):
    post = db.query(models.Post)\
        .order_by(models.Post.published.desc())\
        .first()

    if not post:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} was not found")
    return post


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),
                user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")

    if post.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authorized to perform requested action")
    post_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(payload: schemas.PostUpdate, id: int,
                db: Session = Depends(get_db),
                user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_query.update(payload.dict())
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")

    if post.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authorized to perform requested action")

    db.commit()
    return post.first()
