from typing import List, Optional
from pydantic import BaseModel

# response schema of get all products ->ok
class Getallproducts(BaseModel):
    name : str
    amount : int
    price : int

    class Config():
        orm_mode = True

# input schema of fuzzy search
class Fuzzy(BaseModel):
    name : str

# input schema of add-to-cart
class Addtocart(BaseModel):
    name : str
    amount : int
    user_id : int

# response schema of add-to-cart
class Showorders(Addtocart):
    id: int
    price : int
    total : int
    
    class Config():
        orm_mode = True

# input schema of modification
class Modify(BaseModel):
    name : str
    amount : int

    class Config():
        orm_mode = True

# # input schema
# class BlogBase(BaseModel):
#     title: str
#     body: str

# # input schema
# class Blog(BlogBase):
#     class Config():
#         orm_mode = True

# input schema of new user registration ->ok
class User(BaseModel):
    name:str
    email:str
    password:str

# response schema of show user ->ok
class ShowUser(BaseModel):
    id:int
    name:str
    email:str
    orders : List[Showorders] =[]
    class Config():
        orm_mode = True

# # response schema
# class ShowBlog(BaseModel):
#     title: str
#     body:str
#     creator: ShowUser

#     class Config():
#         orm_mode = True

# # input schema
# class Login(BaseModel):
#     username: str
#     password:str

# ok
class Token(BaseModel):
    access_token: str
    token_type: str

# ok
class TokenData(BaseModel):
    email: Optional[str] = None
