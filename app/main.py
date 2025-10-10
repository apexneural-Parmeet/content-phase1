"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import health, posts, scheduled, ai_content, enhance
from app.scheduler.scheduler import init_scheduler, restore_scheduled_jobs

# Initialize FastAPI app
app = FastAPI(
    title="Social Media AI Manager",
    description="Multi-platform social media posting and scheduling with AI content generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(health.router)
app.include_router(posts.router)
app.include_router(scheduled.router)
app.include_router(ai_content.router)
app.include_router(enhance.router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize scheduler and restore jobs on startup
    """
    print("🚀 Starting Social Media AI Manager...")
    init_scheduler()
    restore_scheduled_jobs()
    print(f"✅ Server is ready on http://localhost:{settings.PORT}")
    print("📱 All platforms configured")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    from app.scheduler.scheduler import scheduler
    if scheduler.running:
        scheduler.shutdown()
        print("👋 Scheduler shut down gracefully")

