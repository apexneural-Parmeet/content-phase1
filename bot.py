#!/usr/bin/env python3
"""
Standalone Telegram Bot for Social Hub
Run independently from the FastAPI server
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.telegram_bot_service import telegram_bot
from app.config import settings


async def main():
    """Main entry point for the Telegram bot"""
    print("=" * 60)
    print("🤖 Social Hub Telegram Bot")
    print("=" * 60)
    
    # Check if token is configured
    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in .env file")
        print("Please add your Telegram bot token to the .env file")
        print("Example: TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    print(f"✅ Bot token configured")
    print(f"🔗 Backend API: http://localhost:{settings.PORT}")
    print("📱 Starting bot polling...")
    print("-" * 60)
    
    try:
        # Start the bot (this will run indefinitely)
        await telegram_bot.start_bot()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down bot...")
        await telegram_bot.stop_bot()
        print("✅ Bot stopped gracefully")
    except Exception as e:
        print(f"❌ ERROR: Bot crashed - {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n💡 TIP: Make sure the backend server is running first!")
    print("   Run: python run.py\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")

