# 🤖 AI Content Generator Guide

## Overview

The AI Content Generator uses **OpenAI's GPT-4** to create platform-specific social media content. It generates optimized posts for Facebook, Instagram, Twitter, and Reddit all at once!

## ✨ Features

### **Multi-Platform Generation**
- Generates 4 different versions simultaneously
- Each version optimized for its platform
- Platform-specific style, length, and hashtags

### **Tone Selection**
- 😊 **Casual** - Friendly and approachable
- 💼 **Professional** - Business and formal
- 😄 **Funny** - Humorous and entertaining  
- ✨ **Inspirational** - Motivational and uplifting

### **Editable Content**
- Edit any generated content
- Real-time character count
- Platform-specific guidelines

### **Direct Integration**
- Click "Use in Create Page" to auto-fill
- Seamless workflow from generate → create → post

---

## 🎯 How to Use

### **Step 1: Navigate to Generator**
Click "🤖 Generate" in the navigation bar

### **Step 2: Enter Your Prompt**
```
Example prompts:
- "Launching our new eco-friendly water bottle"
- "Behind-the-scenes of our creative process"
- "Motivational quote about perseverance"
- "Announcing our summer sale - 30% off"
```

### **Step 3: Select Tone**
Choose from:
- Casual
- Professional
- Funny
- Inspirational

### **Step 4: Generate**
Click "✨ GENERATE CONTENT" button

### **Step 5: Review & Edit**
- See 4 versions (one per platform)
- Edit any content directly
- Character counts shown
- Platform-specific optimizations visible

### **Step 6: Use Content**
- Click "Use in Create Page →" on any platform
- You'll be redirected to Create page with content pre-filled
- Upload image and post/schedule!

---

## 📱 Platform-Specific Optimization

### **Facebook**
- Max: 500 characters
- Style: Conversational and friendly
- Hashtags: 2-3 (optional)
- Tone: Can be longer and more detailed

### **Instagram**
- Max: 400 characters
- Style: Visual and engaging with emojis
- Hashtags: 5-10 relevant hashtags
- Tone: Aesthetic and inspiring

### **Twitter**
- Max: 260 characters
- Style: Concise and punchy
- Hashtags: 1-3 hashtags
- Tone: Sharp and to the point

### **Reddit**
- Max: 300 characters
- Style: Authentic and community-focused
- Hashtags: Avoided (Reddit doesn't use hashtags)
- Tone: Genuine, no spam

---

## 🔧 Technical Details

### **Backend API**

**Endpoint**: `POST /api/generate-content`

**Request**:
```json
{
  "topic": "your topic here",
  "tone": "casual"
}
```

**Response**:
```json
{
  "success": true,
  "platforms": {
    "facebook": {
      "content": "Generated Facebook post...",
      "success": true,
      "character_count": 245
    },
    "instagram": {
      "content": "Generated Instagram post... #hashtags",
      "success": true,
      "character_count": 312
    },
    // ... twitter, reddit
  }
}
```

### **AI Model**
- **Model**: GPT-4o-mini (fast and cost-effective)
- **Temperature**: 0.8 (creative but controlled)
- **Max Tokens**: 300 per platform

### **Configuration**
API key stored in `.env`:
```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

---

## 💡 Tips for Best Results

### **Be Specific**
❌ Bad: "post about product"
✅ Good: "eco-friendly reusable water bottle with temperature control"

### **Include Key Details**
❌ Bad: "sale announcement"
✅ Good: "summer sale - 30% off all items, ends Friday"

### **Mention Target Audience**
❌ Bad: "motivational quote"
✅ Good: "motivational quote for entrepreneurs starting their journey"

### **Try Different Tones**
- Same topic with different tones = different engagement
- Test what resonates with your audience

---

## 🔄 Workflow

```
1. Generate Page
   └─ Enter prompt
   └─ Select tone
   └─ Click Generate
   └─ AI creates 4 versions
   └─ Edit as needed
   └─ Click "Use in Create Page"
      ↓
2. Create Page
   └─ Content pre-filled
   └─ Upload image
   └─ Post now or Schedule
      ↓
3. Posted to platforms!
```

---

## ⚡ Quick Examples

### Example 1: Product Launch
**Prompt**: "Launching our new AI-powered smart home device"
**Tone**: Professional

**Results**:
- Facebook: Detailed features and benefits
- Instagram: Visual appeal with emojis and hashtags
- Twitter: Short, punchy announcement
- Reddit: Technical details, community-focused

### Example 2: Motivational Content
**Prompt**: "Never give up on your dreams"
**Tone**: Inspirational

**Results**:
- Facebook: Story-based, longer format
- Instagram: Quote with aesthetic emojis
- Twitter: Concise wisdom
- Reddit: Authentic encouragement

---

## 🎨 YouTube-Style UI

- Clean white cards
- Platform-specific color accents
- Editable text areas
- Clear character counts
- One-click usage

---

## 🚀 Benefits

✅ **Save Time** - Generate 4 posts in seconds
✅ **Platform Optimization** - Each post tailored
✅ **Consistency** - Same message, different formats
✅ **Inspiration** - Get ideas when you're stuck
✅ **Professional Quality** - AI-powered writing

---

## 📊 Cost Estimate

Using GPT-4o-mini:
- ~$0.01 per generation (4 platforms)
- Very cost-effective
- Fast responses

---

Start generating amazing content! 🤖✨

