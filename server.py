"""
FastAPI server for posting photos to Facebook and Instagram
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv
import aiofiles
from datetime import datetime
import cloudinary
import cloudinary.uploader
import tweepy
import asyncio
import praw

# Load environment variables
load_dotenv()

app = FastAPI(title="Facebook & Instagram Photo Poster")
# Serve uploads directory statically (so files are accessible via URL)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Facebook API configuration
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
FACEBOOK_API_VERSION = "v18.0"
FACEBOOK_GRAPH_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"

# Instagram API configuration
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")  # Direct Instagram Business Account ID
INSTAGRAM_API_VERSION = "v18.0"
INSTAGRAM_GRAPH_URL = f"https://graph.facebook.com/{INSTAGRAM_API_VERSION}"

# Public base URL for serving uploaded images (e.g., ngrok https URL)
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "instagram-uploads")

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )

# Twitter configuration
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

def get_twitter_client() -> tweepy.Client | None:
    if not (TWITTER_API_KEY and TWITTER_API_SECRET and TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_TOKEN_SECRET):
        return None
    # Use OAuth 1.0a for media upload via API v1.1 endpoints
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    )
    api_v1 = tweepy.API(auth)
    return api_v1


def get_twitter_client_v2() -> tweepy.Client | None:
    """Return Tweepy v2 Client for create_tweet (write)."""
    if not (TWITTER_API_KEY and TWITTER_API_SECRET and TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_TOKEN_SECRET):
        return None
    # bearer token is optional for write; provide consumer/access keys for OAuth 1.0a user context
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        return client
    except Exception:
        return None


# Reddit configuration
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
REDDIT_SUBREDDIT = os.getenv("REDDIT_SUBREDDIT", "test")

def get_reddit_client() -> praw.Reddit | None:
    """Return authenticated PRAW Reddit client."""
    if not (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET and REDDIT_USERNAME and REDDIT_PASSWORD):
        return None
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            user_agent=REDDIT_USER_AGENT or "tester/1.0"
        )
        return reddit
    except Exception:
        return None


@app.get("/api/verify-twitter")
async def verify_twitter():
    """
    Verifies Twitter credentials by calling verify_credentials via API v1.1.
    """
    api_v1 = get_twitter_client()
    if api_v1 is None:
        return JSONResponse(status_code=400, content={
            "valid": False,
            "error": "Twitter credentials not configured"
        })
    try:
        user = api_v1.verify_credentials()
        if user is None:
            return {"valid": False, "error": "verify_credentials returned None"}
        return {"valid": True, "user": {"id": str(user.id), "name": user.name, "screen_name": user.screen_name}}
    except Exception as e:
        return JSONResponse(status_code=401, content={
            "valid": False,
            "error": str(e)
        })

# Allowed image types
ALLOWED_EXTENSIONS = {"image/jpeg", "image/jpg", "image/png", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def get_page_id() -> str:
    """
    Get Facebook Page ID from the access token
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{FACEBOOK_GRAPH_URL}/me",
                params={"access_token": FACEBOOK_ACCESS_TOKEN}
            )
            response.raise_for_status()
            data = response.json()
            return data["id"]
        except httpx.HTTPError as e:
            print(f"Error fetching page ID: {e}")
            raise HTTPException(status_code=401, detail="Invalid Facebook token")


