from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Annotated

from . import schemas, models
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Secret key
# Algorithm
# Expiration time

# To get a string like this run:
# $ openssl rand -hex 32
SECRET_KEY = "0df03c6088f51940e6d5e2642e3d206a75b7968b064f166a4da36f4ed6d48e59"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire_time})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: Annotated[str, Depends(oauth2_scheme)],
                        credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if not id:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(token: schemas.Token = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token=token,
                                credentials_exception=credentials_exception)

    user = db.query(models.User)\
        .filter(models.User.id == token.id)\
        .first()

    if not user:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {token.id} not found.")

    return user
