from fastapi import FastAPI
from . import models
from .database import engine
from .routes import post, user, auth, vote


# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
