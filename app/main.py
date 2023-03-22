from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

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
def create_posts(payload: Post):
    cursor.execute(
        """
        INSERT INTO posts (title, content, published)
            VALUES (%s, %s, %s) RETURNING *
        """,
        (payload.title, payload.content, payload.published)
    )
    new_post = cursor.fetchone()
    connection.commit()
    return {"data": new_post}


@app.get("/post")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"posts": posts}


@app.get("/post/latest")
def get_latest_post():
    cursor.execute(
        """SELECT * FROM posts ORDER BY created_at DESC""",
        (id,)
    )
    post = cursor.fetchone()
    return post


@app.get("/post/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
    post = cursor.fetchone()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    return post


@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    post = cursor.fetchone()
    connection.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/post/{id}")
def update_post(payload: Post, id: int):
    cursor.execute(
        """
        UPDATE posts SET title = %s, content = %s, published = %s
            WHERE id = %s RETURNING *
        """,
        (payload.title, payload.content, payload.published, id)
    )
    post = cursor.fetchone()
    connection.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    return {"data": post}
