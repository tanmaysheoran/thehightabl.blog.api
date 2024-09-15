from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
import motor.motor_asyncio
from contextlib import asynccontextmanager

from classes.BlogContent import BlogContent
from classes.NewsLetterSignup import NewsletterSignup
from classes.Post import Post
from classes.EmailTemplate import EmailTemplate

from routes.BlogContent import router as blog_content_router
from routes.Geolocation import router as geolocation_router
from routes.Newsletter import router as newsletter_router
from routes.Post import router as post_router
from routes.EmailTemplate import router as email_template_router
import os

# MongoDB connection string (update with your credentials if necessary)
MONGO_URI = os.environ.get("MONGO_URI")
API_KEY = "mysecretapikey123"

# Connect to the database and initialize Beanie with the models
@asynccontextmanager
async def lifespan(app: FastAPI):
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    database = client.get_database(name="blog")
    await init_beanie(database, document_models=[NewsletterSignup, Post, BlogContent, EmailTemplate])
    yield

# Run the database initialization on startup
app = FastAPI(lifespan=lifespan)

origins = ["https://journey.thehightabl.com", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API endpoint to sign up for the newsletter
app.include_router(blog_content_router)
app.include_router(geolocation_router)
app.include_router(newsletter_router)
app.include_router(post_router)
app.include_router(email_template_router)


# To run the FastAPI app, use: uvicorn app_name:app --reload
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)