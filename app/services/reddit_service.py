"""
Reddit posting service
"""
from fastapi import HTTPException
from app.clients.reddit import get_reddit_client
from app.config import settings


async def post_photo_to_reddit(image_path: str, caption: str) -> dict:
    """
    Post a photo with title (caption) to Reddit subreddit
    
    Args:
        image_path: Path to the image file
        caption: Post title (max 300 characters)
        
    Returns:
        dict: Response with submission ID and URL
    """
    reddit = get_reddit_client()
    if reddit is None:
        raise HTTPException(status_code=500, detail="Reddit credentials not configured")

    try:
        subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)
        title = (caption or "Untitled post")[:300]
        submission = subreddit.submit_image(title=title, image_path=image_path)
        return {"id": submission.id, "url": submission.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Reddit: {str(e)}")

