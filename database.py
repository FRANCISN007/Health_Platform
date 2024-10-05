#database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.environ.get('DB_URL')
#SQLALCHEMY_DATABASE_URL = "sqlite:///./health_db2"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#postgresql://db_url_xsxn_user:v45sQVZYF1jwlteydX8R8g1c7JxK4Acp@dpg-cs0qahm8ii6s73csqntg-a.oregon-postgres.render.com/db_url_xsxn   
#https://github.com/FRANCISN007/Health_Platform
#uvicorn main:app --host 0.0.0 --port 8000'