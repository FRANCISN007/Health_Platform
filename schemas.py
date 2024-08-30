#schema.py
from pydantic import BaseModel, ConfigDict, validator


class UserProfile(BaseModel):
    #username: str
    email: str
    height:float
    weight:float
    age:int
 
    @validator('email')
    def email_must_be_valid(cls, v):
        if '@' not in v:
            raise ValueError('invalid email')
        return v
        
    @validator('height')
    def height_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Height must be a positive number')
        return v

    @validator('weight')
    def weight_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Weight must be a positive number')
        return v

    @validator('age')
    def age_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Age must be a positive number')
        return v

class UserBase(BaseModel):
    username: str
    full_name: str  
        
    
class UserCreate(UserBase):
    email: str
    password: str

class User(UserBase): 
    email: str
    id: int
    
    model_config = ConfigDict(from_attributes=True)    

#class UserCreate(BaseModel):
    #username: str
    #email: str
    #password: str

#class OAuth2PasswordRequestForm(BaseModel):
    #username: str
    #password: str
