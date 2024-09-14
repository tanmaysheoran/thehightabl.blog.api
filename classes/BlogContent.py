from beanie import Document

class BlogContent(Document):
    page_name: str
    content: str
    section_name: str

    class Settings:
        collection = "blog_contents"