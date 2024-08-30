# main.py
from fastapi import FastAPI, Depends, HTTPException, Response, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import pwd_context, authenticate_user, create_access_token, get_current_user
from typing import List, Optional
from database import engine, Base, get_db
import crud, models, schemas, auth
from loguru import logger
#from logger import get_logger


#logger = get_logger(__name__)


logger.add("app.log", rotation="500 MB", level="DEBUG")

Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI() 

@app.get("/")
def read_root():
        return {"message":"WELCOME TO MY APP OF MOVIES"}


@app.post("/Registration", response_model=schemas.User, status_code =status.HTTP_201_CREATED, tags= ["User"])

def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    This Session is for user Registration, fill your details below to signup
    """
    logger.info("creating user.....")
    db_user = crud.get_user_by_username(db, username=user.username)
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    hashed_password = pwd_context.hash(user.password)
    if db_user:
        logger.warning(f"user trying to register but username entered already exist: {user.username}")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if db_user_by_email:
        logger.error(f"User trying to register but email entered already exists: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    logger.info("user successfully created")
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)
    

@app.post("/login", status_code =status.HTTP_201_CREATED, tags=["User"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    This Session is for user to login and generate a token that expires in 30mins time
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.error(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credential ",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"user authorisation successfull for {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.patch("/users/{username}",  tags=["User"])
async def update_user_profile(username: str, user_profile: schemas.UserProfile = Body(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    # This will raise a ValueError if any of the fields are invalid
    user_profile = schemas.UserProfile(**user_profile.dict())  # Ensuring Pydantic validation is triggered

    return crud.update_user_profile(db, current_user, user_profile)
