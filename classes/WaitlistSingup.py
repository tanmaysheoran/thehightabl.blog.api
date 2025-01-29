from beanie import Document
from pydantic import EmailStr

# Models for MongoDB
class WaitlistSignup(Document):
    name: str
    location: str
    email: EmailStr
    isActive: bool = True

    class Settings:
        collection = "waitlist"