from typing import  List, Optional

from click import get_current_context
from ..schemas import  PostCreate, Post, PostOut
from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from .. import models, oauth2
from sqlalchemy import func


router = APIRouter(
    prefix= "/posts",
    tags= ['Post']
)






@router.get("", response_model=List[PostOut])
def test_posts(db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user), limit: int=10, skip: int=0, search: Optional[str]=""):
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() #Here no sql query is needed, just python code.
    
    result = db.query(models.Post, func.count(models.Vote.posts_id).label("votes")).join(models.Vote, models.Vote.posts_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return result

# @app.get('/posts')
# async def post():
#     cursor.execute("""SELECT * FROM posts""") # As we can see without sqlachemy we had to write sql queries.
#     posts = cursor.fetchall()
#     print(posts)
#     return posts


@router.post('/create_post', status_code=status.HTTP_201_CREATED, response_model=Post)
async def create_pos(post: PostCreate, db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):
    #post_dict = post.dict()
    #post_dict['id'] = randrange(0, 100000)
    #my_post.append(post_dict)
    #return {'post': post_dict}
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    #print(**post.dict())
    ## Instead of the above sql commands we can simply use python code for creating posts.
    #new_post = models.Post(title = post.title, content = post.content, published = post.published)
    print(current_user.id)
    new_post = models.Post(owner_id=current_user.id, **post.dict()) # do the same exact thing as the above commented code.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get('/{id}', response_model=PostOut)
async def get_post(id:int, db: Session = Depends((get_db)), current_user: int= Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()
    #post_detail = find_post(id)
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.posts_id).label("votes")).join(models.Vote, models.Vote.posts_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail=f'Post with id:{id} not found')
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {'message': f'Post with id:{id} not found'}
    return post

@router.delete('/{id}')
async def delete_post(id: int, db: Session=Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):
    #deleting post
    #find the index in the array which has required ID
    #my_post.pop(id)
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id== id)
    post = deleted_post.first()
    #index = find_post_index(id)
    if post == None :
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id:{id} does not exists!')
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    #my_post.pop(index)
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{id}', response_model=Post)
async def update_post(id: int, pydantic_post: PostCreate, db: Session=Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    updated_post = db.query(models.Post).filter(models.Post.id == id)

    post = updated_post.first()
    

    #index = find_post_index(id)
    if post == None :
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id:{id} does not exists!')
     
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    updated_post.update(pydantic_post.dict(), synchronize_session=False)
    db.commit()
    #post_dict = post.dict()
    #post_dict['id'] = id
    #my_post[index]=post_dict
    return updated_post.first()