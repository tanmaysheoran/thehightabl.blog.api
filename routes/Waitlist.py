from typing import List
from pydantic import EmailStr, BaseModel
from fastapi import Security, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import logging
from classes.APIKey import get_api_key
from classes.Post import Post
from classes.EmailTemplate import EmailTemplate
from classes.SendGrid import SendGrid
from classes.WaitlistSingup import WaitlistSignup

import os

# Waitlist Signup Request Model
class WaitlistSignupRequest(BaseModel):
    name: str
    location: str
    email: EmailStr

# Waitlist Endpoints

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])

@router.post("/signup", response_model=bool, status_code=201)
async def signup_for_waitlist(waitlist: WaitlistSignupRequest):
    try:
        welcome_mail_template_id = os.environ.get("WAITLIST_WELCOME_EMAIL_TEMPLATE_ID")
        if not welcome_mail_template_id:
            raise HTTPException(status_code=500, detail="Missing email template ID in environment variables")
        
        email_template = await EmailTemplate.get(welcome_mail_template_id)
        
        existing_user = await WaitlistSignup.find_one(WaitlistSignup.email == waitlist.email)
        if existing_user:
            if existing_user.isActive:
                raise HTTPException(status_code=400, detail="Email already signed up for the waitlist")
            else:
                existing_user.isActive = True
                await existing_user.save()
        else:
            new_signup = WaitlistSignup(**waitlist.model_dump())
            await new_signup.insert()

        send_grid = SendGrid()
        send_grid.send_email(to_email=waitlist.email, subject=email_template.subject, content=email_template.body.replace("[name]", waitlist.name))

        return True
    except Exception as e:
        logging.error(f"Error occurred while executing signup_for_waitlist: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while executing signup_for_waitlist: {e}")

@router.get("/users", response_model=List[WaitlistSignup])
async def get_waitlist_users(api_key = Security(get_api_key)):
    users = await WaitlistSignup.find_all().to_list()
    return users

@router.get("/send-notification/{post_id}")
async def send_waitlist_notification(post_id: str, api_key = Security(get_api_key)):
    try:
        post = await Post.get(post_id)
        
        if not post:
            raise HTTPException(status_code=400, detail="Post not found")

        email_template_id = os.environ.get("WAITLIST_EMAIL_TEMPLATE_ID")

        if not email_template_id:
            raise HTTPException(status_code=500, detail="Missing email template ID in environment variables")

        email_template = await EmailTemplate.get(email_template_id)

        if not email_template:
            raise HTTPException(status_code=400, detail="Email Template not found")
        
        waitlist = await WaitlistSignup.find(WaitlistSignup.isActive == True).to_list()

        if not waitlist:
            raise HTTPException(status_code=400, detail="No active signups found in waitlist")
        

        original_subject = post.mail_subject or email_template.subject
        original_content = email_template.body.replace("[content]", post.mail_content)
        original_content = original_content.replace("[link]", f"https://journey.thehightabl.com/posts/article/{post_id}").replace("[title]", post.title).replace("[summary]", post.summary)
        original_subject = original_subject.replace("[title]", post.title)

        send_grid = SendGrid()

        for user in waitlist:
            subject = original_subject.replace("[name]", user.name)
            content = original_content.replace("[name]", user.name).replace("[unsubscribe_link]", f"https://journey-api.thehightabl.com/waitlist/unsubscribe?email={user.email}")

            send_grid.send_email(user.email, subject, content)
        
        return {"status": "success", "emails_sent": len(waitlist)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")
    

@router.get("/unsubscribe", response_class=HTMLResponse)
async def get_html(email: EmailStr):
    try:
        user = await WaitlistSignup.find_one(WaitlistSignup.email == email)
        user.isActive = False
        await user.save()
        
        with open("html_templates/unsubscribe.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail={"message": f"Error occurred: {str(e)}"})
