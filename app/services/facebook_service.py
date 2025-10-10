"""
Facebook posting service
"""
import os
import httpx
from fastapi import HTTPException
from app.config import settings


async def get_facebook_page_id() -> str:
    """
    Get Facebook Page ID from the access token
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.FACEBOOK_GRAPH_URL}/me",
                params={"access_token": settings.FACEBOOK_ACCESS_TOKEN}
            )
            response.raise_for_status()
            data = response.json()
            return data["id"]
        except httpx.HTTPError as e:
            print(f"Error fetching page ID: {e}")
            raise HTTPException(status_code=401, detail="Invalid Facebook token")


async def post_photo_to_facebook(image_path: str, caption: str) -> dict:
    """
    Post a photo with caption to Facebook Page
    
    Args:
        image_path: Path to the image file
        caption: Caption text for the post
        
    Returns:
        dict: Response from Facebook API with post ID
    """
    try:
        page_id = await get_facebook_page_id()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(image_path, "rb") as image_file:
                files = {
                    "source": (os.path.basename(image_path), image_file, "image/jpeg")
                }
                data = {
                    "message": caption,
                    "access_token": settings.FACEBOOK_ACCESS_TOKEN
                }
                
                response = await client.post(
                    f"{settings.FACEBOOK_GRAPH_URL}/{page_id}/photos",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                return response.json()
                
    except httpx.HTTPError as e:
        print(f"Error posting to Facebook: {e}")
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json() if e.response.text else str(e)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to post to Facebook: {error_detail}"
            )
        raise HTTPException(status_code=500, detail=f"Failed to post to Facebook: {str(e)}")

