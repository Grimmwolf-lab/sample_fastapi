from app.routers.vote import vote
from . import models
from .routers import post, user, auth, vote
from fastapi import FastAPI
from .database import engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#all the domains who can request our api
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)





@app.get('/')
async def root():
    return {'message':'Hello World!'}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)





