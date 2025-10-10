"""
AI content generation endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import (
    generate_platform_content, 
    refine_content, 
    regenerate_platform_content,
    regenerate_image
)

router = APIRouter(prefix="/api", tags=["ai"])


class GenerateRequest(BaseModel):
    topic: str
    tone: str = "casual"
    image_style: str = "realistic"
    generate_image: bool = True
    use_prompt_enhancer: bool = True


class RegenerateRequest(BaseModel):
    topic: str
    platform: str
    tone: str = "casual"
    previous_content: str = ""


class RegenerateImageRequest(BaseModel):
    topic: str
    tone: str = "casual"
    image_style: str = "realistic"


class RefineRequest(BaseModel):
    original_content: str
    platform: str
    instructions: str


@router.post("/generate-content")
async def generate_content(request: GenerateRequest):
    """
    Generate platform-specific content for all social media platforms with optional image
    Automatically enhances user prompts for better results
    """
    try:
        result = await generate_platform_content(
            topic=request.topic,
            tone=request.tone,
            image_style=request.image_style,
            generate_image=request.generate_image,
            use_prompt_enhancer=request.use_prompt_enhancer
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content: {str(e)}"
        )


@router.post("/regenerate-content")
async def regenerate_content(request: RegenerateRequest):
    """
    Regenerate content for a specific platform
    """
    try:
        result = await regenerate_platform_content(
            topic=request.topic,
            platform=request.platform,
            tone=request.tone,
            previous_content=request.previous_content
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate content: {str(e)}"
        )


@router.post("/regenerate-image")
async def regenerate_image_endpoint(request: RegenerateImageRequest):
    """
    Regenerate a new image with DALL-E 3
    """
    try:
        result = await regenerate_image(
            topic=request.topic,
            tone=request.tone,
            image_style=request.image_style
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate image: {str(e)}"
        )


@router.post("/refine-content")
async def refine_post_content(request: RefineRequest):
    """
    Refine existing content based on user instructions
    """
    try:
        result = await refine_content(
            original_content=request.original_content,
            platform=request.platform,
            instructions=request.instructions
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refine content: {str(e)}"
        )

