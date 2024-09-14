from beanie import Document
from pydantic import EmailStr

# Models for MongoDB
class NewsletterSignup(Document):
    name: str
    location: str
    email: EmailStr

    class Settings:
        collection = "newsletter"