async def get_instagram_account_info() -> tuple:
    """
    Get Instagram account information
    Returns tuple of (instagram_account_id, username)
    Uses the hardcoded Instagram Account ID from environment
    """
    if not INSTAGRAM_ACCOUNT_ID:
        raise HTTPException(status_code=500, detail="Instagram Account ID not configured")
    
    async with httpx.AsyncClient() as client:
        try:
            # Get username from Instagram account
            response = await client.get(
                f"{INSTAGRAM_GRAPH_URL}/{INSTAGRAM_ACCOUNT_ID}",
                params={
                    "fields": "username",
                    "access_token": INSTAGRAM_ACCESS_TOKEN
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return INSTAGRAM_ACCOUNT_ID, data.get("username", "Instagram")
            
        except httpx.HTTPError as e:
            print(f"Error fetching Instagram info: {e}")
            # Return ID even if username fetch fails
            return INSTAGRAM_ACCOUNT_ID, "Instagram"
        except Exception as e:
            print(f"Error: {e}")
            return INSTAGRAM_ACCOUNT_ID, "Instagram"


async def post_photo_to_facebook(image_path: str, caption: str) -> dict:
    """
    Post a photo with caption to Facebook Page
    """
    try:
        # Get the page ID
        page_id = await get_page_id()
        
        # Prepare the multipart form data
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(image_path, "rb") as image_file:
                files = {
                    "source": (os.path.basename(image_path), image_file, "image/jpeg")
                }
                data = {
                    "message": caption,
                    "access_token": FACEBOOK_ACCESS_TOKEN
                }
                
                response = await client.post(
                    f"{FACEBOOK_GRAPH_URL}/{page_id}/photos",
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


async def post_photo_to_instagram(image_path: str, caption: str) -> dict:
    """
    Post a photo with caption to Instagram using a publicly accessible image_url.
    """
    try:
        # Use the configured Instagram account ID
        ig_account_id = INSTAGRAM_ACCOUNT_ID
        if not ig_account_id:
            raise Exception("Instagram Account ID not configured")

        # Upload to Cloudinary to get a permanent HTTPS URL
        if not (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET):
            raise Exception("Cloudinary is not configured. Please set CLOUDINARY_* env vars.")

        upload_result = cloudinary.uploader.upload(
            image_path,
            folder=CLOUDINARY_FOLDER,
            overwrite=True,
            resource_type="image"
        )
        public_image_url = upload_result.get("secure_url")
        if not public_image_url:
            raise Exception("Failed to obtain secure_url from Cloudinary upload")

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Create media container with image_url
            container_response = await client.post(
                f"{INSTAGRAM_GRAPH_URL}/{ig_account_id}/media",
                data={
                    "image_url": public_image_url,
                    "caption": caption,
                    "access_token": INSTAGRAM_ACCESS_TOKEN
                }
            )

            if container_response.status_code != 200:
                error_data = container_response.json() if container_response.text else {}
                print(f"Instagram container creation failed: {error_data}")
                raise Exception(f"Failed to create media container: {error_data}")

            container_data = container_response.json()
            container_id = container_data.get("id")
            if not container_id:
                raise Exception("No container ID returned from Instagram")

            # Poll container status until FINISHED (or fail after timeout)
            for _ in range(20):  # ~20 * 1s = 20 seconds max wait
                status_resp = await client.get(
                    f"{INSTAGRAM_GRAPH_URL}/{container_id}",
                    params={
                        "fields": "status_code",
                        "access_token": INSTAGRAM_ACCESS_TOKEN
                    }
                )
                status_resp.raise_for_status()
                status = status_resp.json().get("status_code")
                if status == "FINISHED":
                    break
                elif status in ("ERROR", "FAILED"):
                    raise Exception(f"Instagram media processing failed: {status}")
                await asyncio.sleep(1)

            # Publish the container
            publish_response = await client.post(
                f"{INSTAGRAM_GRAPH_URL}/{ig_account_id}/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": INSTAGRAM_ACCESS_TOKEN
                }
            )

            if publish_response.status_code != 200:
                error_data = publish_response.json() if publish_response.text else {}
                print(f"Instagram publish failed: {error_data}")
                raise Exception(f"Failed to publish media: {error_data}")

            return publish_response.json()

    except Exception as e:
        error_msg = str(e)
        print(f"Instagram posting error: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Instagram posting failed: {error_msg}")


async def post_photo_to_twitter(image_path: str, caption: str, cloudinary_url: str | None = None) -> dict:
    """
    Post a photo with caption to Twitter.
    Uses API v1.1 media upload via Tweepy and then posts status with media.
    """
    api_v1 = get_twitter_client()
    if api_v1 is None:
        raise HTTPException(status_code=500, detail="Twitter credentials not configured")

    try:
        # Prefer uploading the local image file to Twitter for best quality
        media = api_v1.media_upload(filename=image_path)
        media_id = media.media_id_string

        status = api_v1.update_status(status=caption[:280] if caption else "", media_ids=[media_id])
        return {"id": status.id_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Twitter: {str(e)}")


async def post_text_to_twitter(caption: str) -> dict:
    """
    Post a text-only tweet (no media) using Twitter API v2 create_tweet.
    """
    client_v2 = get_twitter_client_v2()
    if client_v2 is None:
        raise HTTPException(status_code=500, detail="Twitter credentials not configured for v2")

    try:
        # Twitter v2 supports up to 280 chars for standard accounts
        text = (caption or "")[:280]
        resp = client_v2.create_tweet(text=text)
        tweet_id = None
        if resp and hasattr(resp, "data") and resp.data:
            tweet_id = str(resp.data.get("id"))
        return {"id": tweet_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post text to Twitter (v2): {str(e)}")


async def post_photo_to_twitter_v2(image_path: str, caption: str) -> dict:
    """
    Post a photo with caption to Twitter using v1.1 media upload + v2 create_tweet.
    """
    # v1.1 for media upload
    api_v1 = get_twitter_client()
    if api_v1 is None:
        raise HTTPException(status_code=500, detail="Twitter v1.1 client not configured for media upload")

    # v2 for create_tweet with media_ids
    client_v2 = get_twitter_client_v2()
    if client_v2 is None:
        raise HTTPException(status_code=500, detail="Twitter v2 client not configured for create_tweet")

    try:
        media = api_v1.media_upload(filename=image_path)
        media_id = media.media_id_string
        text = (caption or "")[:280]
        resp = client_v2.create_tweet(text=text, media_ids=[media_id])
        tweet_id = None
        if resp and hasattr(resp, "data") and resp.data:
            tweet_id = str(resp.data.get("id"))
        return {"id": tweet_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post photo to Twitter (v2): {str(e)}")


async def post_photo_to_reddit(image_path: str, caption: str) -> dict:
    """
    Post a photo with title (caption) to Reddit subreddit.
    """
    reddit = get_reddit_client()
    if reddit is None:
        raise HTTPException(status_code=500, detail="Reddit credentials not configured")

    try:
        subreddit = reddit.subreddit(REDDIT_SUBREDDIT)
        title = (caption or "Untitled post")[:300]  # Reddit title max ~300 chars
        submission = subreddit.submit_image(title=title, image_path=image_path)
        return {"id": submission.id, "url": submission.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Reddit: {str(e)}")


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok", "message": "Server is running"}


@app.get("/api/verify-token")
async def verify_token():
    """
    Verify all platform token status
    """
    facebook_status = {"valid": False, "pageInfo": None}
    instagram_status = {"valid": False, "pageInfo": None}
    twitter_status = {"valid": False, "pageInfo": None}
    reddit_status = {"valid": False, "pageInfo": None}
    
    async with httpx.AsyncClient() as client:
        # Verify Facebook token
        try:
            fb_response = await client.get(
                f"{FACEBOOK_GRAPH_URL}/me",
                params={"access_token": FACEBOOK_ACCESS_TOKEN}
            )
            fb_response.raise_for_status()
            fb_data = fb_response.json()
            facebook_status = {
                "valid": True,
                "pageInfo": fb_data
            }
        except httpx.HTTPError as e:
            print(f"Facebook token error: {e}")
            facebook_status = {
                "valid": False,
                "error": str(e)
            }
        
        # Verify Instagram configuration
        try:
            ig_account_id, username = await get_instagram_account_info()
            instagram_status = {
                "valid": True,
                "pageInfo": {
                    "id": ig_account_id,
                    "username": username
                }
            }
        except Exception as e:
            print(f"Instagram configuration error: {e}")
            instagram_status = {
                "valid": False,
                "error": str(e)
            }
    
    # Verify Twitter configuration
    try:
        twitter_client = get_twitter_client()
        # Try to get user info to verify credentials
        user = twitter_client.verify_credentials()
        twitter_status = {
            "valid": True,
            "pageInfo": {
                "id": user.id,
                "username": user.screen_name
            }
        }
    except Exception as e:
        print(f"Twitter configuration error: {e}")
        twitter_status = {
            "valid": False,
            "error": str(e)
        }
    
    # Verify Reddit configuration
    try:
        reddit_client = get_reddit_client()
        # Try to get user info to verify credentials
        user = reddit_client.user.me()
        reddit_status = {
            "valid": True,
            "pageInfo": {
                "name": user.name,
                "id": user.id
            }
        }
    except Exception as e:
        print(f"Reddit configuration error: {e}")
        reddit_status = {
            "valid": False,
            "error": str(e)
        }
    
    return {
        "facebook": facebook_status,
        "instagram": instagram_status,
        "twitter": twitter_status,
        "reddit": reddit_status
    }


@app.post("/api/post")
async def post_to_social_media(
    photo: UploadFile = File(...),
    caption: str = Form("")
):
    """
    Post a photo with caption to both Facebook and Instagram
    """
    # Validate file type
    if photo.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and GIF are allowed."
        )
    
    # Read file and check size
    contents = await photo.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB."
        )
    
    # Save file temporarily
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{photo.filename}"
    file_path = UPLOAD_DIR / filename
    
    try:
        # Write file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        print(f"Processing upload: {{'filename': '{filename}', 'caption': '{caption}'}}")
        
        results = {
            "facebook": {"success": False, "error": None},
            "instagram": {"success": False, "error": None},
            "twitter": {"success": False, "error": None},
            "reddit": {"success": False, "error": None}
        }
        
        # Post to Facebook
        try:
            fb_result = await post_photo_to_facebook(str(file_path), caption)
            results["facebook"] = {
                "success": True,
                "postId": fb_result.get("id"),
                "postLink": f"https://www.facebook.com/{fb_result.get('post_id')}" if fb_result.get('post_id') else None
            }
            print("✅ Posted to Facebook successfully")
        except Exception as fb_error:
            results["facebook"] = {
                "success": False,
                "error": str(fb_error)
            }
            print(f"❌ Facebook posting failed: {fb_error}")
        
        # Post to Instagram
        try:
            ig_result = await post_photo_to_instagram(str(file_path), caption)
            results["instagram"] = {
                "success": True,
                "postId": ig_result.get("id")
            }
            print("✅ Posted to Instagram successfully")
        except Exception as ig_error:
            results["instagram"] = {
                "success": False,
                "error": str(ig_error)
            }
            print(f"❌ Instagram posting failed: {ig_error}")

        # Post photo with caption to Twitter (v1.1 upload + v2 create_tweet)
        try:
            tw_result = await post_photo_to_twitter_v2(str(file_path), caption)
            results["twitter"] = {
                "success": True,
                "postId": tw_result.get("id")
            }
            print("✅ Posted photo to Twitter successfully (v1.1 upload + v2 tweet)")
        except Exception as tw_error:
            results["twitter"] = {
                "success": False,
                "error": str(tw_error)
            }
            print(f"❌ Twitter photo posting failed: {tw_error}")

        # Post photo with title (caption) to Reddit
        try:
            rd_result = await post_photo_to_reddit(str(file_path), caption)
            results["reddit"] = {
                "success": True,
                "postId": rd_result.get("id"),
                "postUrl": rd_result.get("url")
            }
            print("✅ Posted photo to Reddit successfully")
        except Exception as rd_error:
            results["reddit"] = {
                "success": False,
                "error": str(rd_error)
            }
            print(f"❌ Reddit photo posting failed: {rd_error}")
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Determine overall success
        fb_success = results["facebook"]["success"]
        ig_success = results["instagram"]["success"]
        tw_success = results["twitter"]["success"]
        rd_success = results["reddit"]["success"]
        
        successes = []
        if fb_success: successes.append("Facebook")
        if ig_success: successes.append("Instagram")
        if tw_success: successes.append("Twitter")
        if rd_success: successes.append("Reddit")
        
        if len(successes) == 4:
            message = "🎉 Photo posted successfully to all platforms!"
        elif len(successes) > 0:
            message = f"🎉 Posted to {', '.join(successes)}. Others failed."
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to post to any platform"
            )
        
        return {
            "success": fb_success or ig_success or tw_success or rd_success,
            "message": message,
            "results": results
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        if file_path.exists():
            os.remove(file_path)
        raise
    except Exception as e:
        # Clean up file if it exists
        if file_path.exists():
            os.remove(file_path)
        
        print(f"Error in /api/post: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to post: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"✅ Server is running on http://localhost:{port}")
    print(f"📱 Facebook & Instagram API configured")
    uvicorn.run(app, host="0.0.0.0", port=port)

