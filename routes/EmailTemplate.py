from pydantic import BaseModel, EmailStr
from typing import List
from classes.EmailTemplate import EmailTemplate
from fastapi import APIRouter, HTTPException
from classes.APIKey import get_api_key
from fastapi import Security


# Pydantic Model for Input Validation
class EmailTemplateCreate(BaseModel):
    subject: str
    body: str
    subject_placeholders: List[str]
    body_placeholders: List[str]

# Pydantic Model for Updates
class EmailTemplateUpdate(BaseModel):
    subject: str = None
    body: str = None
    subject_placeholders: List[str] = None
    body_placeholders: List[str] = None

router = APIRouter(prefix="/email-templates", tags=["Email Templates"], dependencies=[Security(get_api_key)])



# Create Email Template
@router.post("/", response_model=EmailTemplate)
async def create_email_template(email_template: EmailTemplateCreate):
    email_template_doc = EmailTemplate(**email_template.model_dump())
    await email_template_doc.insert()
    return email_template_doc

# Get All Email Templates
@router.get("/", response_model=List[EmailTemplate])
async def get_all_email_templates():
    email_templates = await EmailTemplate.find_all().to_list()
    return email_templates

# Get Single Email Template by ID
@router.get("/{id}", response_model=EmailTemplate)
async def get_email_template(id: str):
    email_template = await EmailTemplate.get(id)
    if not email_template:
        raise HTTPException(status_code=404, detail="EmailTemplate not found")
    return email_template

# Update Email Template by ID
@router.put("/{id}", response_model=EmailTemplate)
async def update_email_template(id: str, email_template_update: EmailTemplateUpdate):
    email_template = await EmailTemplate.get(id)
    if not email_template:
        raise HTTPException(status_code=404, detail="EmailTemplate not found")

    # Update fields if they exist in the request
    update_data = email_template_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(email_template, key, value)

    await email_template.save()
    return email_template

# Delete Email Template by ID
@router.delete("/{id}", response_model=EmailTemplate)
async def delete_email_template(id: str):
    email_template = await EmailTemplate.get(id)
    if not email_template:
        raise HTTPException(status_code=404, detail="EmailTemplate not found")

    await email_template.delete()
    return email_template