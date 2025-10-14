"""
Telegram Bot service for social media management
Complete feature parity with web frontend
"""
import os
import uuid
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
import httpx
from app.config import settings
from app.services.ai_service import generate_platform_content, regenerate_platform_content
from app.services.facebook_service import post_photo_to_facebook
from app.services.instagram_service import post_photo_to_instagram
from app.services.twitter_service import post_photo_to_twitter
from app.services.reddit_service import post_photo_to_reddit
from app.scheduler.storage import load_scheduled_posts, save_scheduled_posts
from app.scheduler.scheduler import scheduler, execute_scheduled_post
from apscheduler.triggers.date import DateTrigger

# Conversation states
(MENU, GENERATE_TOPIC, GENERATE_TONE, GENERATE_PROVIDER, GENERATE_STYLE, 
 APPROVE_PLATFORMS, CREATE_CAPTION, CREATE_IMAGE, CREATE_PLATFORMS, 
 SCHEDULE_TIME, VIEW_SCHEDULE_DETAIL) = range(11)

# User session storage
user_sessions = {}


class TelegramBotService:
    """Handles all Telegram bot interactions"""
    
    def __init__(self):
        self.application = None
    
    # ==================== COMMAND HANDLERS ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Main menu"""
        keyboard = [
            [InlineKeyboardButton("🤖 Generate AI Content", callback_data="menu_generate")],
            [InlineKeyboardButton("📝 Create Manual Post", callback_data="menu_create")],
            [InlineKeyboardButton("📅 View Scheduled Posts", callback_data="menu_schedule")],
            [InlineKeyboardButton("📊 Platform Status", callback_data="menu_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 *Welcome to Social Hub Bot!*\n\n"
            "Manage all your social media from Telegram!\n\n"
            "📱 Features:\n"
            "• AI content generation (Nano Banana or DALL-E)\n"
            "• Manual post creation\n"
            "• Schedule posts\n"
            "• Multi-platform publishing\n\n"
            "What would you like to do?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return MENU
    
    # ==================== MENU HANDLERS ====================
    
    async def menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle main menu selections"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "menu_generate":
            await query.edit_message_text(
                "🤖 *AI Content Generator*\n\n"
                "Enter your topic or idea:\n\n"
                "_Examples:_\n"
                "• Product launch announcement\n"
                "• Coffee morning vibes\n"
                "• Weekend sale event\n"
                "• Team achievement celebration",
                parse_mode='Markdown'
            )
            return GENERATE_TOPIC
        
        elif query.data == "menu_create":
            await query.edit_message_text(
                "📝 *Create Manual Post*\n\n"
                "Step 1: Send me your image\n\n"
                "You can send a photo or upload an image file.",
                parse_mode='Markdown'
            )
            return CREATE_IMAGE
        
        elif query.data == "menu_schedule":
            posts = load_scheduled_posts()
            
            if not posts:
                keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "📅 *No Scheduled Posts*\n\n"
                    "Use the menu to create your first post!",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                return MENU
            
            # Sort posts
            scheduled = [p for p in posts if p.get('status') != 'posted']
            posted = [p for p in posts if p.get('status') == 'posted']
            
            message = "📅 *Scheduled Posts*\n\n"
            
            if scheduled:
                message += "⏰ *UPCOMING:*\n"
                for post in scheduled[:5]:
                    platforms = ", ".join([p for p, v in post['platforms'].items() if v])
                    message += f"• {post['scheduled_time'][:16]}\n"
                    message += f"  {post['caption'][:40]}...\n"
                    message += f"  📱 {platforms}\n\n"
            
            if posted:
                message += "\n✅ *RECENTLY POSTED:*\n"
                for post in posted[:3]:
                    posted_count = post.get('posted_to', '?')
                    message += f"• {post['scheduled_time'][:16]}\n"
                    message += f"  Posted to {posted_count} platforms\n\n"
            
            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            return MENU
        
        elif query.data == "menu_status":
            message = "📊 *Platform Connection Status*\n\n"
            
            # Check each platform
            platforms_check = {
                "Facebook": settings.FACEBOOK_ACCESS_TOKEN,
                "Instagram": settings.INSTAGRAM_ACCESS_TOKEN,
                "Twitter": settings.TWITTER_API_KEY,
                "Reddit": settings.REDDIT_CLIENT_ID
            }
            
            for name, token in platforms_check.items():
                icon = "🟢" if token else "🔴"
                status = "Connected" if token else "Not configured"
                message += f"{icon} *{name}*: {status}\n"
            
            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            return MENU
        
        elif query.data == "back_menu":
            # Return to main menu
            keyboard = [
                [InlineKeyboardButton("🤖 Generate AI Content", callback_data="menu_generate")],
                [InlineKeyboardButton("📝 Create Manual Post", callback_data="menu_create")],
                [InlineKeyboardButton("📅 View Scheduled Posts", callback_data="menu_schedule")],
                [InlineKeyboardButton("📊 Platform Status", callback_data="menu_status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🎯 *Social Hub Bot - Main Menu*\n\n"
                "What would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return MENU
        
        return MENU
    
    # ==================== AI GENERATION FLOW ====================
    
    async def generate_topic_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle topic input for AI generation"""
        user_id = update.effective_user.id
        topic = update.message.text
        
        # Initialize session
        user_sessions[user_id] = {
            "topic": topic,
            "mode": "generate"
        }
        
        # Show tone options
        keyboard = [
            [InlineKeyboardButton("Casual", callback_data="tone_casual"),
             InlineKeyboardButton("Professional", callback_data="tone_professional")],
            [InlineKeyboardButton("Corporate", callback_data="tone_corporate"),
             InlineKeyboardButton("Funny", callback_data="tone_funny")],
            [InlineKeyboardButton("Inspirational", callback_data="tone_inspirational"),
             InlineKeyboardButton("Educational", callback_data="tone_educational")],
            [InlineKeyboardButton("Storytelling", callback_data="tone_storytelling"),
             InlineKeyboardButton("Promotional", callback_data="tone_promotional")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ Topic: *{topic}*\n\n"
            "Select content tone:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return GENERATE_TONE
    
    async def generate_tone_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tone selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        tone = query.data.replace("tone_", "")
        user_sessions[user_id]["tone"] = tone
        
        # Show image provider options
        keyboard = [
            [InlineKeyboardButton("🍌 Nano Banana (Ultra Fast 2-3s)", callback_data="provider_nano-banana")],
            [InlineKeyboardButton("🎨 DALL-E 3 (Premium 15-20s)", callback_data="provider_dalle")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Tone: *{tone.title()}*\n\n"
            "Select image generator:\n\n"
            "🍌 *Nano Banana* - Ultra-fast, great quality\n"
            "🎨 *DALL-E 3* - Premium quality, slower",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return GENERATE_PROVIDER
    
    async def generate_provider_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image provider selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        provider = query.data.replace("provider_", "")
        user_sessions[user_id]["image_provider"] = provider
        
        # Show image style options
        keyboard = [
            [InlineKeyboardButton("Realistic", callback_data="style_realistic"),
             InlineKeyboardButton("Minimal", callback_data="style_minimal")],
            [InlineKeyboardButton("Anime", callback_data="style_anime"),
             InlineKeyboardButton("2D Art", callback_data="style_2d")],
            [InlineKeyboardButton("Comic Book", callback_data="style_comics"),
             InlineKeyboardButton("Sketch", callback_data="style_sketch")],
            [InlineKeyboardButton("Vintage", callback_data="style_vintage"),
             InlineKeyboardButton("Disney", callback_data="style_disney")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        provider_name = "Nano Banana" if provider == "nano-banana" else "DALL-E 3"
        await query.edit_message_text(
            f"✅ Generator: *{provider_name}*\n\n"
            "Select image style:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return GENERATE_STYLE
    
    async def generate_style_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image style selection and trigger generation"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        style = query.data.replace("style_", "")
        session = user_sessions[user_id]
        session["image_style"] = style
        
        # Get provider name for message
        provider = session.get("image_provider", "dalle")
        provider_name = "Nano Banana (ultra-fast)" if provider == "nano-banana" else "DALL-E 3"
        wait_time = "2-5 seconds" if provider == "nano-banana" else "10-20 seconds"
        
        await query.edit_message_text(
            f"🎨 *Generating AI content...*\n\n"
            f"Creating content for all platforms...\n"
            f"Generating image with {provider_name}...\n\n"
            f"_This may take {wait_time}..._",
            parse_mode='Markdown'
        )
        
        try:
            # Generate content using existing service
            result = await generate_platform_content(
                topic=session["topic"],
                tone=session["tone"],
                image_style=session["image_style"],
                generate_image=True,
                use_prompt_enhancer=False,
                image_provider=provider
            )
            
            # Store generated content in session
            session["generated"] = result
            session["approved_platforms"] = []
            session["image_approved"] = False
            
            # Send generated image
            if result["image"]["success"]:
                # Download and send image
                async with httpx.AsyncClient() as client:
                    img_response = await client.get(result["image"]["image_url"])
                    img_path = Path(f"uploads/telegram_temp_{uuid.uuid4().hex[:8]}.png")
                    
                    with open(img_path, "wb") as f:
                        f.write(img_response.content)
                    
                    session["temp_image_path"] = str(img_path)
                    
                    # Send photo with approval buttons
                    keyboard = [
                        [InlineKeyboardButton("✅ Approve Image", callback_data="img_approve"),
                         InlineKeyboardButton("❌ Reject", callback_data="img_reject")],
                        [InlineKeyboardButton("🔄 Regenerate (Choose Provider)", callback_data="img_regenerate")],
                        [InlineKeyboardButton("🔙 Cancel & Start Over", callback_data="img_cancel")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    with open(img_path, "rb") as photo:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=photo,
                            caption="🎨 *AI-Generated Image*\n\nDo you approve this image?",
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
            
            # Send full content for each platform (separately if needed for long content)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="📝 *Generated Content:*\n\nReview the content for each platform below:",
                parse_mode='Markdown'
            )
            
            # Send each platform's content separately to avoid message length limits
            for platform, data in result["platforms"].items():
                if data["success"]:
                    platform_message = f"*{platform.upper()}:*\n\n{data['content']}"
                    
                    # Telegram has 4096 char limit per message
                    if len(platform_message) > 4000:
                        # Split into chunks if too long
                        chunks = [platform_message[i:i+4000] for i in range(0, len(platform_message), 4000)]
                        for i, chunk in enumerate(chunks):
                            await context.bot.send_message(
                                chat_id=update.effective_chat.id,
                                text=chunk if i == 0 else f"_(continued)_\n{chunk}",
                                parse_mode='Markdown'
                            )
                    else:
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=platform_message,
                            parse_mode='Markdown'
                        )
            
            # Platform approval buttons
            keyboard = [
                [InlineKeyboardButton("✅ Approve Facebook", callback_data="plat_approve_facebook"),
                 InlineKeyboardButton("✅ Approve Instagram", callback_data="plat_approve_instagram")],
                [InlineKeyboardButton("✅ Approve Twitter", callback_data="plat_approve_twitter"),
                 InlineKeyboardButton("✅ Approve Reddit", callback_data="plat_approve_reddit")],
                [InlineKeyboardButton("🚀 Continue to Publish", callback_data="plat_done")],
                [InlineKeyboardButton("🔙 Cancel & Start Over", callback_data="plat_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Select platforms to approve:\n(Tap to approve, tap Continue when ready)",
                reply_markup=reply_markup
            )
            
            return APPROVE_PLATFORMS
            
        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Error generating content:\n{str(e)}\n\nUse /start to try again."
            )
            user_sessions.pop(user_id, None)
            return ConversationHandler.END
    
    async def image_approval_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image approval/rejection/regeneration"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        if query.data == "img_approve":
            session["image_approved"] = True
            await query.edit_message_caption(
                caption="✅ *Image Approved!*",
                parse_mode='Markdown'
            )
            return APPROVE_PLATFORMS
        
        elif query.data == "img_cancel":
            # Cancel and restart
            user_sessions[user_id] = {}
            
            keyboard = [
                [InlineKeyboardButton("🤖 Generate AI Content", callback_data="menu_generate")],
                [InlineKeyboardButton("📝 Create Manual Post", callback_data="menu_create")],
                [InlineKeyboardButton("📅 View Scheduled Posts", callback_data="menu_schedule")],
                [InlineKeyboardButton("📊 Platform Status", callback_data="menu_status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🔙 *Process Cancelled*\n\nReturning to main menu...\n\nWhat would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return MENU
        
        elif query.data == "img_reject":
            session["image_approved"] = False
            await query.edit_message_caption(
                caption="❌ Image rejected. Please regenerate or use /cancel",
                parse_mode='Markdown'
            )
            return APPROVE_PLATFORMS
        
        elif query.data == "img_regenerate":
            # Ask user to select provider again for regeneration
            await query.edit_message_caption(
                caption="🔄 *Regenerate Content & Image*\n\nChoose image generator:",
                parse_mode='Markdown'
            )
            
            # Show provider selection
            keyboard = [
                [InlineKeyboardButton("🍌 Nano Banana (Ultra Fast 2-3s)", callback_data="regen_provider_nano-banana")],
                [InlineKeyboardButton("🎨 DALL-E 3 (Premium 15-20s)", callback_data="regen_provider_dalle")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🔄 *Select Image Generator for Regeneration:*\n\n"
                     "🍌 *Nano Banana* - Ultra-fast, great quality\n"
                     "🎨 *DALL-E 3* - Premium quality, slower",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return APPROVE_PLATFORMS
        
        elif query.data.startswith("regen_provider_"):
            # Handle regeneration with selected provider
            provider = query.data.replace("regen_provider_", "")
            session["image_provider"] = provider  # Update provider choice
            
            provider_name = "Nano Banana" if provider == "nano-banana" else "DALL-E 3"
            wait_time = "2-5 seconds" if provider == "nano-banana" else "10-20 seconds"
            
            await query.edit_message_text(
                f"🔄 *Regenerating all content and image...*\n\n"
                f"Using {provider_name}...\n\n"
                f"_This may take {wait_time}..._",
                parse_mode='Markdown'
            )
            
            try:
                result = await generate_platform_content(
                    topic=session["topic"],
                    tone=session["tone"],
                    image_style=session["image_style"],
                    generate_image=True,
                    use_prompt_enhancer=False,
                    image_provider=provider
                )
                
                # Update session with new generated content
                session["generated"] = result
                session["approved_platforms"] = []  # Reset approvals
                session["image_approved"] = False
                
                # Send new image
                if result["image"]["success"]:
                    async with httpx.AsyncClient() as client:
                        img_response = await client.get(result["image"]["image_url"])
                        img_path = Path(f"uploads/telegram_temp_{uuid.uuid4().hex[:8]}.png")
                        
                        # Clean old temp image
                        if session.get("temp_image_path") and os.path.exists(session["temp_image_path"]):
                            os.remove(session["temp_image_path"])
                        
                        with open(img_path, "wb") as f:
                            f.write(img_response.content)
                        
                        session["temp_image_path"] = str(img_path)
                    
                    # Send new photo
                    keyboard = [
                        [InlineKeyboardButton("✅ Approve Image", callback_data="img_approve"),
                         InlineKeyboardButton("❌ Reject", callback_data="img_reject")],
                        [InlineKeyboardButton("🔄 Regenerate (Choose Provider)", callback_data="img_regenerate")],
                        [InlineKeyboardButton("🔙 Cancel & Start Over", callback_data="img_cancel")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    with open(img_path, "rb") as photo:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=photo,
                            caption="🔄 *New Content & Image Generated!*\n\nDo you approve this image?",
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                
                # Send new content for each platform
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="📝 *Regenerated Content:*\n\nReview the new content below:",
                    parse_mode='Markdown'
                )
                
                for platform, data in result["platforms"].items():
                    if data["success"]:
                        platform_message = f"*{platform.upper()}:*\n\n{data['content']}"
                        
                        # Handle long messages
                        if len(platform_message) > 4000:
                            chunks = [platform_message[i:i+4000] for i in range(0, len(platform_message), 4000)]
                            for i, chunk in enumerate(chunks):
                                await context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=chunk if i == 0 else f"_(continued)_\n{chunk}",
                                    parse_mode='Markdown'
                                )
                        else:
                            await context.bot.send_message(
                                chat_id=update.effective_chat.id,
                                text=platform_message,
                                parse_mode='Markdown'
                            )
                
                # Show platform approval buttons
                keyboard = [
                    [InlineKeyboardButton("✅ Approve Facebook", callback_data="plat_approve_facebook"),
                     InlineKeyboardButton("✅ Approve Instagram", callback_data="plat_approve_instagram")],
                    [InlineKeyboardButton("✅ Approve Twitter", callback_data="plat_approve_twitter"),
                     InlineKeyboardButton("✅ Approve Reddit", callback_data="plat_approve_reddit")],
                    [InlineKeyboardButton("🚀 Continue to Publish", callback_data="plat_done")],
                    [InlineKeyboardButton("🔙 Cancel & Start Over", callback_data="plat_cancel")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Select platforms to approve:\n(Tap to approve, tap Continue when ready)",
                    reply_markup=reply_markup
                )
                
                return APPROVE_PLATFORMS
            
            except Exception as e:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Failed to regenerate: {str(e)}\n\nUse /cancel to start over."
                )
                return APPROVE_PLATFORMS
        
        return APPROVE_PLATFORMS
    
    async def platform_approval_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle platform approval/disapproval"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        if query.data.startswith("plat_approve_"):
            platform = query.data.replace("plat_approve_", "")
            
            # Toggle approval
            if platform in session.get("approved_platforms", []):
                session["approved_platforms"].remove(platform)
                await query.answer("❌ Removed from approval")
            else:
                session.setdefault("approved_platforms", []).append(platform)
                await query.answer(f"✅ {platform.title()} approved!")
            
            # Update message with current approvals
            approved = session.get("approved_platforms", [])
            keyboard = [
                [InlineKeyboardButton(
                    f"{'✅' if 'facebook' in approved else '⬜'} Facebook", 
                    callback_data="plat_approve_facebook"
                ),
                 InlineKeyboardButton(
                    f"{'✅' if 'instagram' in approved else '⬜'} Instagram", 
                    callback_data="plat_approve_instagram"
                )],
                [InlineKeyboardButton(
                    f"{'✅' if 'twitter' in approved else '⬜'} Twitter", 
                    callback_data="plat_approve_twitter"
                ),
                 InlineKeyboardButton(
                    f"{'✅' if 'reddit' in approved else '⬜'} Reddit", 
                    callback_data="plat_approve_reddit"
                )],
                [InlineKeyboardButton("🚀 Continue to Publish", callback_data="plat_done")],
                [InlineKeyboardButton("🔙 Cancel & Start Over", callback_data="plat_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            approved_text = f"Approved: {len(approved)} platforms" if approved else "No platforms approved yet"
            
            await query.edit_message_text(
                f"Select platforms to approve:\n\n"
                f"*{approved_text}*\n\n"
                f"Tap platforms to toggle, then Continue",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return APPROVE_PLATFORMS
        
        elif query.data == "plat_cancel":
            # Cancel and restart
            user_sessions[user_id] = {}
            
            keyboard = [
                [InlineKeyboardButton("🤖 Generate AI Content", callback_data="menu_generate")],
                [InlineKeyboardButton("📝 Create Manual Post", callback_data="menu_create")],
                [InlineKeyboardButton("📅 View Scheduled Posts", callback_data="menu_schedule")],
                [InlineKeyboardButton("📊 Platform Status", callback_data="menu_status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🔙 *Process Cancelled*\n\nReturning to main menu...\n\nWhat would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return MENU
        
        elif query.data == "plat_done":
            approved = session.get("approved_platforms", [])
            image_approved = session.get("image_approved", False)
            
            if not approved:
                await query.answer("⚠️ Please approve at least one platform!", show_alert=True)
                return APPROVE_PLATFORMS
            
            if not image_approved:
                await query.answer("⚠️ Please approve the image first!", show_alert=True)
                return APPROVE_PLATFORMS
            
            # Show publish options
            keyboard = [
                [InlineKeyboardButton("🚀 Publish Now", callback_data="publish_now")],
                [InlineKeyboardButton("📅 Schedule for Later", callback_data="publish_schedule")],
                [InlineKeyboardButton("🔙 Cancel & Start Over", callback_data="publish_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✅ Ready to publish!\n\n"
                f"*Approved Platforms:* {len(approved)}\n"
                f"• {', '.join([p.title() for p in approved])}\n\n"
                f"*Image:* Approved ✅\n\n"
                f"What would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return APPROVE_PLATFORMS
        
        elif query.data == "publish_cancel":
            # Cancel and restart
            user_sessions[user_id] = {}
            
            keyboard = [
                [InlineKeyboardButton("🤖 Generate AI Content", callback_data="menu_generate")],
                [InlineKeyboardButton("📝 Create Manual Post", callback_data="menu_create")],
                [InlineKeyboardButton("📅 View Scheduled Posts", callback_data="menu_schedule")],
                [InlineKeyboardButton("📊 Platform Status", callback_data="menu_status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🔙 *Process Cancelled*\n\nReturning to main menu...\n\nWhat would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return MENU
        
        elif query.data == "publish_now":
            await self.publish_content(update, context, scheduled=False)
            return ConversationHandler.END
        
        elif query.data == "publish_schedule":
            await query.edit_message_text(
                "📅 *Schedule Post*\n\n"
                "Send date and time in format:\n"
                "`YYYY-MM-DD HH:MM`\n\n"
                "*Examples:*\n"
                "• `2025-10-10 14:30`\n"
                "• `2025-10-15 09:00`\n\n"
                "_Or use quick options:_",
                parse_mode='Markdown'
            )
            
            # Quick schedule buttons
            now = datetime.now()
            keyboard = [
                [InlineKeyboardButton("In 1 hour", callback_data=f"quick_{(now + timedelta(hours=1)).isoformat()}")],
                [InlineKeyboardButton("In 3 hours", callback_data=f"quick_{(now + timedelta(hours=3)).isoformat()}")],
                [InlineKeyboardButton("Tomorrow 9 AM", callback_data=f"quick_{(now + timedelta(days=1)).replace(hour=9, minute=0).isoformat()}")],
                [InlineKeyboardButton("« Back", callback_data="back_publish")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Or choose a quick option:",
                reply_markup=reply_markup
            )
            
            return SCHEDULE_TIME
        
        elif query.data == "cancel":
            user_id = update.effective_user.id
            # Clean up temp files
            if session.get("temp_image_path") and os.path.exists(session["temp_image_path"]):
                os.remove(session["temp_image_path"])
            user_sessions.pop(user_id, None)
            await query.edit_message_text("❌ Cancelled. Use /start to begin again.")
            return ConversationHandler.END
        
        return APPROVE_PLATFORMS
    
    async def schedule_time_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle scheduling time input"""
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        # Check if it's a callback (quick option) or message (custom time)
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data.startswith("quick_"):
                scheduled_time = query.data.replace("quick_", "")
                await self.schedule_post(update, context, scheduled_time)
                return ConversationHandler.END
        else:
            # Parse custom time input
            time_str = update.message.text.strip()
            
            try:
                # Parse format: YYYY-MM-DD HH:MM
                scheduled_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                
                if scheduled_dt <= datetime.now():
                    await update.message.reply_text(
                        "⚠️ Time must be in the future!\n\n"
                        "Please send again:"
                    )
                    return SCHEDULE_TIME
                
                scheduled_time = scheduled_dt.isoformat()
                await self.schedule_post(update, context, scheduled_time)
                return ConversationHandler.END
                
            except ValueError:
                await update.message.reply_text(
                    "❌ Invalid format!\n\n"
                    "Please use: `YYYY-MM-DD HH:MM`\n"
                    "Example: `2025-10-10 14:30`",
                    parse_mode='Markdown'
                )
                return SCHEDULE_TIME
        
        return SCHEDULE_TIME
    
    async def publish_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE, scheduled=False):
        """Publish content to approved platforms"""
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        query = update.callback_query if update.callback_query else None
        if query:
            await query.edit_message_text("🚀 Publishing to platforms...")
        
        generated = session.get("generated", {})
        approved_platforms = session.get("approved_platforms", [])
        img_path = session.get("temp_image_path")
        
        results = []
        success_count = 0
        
        # Post to each approved platform
        for platform in approved_platforms:
            platform_content = generated["platforms"].get(platform, {})
            if not platform_content.get("success"):
                continue
            
            caption = platform_content["content"]
            
            try:
                if platform == "facebook":
                    await post_photo_to_facebook(img_path, caption)
                    results.append(f"✅ Facebook")
                    success_count += 1
                elif platform == "instagram":
                    await post_photo_to_instagram(img_path, caption)
                    results.append(f"✅ Instagram")
                    success_count += 1
                elif platform == "twitter":
                    await post_photo_to_twitter(img_path, caption)
                    results.append(f"✅ Twitter")
                    success_count += 1
                elif platform == "reddit":
                    await post_photo_to_reddit(img_path, caption)
                    results.append(f"✅ Reddit")
                    success_count += 1
            except Exception as e:
                results.append(f"❌ {platform.title()}: {str(e)}")
        
        # Clean up temp image
        if img_path and os.path.exists(img_path):
            os.remove(img_path)
        
        # Send results
        result_message = f"🎉 *Publishing Complete!*\n\n" + "\n".join(results)
        result_message += f"\n\nPosted to {success_count}/{len(approved_platforms)} platforms"
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result_message,
            parse_mode='Markdown'
        )
        
        # Clear session
        user_sessions.pop(user_id, None)
    
    async def schedule_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE, scheduled_time: str):
        """Schedule a post for later"""
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        generated = session.get("generated", {})
        approved_platforms = session.get("approved_platforms", [])
        img_path = session.get("temp_image_path")
        
        # Create scheduled post for each approved platform
        for platform in approved_platforms:
            platform_content = generated["platforms"].get(platform, {})
            if not platform_content.get("success"):
                continue
            
            caption = platform_content["content"]
            
            # Create post ID
            post_id = str(uuid.uuid4())
            
            # Save post info
            scheduled_post = {
                "id": post_id,
                "caption": caption,
                "image_path": img_path,
                "platforms": {platform: True},
                "scheduled_time": scheduled_time,
                "created_at": datetime.now().isoformat(),
                "status": "scheduled",
                "source": "telegram"
            }
            
            posts = load_scheduled_posts()
            posts.append(scheduled_post)
            save_scheduled_posts(posts)
            
            # Schedule the job
            schedule_dt = datetime.fromisoformat(scheduled_time)
            scheduler.add_job(
                func=execute_scheduled_post,
                trigger=DateTrigger(run_date=schedule_dt),
                args=[post_id, img_path, caption, {platform: True}],
                id=post_id,
                replace_existing=True
            )
        
        formatted_time = datetime.fromisoformat(scheduled_time).strftime("%b %d, %Y at %I:%M %p")
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ *Scheduled Successfully!*\n\n"
                 f"📅 {formatted_time}\n"
                 f"📱 Platforms: {', '.join([p.title() for p in approved_platforms])}\n\n"
                 f"You'll be notified when posted!",
            parse_mode='Markdown'
        )
        
        # Clear session (but don't delete image yet - scheduler needs it)
        user_sessions.pop(user_id, None)
    
    # ==================== MANUAL POST CREATION ====================
    
    async def create_image_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image upload for manual post"""
        user_id = update.effective_user.id
        
        # Get photo
        if update.message.photo:
            photo = update.message.photo[-1]  # Get largest size
            file = await context.bot.get_file(photo.file_id)
            
            # Download and save
            img_path = Path(f"uploads/telegram_{uuid.uuid4().hex[:8]}.jpg")
            await file.download_to_drive(img_path)
            
            # Initialize session
            user_sessions[user_id] = {
                "mode": "manual",
                "image_path": str(img_path)
            }
            
            await update.message.reply_text(
                "✅ *Image Received!*\n\n"
                "Now send me your caption text:",
                parse_mode='Markdown'
            )
            return CREATE_CAPTION
        else:
            await update.message.reply_text(
                "⚠️ Please send an image.\n\n"
                "You can send a photo or upload an image file."
            )
            return CREATE_IMAGE
    
    async def create_caption_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle caption input for manual post"""
        user_id = update.effective_user.id
        caption = update.message.text
        
        session = user_sessions.get(user_id, {})
        session["caption"] = caption
        
        # Platform selection
        keyboard = [
            [InlineKeyboardButton("⬜ Facebook", callback_data="manual_plat_facebook"),
             InlineKeyboardButton("⬜ Instagram", callback_data="manual_plat_instagram")],
            [InlineKeyboardButton("⬜ Twitter", callback_data="manual_plat_twitter"),
             InlineKeyboardButton("⬜ Reddit", callback_data="manual_plat_reddit")],
            [InlineKeyboardButton("🚀 Continue", callback_data="manual_done")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ Caption saved!\n\n"
            f"Select platforms to post to:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return CREATE_PLATFORMS
    
    async def manual_platform_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle platform selection for manual post"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        if query.data.startswith("manual_plat_"):
            platform = query.data.replace("manual_plat_", "")
            
            # Toggle selection
            selected = session.setdefault("selected_platforms", [])
            if platform in selected:
                selected.remove(platform)
                await query.answer(f"❌ {platform.title()} removed")
            else:
                selected.append(platform)
                await query.answer(f"✅ {platform.title()} added!")
            
            # Update buttons
            keyboard = [
                [InlineKeyboardButton(
                    f"{'✅' if 'facebook' in selected else '⬜'} Facebook", 
                    callback_data="manual_plat_facebook"
                ),
                 InlineKeyboardButton(
                    f"{'✅' if 'instagram' in selected else '⬜'} Instagram", 
                    callback_data="manual_plat_instagram"
                )],
                [InlineKeyboardButton(
                    f"{'✅' if 'twitter' in selected else '⬜'} Twitter", 
                    callback_data="manual_plat_twitter"
                ),
                 InlineKeyboardButton(
                    f"{'✅' if 'reddit' in selected else '⬜'} Reddit", 
                    callback_data="manual_plat_reddit"
                )],
                [InlineKeyboardButton("🚀 Continue", callback_data="manual_done")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            selected_text = f"{len(selected)} platforms selected" if selected else "No platforms selected"
            
            await query.edit_message_text(
                f"Select platforms:\n\n*{selected_text}*",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return CREATE_PLATFORMS
        
        elif query.data == "manual_done":
            selected = session.get("selected_platforms", [])
            
            if not selected:
                await query.answer("⚠️ Select at least one platform!", show_alert=True)
                return CREATE_PLATFORMS
            
            # Show publish options
            keyboard = [
                [InlineKeyboardButton("🚀 Post Now", callback_data="manual_publish_now")],
                [InlineKeyboardButton("📅 Schedule", callback_data="manual_publish_schedule")],
                [InlineKeyboardButton("🔙 Cancel & Start Over", callback_data="manual_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✅ Ready!\n\n"
                f"*Platforms:* {', '.join([p.title() for p in selected])}\n\n"
                f"What would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return CREATE_PLATFORMS
        
        elif query.data == "manual_publish_now":
            await self.publish_manual_post(update, context, scheduled=False)
            return ConversationHandler.END
        
        elif query.data == "manual_publish_schedule":
            await query.edit_message_text(
                "📅 *Schedule Post*\n\n"
                "Send date and time:\n"
                "`YYYY-MM-DD HH:MM`",
                parse_mode='Markdown'
            )
            return SCHEDULE_TIME
        
        elif query.data == "manual_cancel":
            # Cancel and restart
            user_sessions[user_id] = {}
            
            keyboard = [
                [InlineKeyboardButton("🤖 Generate AI Content", callback_data="menu_generate")],
                [InlineKeyboardButton("📝 Create Manual Post", callback_data="menu_create")],
                [InlineKeyboardButton("📅 View Scheduled Posts", callback_data="menu_schedule")],
                [InlineKeyboardButton("📊 Platform Status", callback_data="menu_status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🔙 *Process Cancelled*\n\nReturning to main menu...\n\nWhat would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return MENU
        
        return CREATE_PLATFORMS
    
    async def publish_manual_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE, scheduled=False):
        """Publish manual post immediately"""
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        query = update.callback_query
        await query.edit_message_text("🚀 Publishing...")
        
        caption = session.get("caption", "")
        img_path = session.get("image_path")
        selected = session.get("selected_platforms", [])
        
        results = []
        success_count = 0
        
        for platform in selected:
            try:
                if platform == "facebook":
                    await post_photo_to_facebook(img_path, caption)
                    results.append(f"✅ Facebook")
                    success_count += 1
                elif platform == "instagram":
                    await post_photo_to_instagram(img_path, caption)
                    results.append(f"✅ Instagram")
                    success_count += 1
                elif platform == "twitter":
                    await post_photo_to_twitter(img_path, caption)
                    results.append(f"✅ Twitter")
                    success_count += 1
                elif platform == "reddit":
                    await post_photo_to_reddit(img_path, caption)
                    results.append(f"✅ Reddit")
                    success_count += 1
            except Exception as e:
                results.append(f"❌ {platform.title()}: Error")
        
        # Clean up
        if img_path and os.path.exists(img_path):
            os.remove(img_path)
        
        result_message = f"🎉 *Posted!*\n\n" + "\n".join(results)
        result_message += f"\n\n{success_count}/{len(selected)} successful"
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result_message,
            parse_mode='Markdown'
        )
        
        user_sessions.pop(user_id, None)
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command"""
        user_id = update.effective_user.id
        session = user_sessions.pop(user_id, None)
        
        # Clean up temp files
        if session and session.get("temp_image_path"):
            if os.path.exists(session["temp_image_path"]):
                os.remove(session["temp_image_path"])
        
        await update.message.reply_text(
            "❌ Operation cancelled.\n\n"
            "Use /start to begin again."
        )
        return ConversationHandler.END
    
    # ==================== BOT SETUP ====================
    
    def build_application(self):
        """Build and configure the bot application"""
        if not settings.TELEGRAM_BOT_TOKEN:
            print("⚠️ TELEGRAM_BOT_TOKEN not configured. Bot will not start.")
            return None
        
        # Create application
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Main conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_command)],
            states={
                MENU: [CallbackQueryHandler(self.menu_handler)],
                GENERATE_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.generate_topic_handler)],
                GENERATE_TONE: [CallbackQueryHandler(self.generate_tone_handler)],
                GENERATE_PROVIDER: [CallbackQueryHandler(self.generate_provider_handler)],
                GENERATE_STYLE: [CallbackQueryHandler(self.generate_style_handler)],
                APPROVE_PLATFORMS: [
                    CallbackQueryHandler(self.image_approval_handler, pattern="^img_"),
                    CallbackQueryHandler(self.image_approval_handler, pattern="^regen_provider_"),
                    CallbackQueryHandler(self.platform_approval_handler)
                ],
                CREATE_IMAGE: [MessageHandler(filters.PHOTO, self.create_image_handler)],
                CREATE_CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.create_caption_handler)],
                CREATE_PLATFORMS: [CallbackQueryHandler(self.manual_platform_handler)],
                SCHEDULE_TIME: [
                    CallbackQueryHandler(self.schedule_time_handler, pattern="^quick_"),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.schedule_time_handler)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel_command)],
        )
        
        self.application.add_handler(conv_handler)
        
        print("✅ Telegram bot handlers configured")
        return self.application
    
    async def start_bot(self):
        """Start the Telegram bot and keep it running"""
        if not self.application:
            self.build_application()
        
        if self.application:
            print("🤖 Starting Telegram bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)
            print(f"✅ Telegram bot started successfully!")
            print(f"📱 Open Telegram and search for your bot")
            print(f"⏳ Bot is running... Press Ctrl+C to stop")
            
            # Keep the bot running (idle mode)
            try:
                # Run indefinitely until interrupted
                stop_event = asyncio.Event()
                await stop_event.wait()
            except asyncio.CancelledError:
                pass
        else:
            print("❌ Telegram bot not configured")
    
    async def stop_bot(self):
        """Stop the Telegram bot"""
        if self.application:
            print("🛑 Stopping Telegram bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            print("✅ Telegram bot stopped")


# Global bot instance
telegram_bot = TelegramBotService()

