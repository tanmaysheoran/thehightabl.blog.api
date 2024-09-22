from typing import  List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from classes.BlogContent import BlogContent
from classes.APIKey import get_api_key
from fastapi import Security

# BlogContent Request Models
class BlogContentRequest(BaseModel):
    page_name: str
    content: str
    section_name: str

# BlogContent Endpoints
router = APIRouter(prefix="/content", tags=["BlogContent"])
@router.post("/", response_model=BlogContent)
async def create_blog_content(content: BlogContentRequest, api_key = Security(get_api_key)):
    new_content = BlogContent(**content.model_dump())
    await new_content.insert()
    return new_content

@router.get("/", response_model=List[BlogContent])
async def list_blog_contents():
    contents = await BlogContent.find_all().to_list()
    return contents

@router.get("/{page_name}/{section_name}", response_model=BlogContent)
async def get_blog_content(page_name: str, section_name:str):
    content = await BlogContent.find_one(BlogContent.page_name==page_name, BlogContent.section_name==section_name)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.put("/{page_name}/{section_name}", response_model=BlogContent)
async def update_blog_content(page_name: str, section_name:str, content: BlogContentRequest, api_key = Security(get_api_key)):
    existing_content = await BlogContent.get(page_name=page_name, section_name=section_name)
    if not existing_content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    await existing_content.update({"$set": content.model_dump()})
    return existing_content

@router.delete("/{page_name}/{section_name}", response_model=dict)
async def delete_blog_content(page_name: str, section_name:str, api_key = Security(get_api_key)):
    content = await BlogContent.get(page_name=page_name, section_name=section_name)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    await content.delete()
    return {"message": "Content deleted successfully"}
