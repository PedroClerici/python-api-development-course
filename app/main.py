from fastapi import FastAPI, Depends, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
import time

from . import models
from .database import engine, get_db

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Creating a schema for request validation!
class Post(BaseModel):
    title: str
    content: str
    published: bool = False


while True:
    try:
        connection = psycopg2.connect(
            host='localhost',
            database='fastapi',
            user='postgres',
            cursor_factory=RealDictCursor
        )
        cursor = connection.cursor()
        print('Connection with the database was successful!')
        break
    except Exception as error:
        print("Connection to database fail!")
        print("Error:", error)
        time.sleep(3)


@app.post("/post", status_code=status.HTTP_201_CREATED)
def create_posts(payload: Post, db: Session = Depends(get_db)):
    # Create a new post based on the model
    new_post = models.Post(title=payload.title, content=payload.content,
                           published=payload.published)
    # You can also create a post model by just unpacking the payload:
    # new_post = models.Post(**payload)

    # Add the new post to the database
    db.add(new_post)
    # Commits changes to the database
    db.commit()
    # Retrieves the new post created from the database
    db.refresh(new_post)

    return {"data": new_post}


@app.get("/post")
def get_posts(db: Session = Depends(get_db)):
    # Gets every post from the posts table
    posts = db.query(models.Post).all()
    return {"posts": posts}


@app.get("/post/latest")
def get_latest_post(db: Session = Depends(get_db)):
    latest_post = db.query(models.Post)\
        .order_by(models.Post.published.desc())\
        .first()
    if not latest_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    return {"post": latest_post}


@app.get("/post/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).one()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    return {"post": post}


@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    is_deleted = db.query(models.Post).filter(models.Post.id == id).delete()
    db.commit()
    if not is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/post/{id}")
def update_post(payload: Post, id: int, db: Session = Depends(get_db)):
    updated_post = db.query(models.Post).filter(models.Post.id == id)\
            .update(**payload.dict(), synchronize_session="evaluate")
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    return {"data": update_post}
