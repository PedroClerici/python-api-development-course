from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()


# Creating a schema for request validation!
class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None
    id: int


my_posts = [
    {
        "title": "Top beaches in Florida!",
        "content": "The Florida state is...",
        "published": True,
        "rating": None,
        "id": 0,
    },
    {
        "title": "Favorite foods!",
        "content": "Cinnamon Rolls are awesome! But...",
        "published": True,
        "rating": 4,
        "id": 1,
    },
]


def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post


@app.get("/post")
def get_posts():
    return {"posts": my_posts}


@app.get("/post/latest")
def get_latest_post():
    return my_posts[-1]


@app.get("/post/{id}")
def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Post with id: {id} was not found"}
    return post


@app.post("/post", status_code=status.HTTP_201_CREATED)
def create_posts(payload: Post):
    post_dict = payload.dict()
    post_dict["id"] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}


@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    my_posts.remove(post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/post/{id}")
def update_post(payload: Post, id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
    updated_post = payload.dict()
    my_posts[my_posts.index(post)] = updated_post
    return {"data": find_post(updated_post["id"])}
