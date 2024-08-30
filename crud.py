# crud.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy.orm import Session, joinedload


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        username=user.username, 
        full_name=user.full_name, 
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def update_user_profile(db: Session, user:schemas.User, user_profile: schemas.UserProfile):
    #user = db.query(models.UserProfile).filter(models.UserProfile.username == username).first()
    #if not user:
        #raise HTTPException(status_code=404, detail="User not found")
    
    # Update the user fields
    #user.username = user_profile.username
    user.email = user_profile.email
    user.height = user_profile.height
    user.weight = user_profile.weight
    user.age = user_profile.age

    db.commit()
    db.refresh(user)
    return user

def delete_username(db: Session, username: str):
    db.query(models.User).filter(models.User.username == username).delete()
    db.commit()


