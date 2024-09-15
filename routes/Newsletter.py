
from typing import List
from pydantic import EmailStr,BaseModel
from fastapi import Security,APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from classes.APIKey import get_api_key
from classes.Post import Post
from classes.NewsLetterSignup import NewsletterSignup
from classes.EmailTemplate import EmailTemplate
from classes.SendGrid import SendGrid

from bson import ObjectId
import os

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

    welcome_mail_template_id = os.environ.get("NEWSLETTER_WELCOME_EMAIL_TEMPLATE_ID")
    if not welcome_mail_template_id:
        raise HTTPException(status_code=500, detail="Missing email template ID in environment variables")
    
    email_template = await EmailTemplate.get(welcome_mail_template_id)

    new_signup = NewsletterSignup(**newsletter.model_dump())
    await new_signup.insert()
    
    send_grid = SendGrid()
    send_grid.send_email(to_email=newsletter.email, subject=email_template.subject,content=email_template.body.replace("[name]", newsletter.name))

    return new_signup

@router.get("/users", response_model=List[NewsletterSignup])
async def get_newsletter_users(api_key = Security(get_api_key)):
    users = await NewsletterSignup.find_all().to_list()
    return users

@router.get("/send-notification/{post_id}")
async def send_newsletter_notification(post_id:str, api_key = Security(get_api_key)):
    try:
        post = await Post.get(post_id)
        
        if not post:
            raise HTTPException(status_code=400, detail="Post not found")

        email_template_id = os.environ.get("NEWSLETTER_EMAIL_TEMPLATE_ID")

        if not email_template_id:
            raise HTTPException(status_code=500, detail="Missing email template ID in environment variables")

        email_template = await EmailTemplate.get(email_template_id)

        if not email_template:
            raise HTTPException(status_code=400, detail="Email Template not found")
        
        newsletter_list = await NewsletterSignup.find(NewsletterSignup.isActive == True).to_list()

        if not newsletter_list:
            raise HTTPException(status_code=400, detail="No active signups found in newsletter")
        

        original_subject = post.mail_subject or email_template.subject
        original_content = email_template.body.replace("[content]", post.mail_content)
        original_content = original_content.replace("[link]", f"https://journey.thehightabl.com/post?id={post_id}").replace("[title]", post.title).replace("[summary]", post.summary)
        original_subject = original_subject.replace("[title]",post.title)

        send_grid = SendGrid()

        for user in newsletter_list:
            subject = original_subject.replace("[name]",user.name)
            content = original_content.replace("[name]",user.name).replace("[unsubscribe_link]",f"https://journey-api.thehightabl.com/newsletter/unsubscribe?email={user.email}")

            send_grid.send_email(user.email, subject, content)
        
        return {"status": "success", "emails_sent": len(newsletter_list)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured: {str(e)}")
    

@router.get("/unsubscribe", response_class=HTMLResponse)
async def get_html(email:EmailStr):
    try:
        user = await NewsletterSignup.find_one(NewsletterSignup.email==email)
        user.isActive = False
        await user.save()
        
        html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Unsubscribe Confirmation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                text-align: center;
                background-color: #ffffff;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
            }
            p {
                color: #555;
                font-size: 18px;
                margin: 20px 0;
            }
            .back-home {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #3498db;
                color: #fff;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.3s;
            }
            .back-home:hover {
                background-color: #2980b9;
            }
        </style>
    </head>
    <body>

        <div class="container">
            <h1>You've Been Unsubscribed</h1>
            <p>You have successfully been removed from our newsletter. We're sorry to see you go!</p>
        </div>

    </body>
    </html>

        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Error occured: {str(e)}")