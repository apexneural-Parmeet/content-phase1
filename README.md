# 🎯 Social Hub - Multi-Platform Social Media Manager

A powerful, AI-enhanced social media management platform that lets you create, schedule, and publish content to multiple platforms simultaneously.

## ✨ Key Features

- **AI Content Generation** - GPT-4 powered content creation with platform-specific optimization
- **DALL-E Image Generation** - AI-generated images in multiple artistic styles
- **Smart Prompt Enhancement** - Automatically improves your prompts for better results
- **Multi-Platform Publishing** - Post to Facebook, Instagram, Twitter, and Reddit
- **Intelligent Scheduling** - Schedule posts with precise date/time control
- **Content Persistence** - Never lose your generated content when navigating
- **Approval Workflow** - Review and approve content before publishing
- **8 Content Tones** - Casual, Professional, Corporate Minimal, Funny, Inspirational, Educational, Storytelling, Promotional
- **9 Image Styles** - Realistic, Minimal, Anime, 2D Art, Comic Book, Sketch, Vintage, Disney, 3D Render

## 📁 Project Structure

```
social-hub/
├── app/                      # Backend application
│   ├── clients/             # Social media API clients
│   ├── config.py           # Configuration settings
│   ├── main.py             # FastAPI application entry
│   ├── models/             # Pydantic schemas
│   ├── routes/             # API endpoints
│   │   ├── ai_content.py  # AI generation endpoints
│   │   ├── health.py      # Health check & platform verification
│   │   ├── posts.py       # Post creation & management
│   │   └── scheduled.py   # Scheduler management
│   ├── scheduler/          # Background job scheduler
│   ├── services/           # Business logic
│   │   ├── ai_service.py  # OpenAI integration
│   │   ├── facebook_service.py
│   │   ├── instagram_service.py
│   │   ├── twitter_service.py
│   │   └── reddit_service.py
│   └── utils/              # Helper functions
│
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   │   ├── Logo.jsx
│   │   │   ├── Navigation.jsx
│   │   │   └── SocialIcons.jsx
│   │   ├── context/        # React contexts
│   │   │   └── GeneratedContentContext.jsx
│   │   ├── pages/          # Page components
│   │   │   ├── LandingPage.jsx
│   │   │   ├── GeneratorPage.jsx
│   │   │   ├── HomePage.jsx
│   │   │   └── SchedulerPage.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── docs/                    # Documentation
│   ├── AI_GENERATOR_GUIDE.md
│   ├── BACKEND_ARCHITECTURE.md
│   ├── PUBLISH_TO_ALL_FEATURE.md
│   ├── SCHEDULER_GUIDE.md
│   ├── TONE_AND_STYLE_GUIDE.md
│   └── ...
│
├── logs/                    # Server logs
│   └── server.log
│
├── scripts/                 # Utility scripts
│   ├── start_server.sh     # Start backend
│   ├── stop_server.sh      # Stop all servers
│   ├── start_frontend.sh   # Start frontend
│   └── dev.sh              # Start full dev environment
│
├── uploads/                 # Uploaded files
│   └── ai_generated/       # AI-generated images
│
├── .env                     # Environment variables (create this!)
├── .gitignore              # Git ignore rules
├── requirements.txt         # Python dependencies
├── run.py                  # Application entry point
└── scheduled_posts.json    # Scheduled posts database
```

## 🚀 Quick Start

### 1. Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Facebook
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_access_token

# Instagram
INSTAGRAM_ACCOUNT_ID=your_account_id
INSTAGRAM_ACCESS_TOKEN=your_access_token

# Twitter
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Reddit
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
REDDIT_USER_AGENT=your_app_name

# Cloudinary (for Instagram)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 3. Start the Application

**Option A: Use convenience scripts**
```bash
# Start backend
./scripts/start_server.sh

# Start frontend (in new terminal)
./scripts/start_frontend.sh
```

**Option B: Manual start**
```bash
# Backend
python run.py

# Frontend (in new terminal)
cd frontend
npm run dev
```

