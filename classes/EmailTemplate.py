from beanie import Document
from typing import List

# Models for MongoDB
class EmailTemplate(Document):
    subject: str
    body: str
    subject_placeholders: List[str] = []
    body_placeholders: List[str] = []

    class Settings:
        collection = "emailTemplates"