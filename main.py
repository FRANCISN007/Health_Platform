# main.py
import os
from fastapi import FastAPI, Depends, HTTPException, Response, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import pwd_context, authenticate_user, create_access_token, get_current_user
from typing import List, Optional
from database import engine, Base, get_db
import crud, models, schemas, auth
from loguru import logger

from fastapi import FastAPI
import requests
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from bs4 import BeautifulSoup


import nltk

# Set the directory where nltk_data should be stored
nltk_data_dir = '/opt/render/nltk_data'
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

# Download the necessary punkt resource
nltk.download('punkt', download_dir=nltk_data_dir)



# Download necessary NLTK resources at startup
nltk.download('stopwords')
nltk.download('punkt')

# Initialize FastAPI app
app = FastAPI()


# Your valid Google Custom Search API key and Search Engine ID
#API_KEY = "AIzaSyC8KUNnXfAJNAbslhsYT2AQpyhPk_YMj7Y"
#CX = "f26320feb4dbe4a1b"  # Replace with your actual CX (Search Engine ID)

API_KEY = os.environ.get('API_KEY')
CX = os.environ.get('CX')

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

@app.patch("/users/profile", tags=["User"])
async def update_user_profile(
    user_profile: schemas.UserProfile = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update user profile without providing username.
    Ensure that the email matches the original user's email.
    """
    # Fetch the current user's profile from the database using the current user's username
    existing_profile = crud.get_user_profile_by_username(db=db, username=current_user.username)

    if not existing_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    # Ensure that the email from the request body matches the current user's email
    if user_profile.email.strip() != current_user.email.strip():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The email provided does not match the current user's email"
        )

    # Proceed with the update
    updated_profile = crud.update_user_profile(db=db, user_id=current_user.id, user_profile=user_profile)

    return updated_profile


@app.get("/users/profile", response_model=schemas.UserProfileWithID, tags=["User"])
def view_user_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    View the current user's profile.
    """
    user_profile = crud.get_user_profile_by_username(db=db, username=current_user.username)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return user_profile




def search_for_answer(question):
    try:
        # Tokenize and filter stopwords
        question = question.lower()
        tokens = word_tokenize(question)

        # Leave out fewer stopwords to retain more context
        tokens = [token for token in tokens if token not in stopwords.words("english") and token.isalnum()]

        # Formulate the search query
        search_query = " ".join(tokens)

        # Make a request to Google Custom Search API
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': API_KEY,
            'cx': CX,
            'q': search_query,
            'num': 3  # Retrieve the top 3 results for a more comprehensive answer
        }
        response = requests.get(url, params=params)
        data = response.json()

        # Check if items exist in the response
        if 'items' in data:
            full_answer = ""
            # Iterate over the first few search results
            for item in data['items']:
                # Get the snippet and the URL
                snippet = item.get('snippet', "No snippet available.")
                link = item.get('link', "")

                # Try to get the full content from the page using BeautifulSoup
                if link:
                    try:
                        page_content = requests.get(link).content
                        soup = BeautifulSoup(page_content, 'html.parser')
                        # Extract the paragraph text
                        paragraphs = soup.find_all('p')
                        # Combine paragraph texts (you can refine the extraction logic)
                        full_text = " ".join([para.get_text() for para in paragraphs])
                        full_answer += full_text[:1000] + "\n\n"  # Limit to first 1000 characters for now
                    except Exception as e:
                        # If web scraping fails, fallback to using the snippet
                        full_answer += snippet + "\n\n"
                else:
                    full_answer += snippet + "\n\n"
            return full_answer.strip()
        else:
            return f"Debugging Info: {data}"

    except Exception as e:
        return f"Error occurred: {str(e)}"

# Create an endpoint for users to ask questions
@app.post("/", tags= ["User"])
async def ask_question(question: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    answer = search_for_answer(question)
    return {"answer": answer}


@app.delete("/users/{username}", tags= ["User"])
def delete_username(username: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    This endpoint allows the user to Delete its own created profile
    """
    
    existing_username = crud.get_user_by_username(db=db, username=username)
    if existing_username is None:
        logger.warning(f"username not found with id: {username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"username {username} does not exist")
    if current_user.username != username: 
        logger.warning(f"User {current_user.username} is not authorized to delete username: {username}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not authorized to delete username {username}")
       
    crud.delete_username(db=db, username=username)
    logger.info(f"Username {username} deleted successfully")
    return {"message": "username deleted successfully"}


