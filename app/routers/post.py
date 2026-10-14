from fastapi  import FastAPI, Depends, HTTPException, status, Response, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/post",
    tags=['Posts']
)

# @router.get("/", response_model= List[schemas.PostRes])
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
            limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()   # to get only logged in user posts to himself
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    return [
        schemas.PostOut(
            **schemas.PostRes.model_validate(post).model_dump(),
            votes=votes
        )
        for post, votes in results
    ]
    
    
    # posts = []

    # for post, votes in results:
    #     posts.append({
    #         "id": post.id,
    #         "title": post.title,
    #         "content": post.content,
    #         "published": post.published,
    #         "created_at": post.created_at,
    #         "owner_id": post.owner_id,
    #         "owner": post.owner,
    #         "votes": votes,
    #     })
    
    # return results

    
# @router.get("/{id}", response_model= schemas.PostRes)
@router.get("/{id}", response_model= schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", str(id))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()  #This does not return vote count but below does, for that changed, response_model to PostOut from PostRes
    
    result = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post not found")
    
    # if post.owner_id != current_user.id:         #this ensures one particular user get his details of post only
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    
    # return post
    post, votes = result

    return schemas.PostOut(
        **schemas.PostRes.model_validate(
            post, from_attributes=True
        ).model_dump(),
        votes=votes
    )




@router.post("/", status_code= status.HTTP_201_CREATED, response_model= schemas.PostRes)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""" (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    # print(current_user.email)
    # print(current_user.id)
    new_post = models.Post(owner_id= current_user.id,**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.put("/{id}", response_model= schemas.PostRes)
def updated_post(id : int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published =%s, RETURNING *""", (post.title, post.content, post.published), str(id))    
    # updated_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    
    if updated_post == None:
        raise HTTPException(status_code = status.HTTP_204_NO_CONTENT, detail="No post found")
    
    if updated_post.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
        
    # post_query.update('title': 'hey, this is updated title', 'content': 'updated', synchronize_session=False)
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

@router.delete("/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="No post with {id} found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code= status.HTTP_204_NO_CONTENT)