**Option C: Development mode (both at once)**
```bash
./scripts/dev.sh
# Then in new terminal: cd frontend && npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 Usage Guide

### Workflow 1: AI-Generated Content

1. **Navigate to Generate page**
2. **Enter your topic/idea** (e.g., "New product launch")
3. **Select content tone** (e.g., Professional, Funny, Corporate Minimal)
4. **Select image style** (e.g., Realistic, Anime, Minimal)
5. **Enable AI Prompt Enhancer** (recommended - on by default)
6. **Click "Generate Content"**
7. **Review** AI-enhanced prompts, generated content, and image
8. **Approve/Reject/Regenerate** for each platform
9. **Approve the image**
10. **Publish**:
    - Click "Publish to All Approved" for immediate posting
    - Click "Schedule All Approved" to schedule for later

### Workflow 2: Manual Content Creation

1. **Navigate to Create page**
2. **Write your caption**
3. **Upload an image**
4. **Select platforms** (checkboxes)
5. **Toggle "Schedule Post"** if you want to schedule
6. **Click "Post to All Platforms"** or "Schedule Post"

### Workflow 3: Manage Scheduled Posts

1. **Navigate to Scheduler page**
2. **View** scheduled posts in calendar or list format
3. **Delete** posts if needed
4. Posts automatically publish at scheduled time

## 🎨 Content Tones

| Tone | Description | Best For |
|------|-------------|----------|
| **Casual** | Friendly and relaxed | Community engagement |
| **Professional** | Business-like and formal | Corporate announcements |
| **Corporate Minimal** | Ultra-brief, clean text | Apple/Tesla-style posts |
| **Funny** | Humorous and hilarious | Viral entertainment |
| **Inspirational** | Motivational and uplifting | Quotes, success stories |
| **Educational** | Informative and teaching | How-to guides |
| **Storytelling** | Narrative and engaging | Brand stories |
| **Promotional** | Sales-focused | Product launches |

## 🖼️ Image Styles

| Style | Description | Visual Effect |
|-------|-------------|--------------|
| **Realistic** | Photo-realistic | Professional photography |
| **Minimal Clean** | Ultra-minimalist | Apple-style simplicity |
| **Anime** | Japanese anime style | Vibrant cel-shaded art |
| **2D Art** | Flat illustration | Modern vector graphics |
| **Comic Book** | Comic art style | Bold outlines & colors |
| **Sketch** | Hand-drawn | Artistic pencil work |
| **Vintage** | Retro look | Nostalgic 1950s-80s |
| **Disney** | Disney animation | Pixar-style 3D cartoon |
| **3D Render** | 3D graphics | CGI quality rendering |

## 🔧 Scripts Reference

### Backend
```bash
./scripts/start_server.sh    # Start backend server
./scripts/stop_server.sh     # Stop all servers
```

### Frontend
```bash
./scripts/start_frontend.sh  # Start React dev server
```

### Development
```bash
./scripts/dev.sh            # Start backend + show instructions
```

### Logs
All server logs are stored in `logs/server.log`

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI** - Modern async web framework
- **APScheduler** - Background job scheduling
- **OpenAI** - GPT-4 & DALL-E integration
- **Tweepy** - Twitter API client
- **PRAW** - Reddit API client
- **Cloudinary** - Image hosting for Instagram

### Frontend (React/Vite)
- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **Context API** - State management
- **localStorage** - Data persistence

## 📚 Documentation

Comprehensive guides in the `docs/` folder:

- **[AI Generator Guide](docs/AI_GENERATOR_GUIDE.md)** - Complete AI features documentation
- **[Backend Architecture](docs/BACKEND_ARCHITECTURE.md)** - System design and structure
- **[Scheduler Guide](docs/SCHEDULER_GUIDE.md)** - Scheduling system details
- **[Tone & Style Guide](docs/TONE_AND_STYLE_GUIDE.md)** - Content personalization
- **[Publish to All Feature](docs/PUBLISH_TO_ALL_FEATURE.md)** - Multi-platform publishing

## 🔒 Security

- ✅ Environment variables for all secrets
- ✅ File upload validation (type, size)
- ✅ Input sanitization
- ✅ CORS configuration
- ✅ API rate limiting considerations

## 🛠️ Development

### Adding a New Platform
1. Create service in `app/services/`
2. Add client in `app/clients/` (if needed)
3. Update `app/routes/posts.py`
4. Add UI components in frontend
5. Update platform status checks

### Customizing AI Prompts
Edit `app/services/ai_service.py`:
- `tone_instructions` - Content tone definitions
- `style_prompts` - Image style definitions
- `enhance_user_prompt` - Prompt enhancement logic

## 📊 Platform Requirements

### Facebook
- Page Access Token
- Page ID
- `pages_read_engagement` permission

### Instagram
- Business/Creator Account
- Access Token via Facebook
- Cloudinary account for image hosting

### Twitter
- API Key & Secret
- Access Token & Secret
- Elevated access for media upload

### Reddit
- Client ID & Secret
- Username & Password
- User Agent

## 🐛 Troubleshooting

### Server won't start
```bash
# Check logs
cat logs/server.log

# Kill any stuck processes
./scripts/stop_server.sh

# Restart
./scripts/start_server.sh
```

### Frontend won't connect to backend
- Ensure backend is running: http://localhost:8000/api/health
- Check browser console for CORS errors
- Verify API URLs in frontend code

### Platform posting fails
- Check platform credentials in `.env`
- Verify tokens with: `curl http://localhost:8000/api/verify-token`
- Check individual platform API status

### Scheduled posts not executing
- Check `scheduled_posts.json` exists
- Verify scheduler is running (check logs)
- Ensure server stays running

## 📝 License

This project is for educational and personal use.

## 🤝 Contributing

This is a personal project. Feel free to fork and customize for your needs!

---

**Version**: 2.0  
**Last Updated**: October 9, 2025  
**Status**: Production Ready

For detailed documentation, see the `docs/` folder.
