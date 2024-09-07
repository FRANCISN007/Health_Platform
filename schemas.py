#schema.py
from pydantic import BaseModel, ConfigDict, validator


class UserProfile(BaseModel):
    username: str
    email: str
    full_name:str
    gender: str
    address:str
    country: str
    phone_no: str
    date_of_birth:str
 




class UserBase(BaseModel):
    username: str
    #full_name: str  
        
    
class UserCreate(UserBase):
    email: str
    password: str

class User(UserBase): 
    email: str
    id: int
 
class UserProfile_id(UserProfile):  
    email: str
    id: int

           
model_config = ConfigDict(from_attributes=True)   


class UserProfileWithID(BaseModel):
    id: int  # Include the user ID
    username: str
    email: str
    full_name: str
    gender: str
    address: str
    country: str
    phone_no: str
    date_of_birth: str

    class Config:
        orm_mode = True  # This ensures compatibility with SQLAlchemy models
 

#class UserCreate(BaseModel):
    #username: str
    #email: str
    #password: str

#class OAuth2PasswordRequestForm(BaseModel):
    #username: str
    #password: str
    

