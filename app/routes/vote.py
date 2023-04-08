from fastapi import Depends, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/vote", tags=["Vote"])

@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
def vote(payload: schemas.VoteCreate,
         db: Session = Depends(get_db),
         user: schemas.User = Depends(oauth2.get_current_user)):

     post = db.query(models.Post)\
          .filter(models.Post.id == payload.post_id)\
          .first()

     # Checks if post exists
     if not post:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail= f"Post with id of {payload.post_id} not found.")

     vote_query = db.query(models.Vote)\
          .filter(models.Vote.user_id == user.id,
                  models.Vote.post_id == payload.post_id)
           
     found_vote = vote_query.first()

     # If user wanna create a vote
     if payload.vote_dir == 1:
          if found_vote:
               raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                   detail= (f"User {user.id} has already voted "
                                            f"on post with id of {found_vote.post_id}."))
          
          db.add(models.Vote(post_id=payload.post_id, user_id=user.id))
          db.commit()

          return {"message": "successfully added vote."}
     
     # If user wanna remove a vote
     if payload.vote_dir == 0:
          if not found_vote:
               raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                   detail= (f"User with id of {user.id} has not voted "
                                            f"on post with id of {payload.post_id}."))

          vote_query.delete() 
          db.commit()

          return {"message": "successfully removed vote."}
