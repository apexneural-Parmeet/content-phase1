"""
Storage management for scheduled posts
"""
import json
from app.config import settings


def load_scheduled_posts() -> list:
    """
    Load scheduled posts from JSON file
    
    Returns:
        list: List of scheduled posts
    """
    if settings.SCHEDULED_POSTS_FILE.exists():
        try:
            with open(settings.SCHEDULED_POSTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading scheduled posts: {e}")
            return []
    return []


def save_scheduled_posts(posts: list) -> None:
    """
    Save scheduled posts to JSON file
    
    Args:
        posts: List of scheduled posts to save
    """
    try:
        with open(settings.SCHEDULED_POSTS_FILE, 'w') as f:
            json.dump(posts, f, indent=2)
    except Exception as e:
        print(f"Error saving scheduled posts: {e}")

