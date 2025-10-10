"""
Twitter API client configuration
"""
import tweepy
from app.config import settings

def get_twitter_v1_client() -> tweepy.API | None:
    """
    Return Tweepy API v1.1 client for media upload.
    Returns None if credentials are not configured.
    """
    if not all([
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_TOKEN_SECRET
    ]):
        return None
    
    auth = tweepy.OAuth1UserHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_TOKEN_SECRET
    )
    return tweepy.API(auth)


def get_twitter_v2_client() -> tweepy.Client | None:
    """
    Return Tweepy v2 Client for create_tweet (write operations).
    Returns None if credentials are not configured.
    """
    if not all([
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_TOKEN_SECRET
    ]):
        return None
    
    try:
        return tweepy.Client(
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
    except Exception:
        return None

