from typing import List, Optional
from pydantic import Field
from beanie import Document
from datetime import datetime
from bson import ObjectId


class Post(Document):
    title: str
    subtitle: Optional[str]
    summary: str
    author: str
    author_link: Optional[str]
    publish_date: datetime
    body: str
    mail_subject: str
    mail_content: str

    class Settings:
        collection = "posts"
    
    class Config():
        json_encoders={
            ObjectId : str
        }