
from typing import List
from pydantic import EmailStr,BaseModel
from fastapi import Security,APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import logging
from classes.APIKey import get_api_key
from classes.Post import Post
from classes.NewsLetterSignup import NewsletterSignup
from classes.EmailTemplate import EmailTemplate
from classes.SendGrid import SendGrid

import os

# Newsletter Signup Request Model
class NewsletterSignupRequest(BaseModel):
    name: str
    location: str
    email: EmailStr

# Newsletter Endpoints

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])

@router.post("/signup", response_model=bool, status_code=201)
async def signup_for_newsletter(newsletter: NewsletterSignupRequest):
    try:
        welcome_mail_template_id = os.environ.get("NEWSLETTER_WELCOME_EMAIL_TEMPLATE_ID")
        if not welcome_mail_template_id:
            raise HTTPException(status_code=500, detail="Missing email template ID in environment variables")
        
        email_template = await EmailTemplate.get(welcome_mail_template_id)
        
        existing_user = await NewsletterSignup.find_one(NewsletterSignup.email == newsletter.email)
        if existing_user:
            if existing_user.isActive:
                raise HTTPException(status_code=400, detail="Email already signed up for the newsletter")
            else:
                existing_user.isActive = True
                await existing_user.save()
        else:
            new_signup = NewsletterSignup(**newsletter.model_dump())
            await new_signup.insert()

        send_grid = SendGrid()
        send_grid.send_email(to_email=newsletter.email, subject=email_template.subject,content=email_template.body.replace("[name]", newsletter.name))

        return True
    except Exception as e:
        logging.error(f"Error occured while executing signup_for_newsletter : {e}")
        raise HTTPException(status_code=500, detail=f"Error occured while executing signup_for_newsletter : {e}")

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
        original_content = original_content.replace("[link]", f"https://journey.thehightabl.com/posts/article/{post_id}").replace("[title]", post.title).replace("[summary]", post.summary)
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
        
        with open("html_templates/unsubscribe.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail={"message": f"Error occured: {str(e)}"})