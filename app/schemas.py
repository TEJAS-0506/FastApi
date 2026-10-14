from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from typing import Optional, Annotated


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    

class PostCreate(Post):
    pass


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    # class config:
    #     orm_mode = True


class PostRes(Post):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    
    model_config = ConfigDict(from_attributes=True)
    # class config:
    #     orm_mode = True
        


class PostOut(PostRes):
    # Post: Post
    votes: int
    
    model_config = ConfigDict(from_attributes=True)
    # class config:
    #     orm_mode = True   
    
    

class UserLogin(BaseModel):
    email : EmailStr
    password : str
    


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(ge=0, le=1)]
