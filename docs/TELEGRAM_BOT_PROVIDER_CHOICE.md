# 🤖 Telegram Bot - Image Provider Choice

## Overview

Added image provider selection to Telegram bot, giving users the choice between **Nano Banana (Fal.ai)** and **DALL-E 3** for image generation.

## User Flow in Telegram Bot

### **Complete Generation Flow:**

```
1. User: /start
   Bot: [Main Menu]

2. User: Clicks "Generate AI Content"
   Bot: "Enter your topic"

3. User: "Coffee shop launch"
   Bot: Shows tone options

4. User: Clicks "Casual"
   Bot: Shows IMAGE PROVIDER options:
        🍌 Nano Banana (Ultra Fast 2-3s)
        🎨 DALL-E 3 (Premium 15-20s)

5. User: Clicks "🍌 Nano Banana"
   Bot: Shows image style options

6. User: Clicks "Realistic"
   Bot: "Generating with Nano Banana... (2-5 seconds)"

7. Bot: Sends image + content (ultra-fast!)

8. User: Can approve/regenerate/schedule
```

---

## 🎯 **New Conversation State**

### **Added State:**
```python
GENERATE_PROVIDER  # Between GENERATE_TONE and GENERATE_STYLE
```

### **Complete Flow:**
```
MENU → GENERATE_TOPIC → GENERATE_TONE → GENERATE_PROVIDER → GENERATE_STYLE → APPROVE_PLATFORMS
```

---

## 📝 **Implementation Details**

### **File:** `app/services/telegram_bot_service.py`

### **1. Updated States (Line 32)**
```python
(MENU, GENERATE_TOPIC, GENERATE_TONE, GENERATE_PROVIDER, GENERATE_STYLE, 
 APPROVE_PLATFORMS, CREATE_CAPTION, CREATE_IMAGE, CREATE_PLATFORMS, 
 SCHEDULE_TIME, VIEW_SCHEDULE_DETAIL) = range(11)
```

### **2. New Handler: `generate_provider_handler` (Lines 241-270)**

Shows provider selection buttons:
```python
keyboard = [
    [InlineKeyboardButton("🍌 Nano Banana (Ultra Fast 2-3s)", callback_data="provider_nano-banana")],
    [InlineKeyboardButton("🎨 DALL-E 3 (Premium 15-20s)", callback_data="provider_dalle")]
]
```

Stores selection:
```python
provider = query.data.replace("provider_", "")
user_sessions[user_id]["image_provider"] = provider
```

### **3. Updated `generate_style_handler` (Lines 282-304)**

Uses selected provider:
```python
provider = session.get("image_provider", "dalle")
provider_name = "Nano Banana (ultra-fast)" if provider == "nano-banana" else "DALL-E 3"
wait_time = "2-5 seconds" if provider == "nano-banana" else "10-20 seconds"

# Shows provider in generation message
await query.edit_message_text(
    f"Generating image with {provider_name}...\n"
    f"This may take {wait_time}..."
)

# Passes provider to generation function
result = await generate_platform_content(
    topic=session["topic"],
    tone=session["tone"],
    image_style=session["image_style"],
    generate_image=True,
    use_prompt_enhancer=False,
    image_provider=provider  # ← NEW
)
```

### **4. Updated Regenerate Handler (Lines 428-445)**

Also uses stored provider for regeneration:
```python
provider = session.get("image_provider", "dalle")
result = await generate_platform_content(
    ...,
    image_provider=provider
)
```

### **5. Updated Welcome Message (Lines 58-69)**

```
Features:
• AI content generation (Nano Banana or DALL-E)  ← Updated
```

---

## 🎨 **Visual Flow in Telegram**

### **Step 4: Provider Selection Screen**

```
✅ Tone: Casual

Select image generator:

🍌 Nano Banana - Ultra-fast, great quality
🎨 DALL-E 3 - Premium quality, slower

┌──────────────────────────────────────┐
│  🍌 Nano Banana (Ultra Fast 2-3s)   │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│  🎨 DALL-E 3 (Premium 15-20s)       │
└──────────────────────────────────────┘
```

### **Generation Message (Nano Banana)**

```
🎨 Generating AI content...

Creating content for all platforms...
Generating image with Nano Banana (ultra-fast)...

This may take 2-5 seconds...
```

### **Generation Message (DALL-E 3)**

```
🎨 Generating AI content...

Creating content for all platforms...
Generating image with DALL-E 3...

This may take 10-20 seconds...
```

---

## 🔄 **Regeneration Flow**

When user clicks "🔄 Regenerate All Again":

1. **Bot checks** stored provider from session
2. **Shows message**: "Using Nano Banana..." or "Using DALL-E 3..."
3. **Generates** with same provider as original
4. **Maintains consistency** in the conversation

---

## 📊 **Session Storage**

```python
user_sessions[user_id] = {
    "topic": "Coffee shop launch",
    "tone": "casual",
    "image_provider": "nano-banana",  # ← NEW: Stored choice
    "image_style": "realistic",
    "generated": {...},
    "approved_platforms": [],
    "image_approved": False
}
```

---

## ✅ **Benefits**

### **For Users**
✅ **Same choice as web app** - Consistent experience  
✅ **Speed control** - Pick fast vs premium  
✅ **Transparent** - See which provider is being used  
✅ **Smart regeneration** - Remembers provider choice  

### **For Bot**
✅ **User preference** - Remembers choice per session  
✅ **Clear messaging** - Shows expected wait time  
✅ **Consistent prompts** - Both providers use same system prompts  
✅ **Error handling** - Falls back gracefully  

---

## 🧪 **Testing**

### **Test Nano Banana:**
1. Start bot: `python bot.py`
2. Message bot: `/start`
3. Click: "Generate AI Content"
4. Enter: "Beautiful sunset"
5. Select tone: "Casual"
6. **Select: "🍌 Nano Banana"**
7. Select style: "Realistic"
8. Watch: Image in 2-3 seconds! ⚡

### **Test DALL-E 3:**
1. Same steps as above
2. **Select: "🎨 DALL-E 3"**
3. Watch: Image in 15-20 seconds

### **Test Regeneration:**
1. After generation, click "🔄 Regenerate All"
2. Bot uses same provider as before
3. New image generated with same provider

---

## 📋 **Files Modified**

- ✅ `app/services/telegram_bot_service.py`
  - Added GENERATE_PROVIDER state
  - Added generate_provider_handler
  - Updated generate_style_handler to use provider
  - Updated regenerate handler to use provider
  - Updated welcome message

---

## 🎯 **Complete Bot Flow Now**

```
/start
  ↓
Main Menu
  ↓
Generate AI Content
  ↓
Enter Topic: "Coffee shop"
  ↓
Select Tone: "Casual"
  ↓
Select Provider: "🍌 Nano Banana" or "🎨 DALL-E 3"  ← NEW STEP
  ↓
Select Style: "Realistic"
  ↓
Generate (2-3s or 15-20s depending on provider)
  ↓
Approve & Publish
```

---

## 🚀 **Ready to Use!**

Start the bot:
```bash
python bot.py
```

Users can now choose between ultra-fast Nano Banana and premium DALL-E 3! 🍌🎨

---

**Created**: October 14, 2025  
**Status**: Production Ready ✅

