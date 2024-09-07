#models.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    hashed_password = Column(String, nullable=False)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)  # Ensure unique constraint on user_id
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name= Column(String)
    gender = Column(String)
    address = Column(String)
    country = Column(String)
    phone_no = Column(String)
    date_of_birth = Column(String)
    
    user = relationship("User", back_populates="profile")
    
    