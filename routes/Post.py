from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter, HTTPException
from classes.Post import Post
from classes.APIKey import get_api_key
from fastapi import Security
# Post Request Models
class PostRequest(BaseModel):
    title: str
    subtitle: Optional[str]
    summary: str
    author: str
    author_link: Optional[str]
    publish_date: datetime
    body: str

class PostResponse(BaseModel):
    id: str
    title: str
    summary: str
    author: str
    publish_date: datetime

# Post Endpoints
\
router = APIRouter(prefix="/posts", tags=["Post"])

@router.post("/", response_model=Post)
async def create_post(post: PostRequest, api_key:str = Security(get_api_key)):
    new_post = Post(**post.model_dump())
    await new_post.insert()
    return new_post

@router.get("/", response_model=List[PostResponse])
async def list_posts():
    posts = [item.model_dump() for item in await Post.find_all().to_list()]
    return posts

@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: str):
    post = await Post.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=Post)
async def update_post(post_id: str, post: PostRequest, api_key:str = Security(get_api_key)):
    existing_post = await Post.get(post_id)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    await existing_post.update({"$set": post.model_dump()})
    return existing_post

@router.delete("/{post_id}", response_model=dict)
async def delete_post(post_id: str, api_key:str = Security(get_api_key)):
    post = await Post.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    await post.delete()
    return {"message": "Post deleted successfully"}
