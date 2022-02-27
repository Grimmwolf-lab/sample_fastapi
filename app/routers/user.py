from ..schemas import UserOut, UserCreate
from sqlalchemy.orm import Session
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import  get_db
from ..utils import hash
from .. import models

router = APIRouter(
    prefix="/users" #automatically provides with the path.
)




@router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def create_user(user: UserCreate, db: Session=Depends(get_db)):
#hash the password -user.password

    hashed_password = hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict()) # do the same exact thing as the above commented code.
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/{id}', status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def get_user(id: int, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} not found!")
    return user
