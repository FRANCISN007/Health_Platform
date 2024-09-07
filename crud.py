# crud.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy.orm import Session, joinedload


#def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    #db_user = models.User(
        #username=user.username, 
        #full_name=user.full_name, 
        #email=user.email,
        #hashed_password=hashed_password
    #)
    #db.add(db_user)
    #db.commit()
    #db.refresh(db_user)
    #return db_user

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        username=user.username, 
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Automatically create a UserProfile when a new user is registered
    db_user_profile = models.UserProfile(
        user_id=db_user.id,  # Link to the user via user_id
        username=user.username,
        email=user.email,
        full_name="",  # Set default or blank values as appropriate
        gender="",
        address="",
        country="",
        phone_no="",
        date_of_birth=""
    )
    db.add(db_user_profile)
    db.commit()
    db.refresh(db_user_profile)

    return db_user



def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def update_user_profile(db: Session, username: str, user:schemas.User, user_profile: schemas.UserProfile):
    user = db.query(models.UserProfile).filter(models.UserProfile.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Username not found")
    
    # Update the user fields
    #user.username = user_profile.username
    #user.id=user_profile.id
    #user.username=user_profile.username
    
    user.email = user_profile.email
    user.full_name = user_profile.full_name
    user.gender = user_profile.gender
    user.address = user_profile.address
    user.country = user_profile.country
    user.phone_no = user_profile.phone_no
    user.date_of_birth = user_profile.date_of_birth

    db.commit()
    db.refresh(user)
    return user



def delete_username(db: Session, username: str):
    db.query(models.User).filter(models.User.username == username).delete()
    db.commit()
    


def get_user_profile_by_username(db: Session, username: str):
    return db.query(models.UserProfile).filter(models.UserProfile.username == username).first()





