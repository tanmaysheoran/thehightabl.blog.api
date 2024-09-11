from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from beanie import Document, init_beanie
import motor.motor_asyncio
from typing import Optional
import asyncio
from contextlib import asynccontextmanager

# MongoDB connection string (update with your credentials if necessary)
MONGO_URI = "mongodb+srv://fast:8j1peRu2dktTGfw2@cluster0.npsydwr.mongodb.net/?retryWrites=true&w=majority&appName=cluster0/identity"

# MongoDB models (using Beanie)
class NewsletterSignup(Document):
    name: str
    email: EmailStr
    city: Optional[str] = None

    class Settings:
        collection = "signups"  # MongoDB collection name

# Pydantic model for request validation
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    city: Optional[str] = None

# Connect to the database and initialize Beanie with the models
@asynccontextmanager
async def lifespan(app: FastAPI):
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    database = client.get_database(name="identity")
    await init_beanie(database, document_models=[NewsletterSignup])
    yield

# Run the database initialization on startup
app = FastAPI(lifespan=lifespan)
# API endpoint to sign up for the newsletter
@app.post("/signup", response_model=SignupRequest)
async def signup(signup_request: SignupRequest):
    # Check if the email already exists in the database
    existing_user = await NewsletterSignup.find_one(NewsletterSignup.email == signup_request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already signed up for the newsletter")

    # Create a new signup document
    new_signup = NewsletterSignup(**signup_request.dict())
    await new_signup.insert()  # Save to MongoDB

    return signup_request



# To run the FastAPI app, use: uvicorn app_name:app --reload
