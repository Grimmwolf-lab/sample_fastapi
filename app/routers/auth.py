from tokenize import Token
from .. import utils, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserLogin, Token
from .. import models

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model = Token)
def login(user_credentials:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    #create a token
    # return token

    access_token = oauth2.create_access_token(data = {"user_id":user.id})
    return {"access_token": access_token, "token_type": "bearer"}