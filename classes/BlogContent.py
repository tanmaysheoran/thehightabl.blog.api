from beanie import Document
from bson import ObjectId


class BlogContent(Document):
    page_name: str
    content: str
    section_name: str

    class Settings:
        collection = "blog_contents"

    class Config():
        json_encoders={
            ObjectId : str
        }