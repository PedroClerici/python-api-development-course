from fastapi import FastAPI
from fastapi.params import Body

app = FastAPI()


# Handling get requests
@app.get("/")
def root():
    return {"message": "Hello, world!"}


# Handling post requests
@app.post("/")
def create_post(body: dict = Body(...)):
    return {key: value for key, value in body.items()}
