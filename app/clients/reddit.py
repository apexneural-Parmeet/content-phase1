"""
Reddit API client configuration
"""
import praw
from app.config import settings

def get_reddit_client() -> praw.Reddit | None:
    """
    Return authenticated PRAW Reddit client.
    Returns None if credentials are not configured.
    """
    if not all([
        settings.REDDIT_CLIENT_ID,
        settings.REDDIT_CLIENT_SECRET,
        settings.REDDIT_USERNAME,
        settings.REDDIT_PASSWORD
    ]):
        return None
    
    try:
        return praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            username=settings.REDDIT_USERNAME,
            password=settings.REDDIT_PASSWORD,
            user_agent=settings.REDDIT_USER_AGENT
        )
    except Exception:
        return None

