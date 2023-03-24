import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED

app = FastAPI()

# Secret key for JWT encoding and decoding
SECRET_KEY = "your_secret_key"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    password: str

# Dummy user data
users = [
    User(username="user1", password="password1"),
    User(username="user2", password="password2")
]

def create_jwt_token(data: dict):
    token = jwt.encode(data, SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

@app.post("/token")
async def login(user: User):
    if user not in users:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_jwt_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt_token(token)
    user = payload.get("sub")
    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user

@app.get("/users/me")
async def get_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}