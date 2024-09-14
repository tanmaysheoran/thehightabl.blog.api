from pydantic import BaseModel
from classes.NewsLetterSignup import NewsletterSignup
from typing import List
from pydantic import EmailStr
from fastapi import APIRouter, HTTPException
from classes.APIKey import get_api_key
from fastapi import Security

# Newsletter Signup Request Model
class NewsletterSignupRequest(BaseModel):
    name: str
    location: str
    email: EmailStr

# Newsletter Endpoints

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])

@router.post("/signup", response_model=NewsletterSignup)
async def signup_for_newsletter(newsletter: NewsletterSignupRequest):
    existing_user = await NewsletterSignup.find_one(NewsletterSignup.email == newsletter.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already signed up for the newsletter")
    new_signup = NewsletterSignup(**newsletter.model_dump())
    await new_signup.insert()
    return new_signup

@router.get("/users", response_model=List[NewsletterSignup])
async def get_newsletter_users(api_key = Security(get_api_key)):
    users = await NewsletterSignup.find_all().to_list()
    return users
