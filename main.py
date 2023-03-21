from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


# Creating a schema for request validation!
class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None


# Handling get requests
@app.get("/")
def root():
    return {"message": "Hello, world!"}


# Handling post requests
@app.post("/")
def get_post(payload: dict = Body(...)):
    print(payload)
    return {key: value for key, value in payload.items()}


@app.post("/post")
def create_post(payload: Post):
    print(payload)
    # Converting a pydantic model to a dict and returning it
    return payload.dict()
