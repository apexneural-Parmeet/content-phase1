# Facebook Photo Poster 📱

A modern web application that allows you to post photos with captions to your Facebook page using the Facebook Graph API.

**Backend:** Python with FastAPI  
**Frontend:** React with Vite

## Features

✅ Modern React user interface  
✅ Upload photos (JPEG, PNG, GIF)  
✅ Add custom captions  
✅ Real-time image preview  
✅ Character counter for captions  
✅ Automatic Facebook posting  
✅ Token validation  
✅ Error handling  
✅ Async/await for better performance  
✅ Component-based architecture

## Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Uvicorn** - High-performance ASGI server
- **httpx** - Async HTTP client for Facebook API
- **python-multipart** - File upload handling
- **aiofiles** - Async file operations
- **python-dotenv** - Environment variable management

### Frontend
- **React 18** - Modern UI library
- **Vite** - Lightning-fast build tool
- **CSS3** - Modern styling with gradients and animations

### External APIs
- **Facebook Graph API v18.0** - For posting photos

## Prerequisites

- Python 3.8 or higher
- Node.js 16+ and npm
- Facebook Page Access Token

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "/Users/parmeetsingh/Documents/dbaas/facebook try"
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install React dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment variables:**
   The `.env` file contains your Facebook token:
   ```
   FACEBOOK_PAGE_ACCESS_TOKEN=your_token_here
   PORT=8000
   ```

## Running the Application

You need to run both the backend and frontend servers:

### 1. Start the Backend (FastAPI)

In the project root directory:
```bash
python3 server.py
```

The backend will run on `http://localhost:8000`

### 2. Start the Frontend (React)

In a new terminal, navigate to the frontend directory:
```bash
cd frontend
npm run dev
```

The frontend will run on `http://localhost:3000`

### 3. Access the Application

Open your browser and go to: `http://localhost:3000`

## Project Structure

```
facebook try/
├── server.py          # FastAPI backend
├── requirements.txt   # Python dependencies
├── .env              # Environment variables (API token)
├── .gitignore        # Git ignore rules
├── README.md         # This file
└── frontend/         # React application
    ├── package.json  # Node.js dependencies
    ├── vite.config.js # Vite configuration with proxy
    ├── index.html    # HTML entry point
    └── src/
        ├── App.jsx   # Main React component
        ├── App.css   # Component styles
        ├── main.jsx  # React entry point
        └── index.css # Global styles
```

## API Endpoints

### `GET /api/health`
Health check endpoint to verify server is running.

**Response:**
```json
{"status": "ok", "message": "Server is running"}
```

### `GET /api/verify-token`
Verifies the Facebook access token and returns page information.

**Response:**
```json
{
  "valid": true,
  "pageInfo": {
    "name": "Your Page Name",
    "id": "page_id"
  }
}
```

### `POST /api/post`
Posts a photo with caption to Facebook.

**Request:**
- Content-Type: `multipart/form-data`
- `photo`: Image file (required)
- `caption`: Text caption (optional)

**Response:**
```json
{
  "success": true,
  "message": "Photo posted successfully to Facebook!",
  "postId": "post_id",
  "postLink": "https://www.facebook.com/post_id"
}
```

## Development

### Backend Development

The FastAPI backend includes automatic API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Frontend Development

Vite provides:
- Hot Module Replacement (HMR) for instant updates
- Fast build times
- Automatic proxy to backend API

### Running Tests

Backend:
```bash
# Add pytest and run tests
pytest
```

Frontend:
```bash
cd frontend
npm run test
```

## Building for Production

### Backend
The Python server is production-ready. For deployment:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Frontend
Build the React app:
```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/`

## Facebook API Integration

This application uses the Facebook Graph API v18.0 to post photos to your page. The API token is configured in the `.env` file.

### Required Permissions

Your Facebook token should have the following permissions:
- `pages_manage_posts`
- `pages_read_engagement`

## Performance Features

✅ **Async/Await** - Non-blocking I/O operations  
✅ **FastAPI** - High-performance async framework  
✅ **React** - Fast, efficient UI rendering  
✅ **Vite** - Lightning-fast development builds  
✅ **Component-based** - Reusable, maintainable code  
✅ **Automatic cleanup** - Temporary files deleted after upload  
✅ **Input validation** - File type and size checks  
✅ **Error handling** - Comprehensive error messages

## Security Notes

⚠️ **Important Security Considerations:**

1. The `.env` file contains your API token and should **never** be committed to Git
2. The `.gitignore` file is configured to exclude sensitive files
3. Always keep your access token secure and private
4. File uploads are validated for type and size
5. CORS is configured for development (adjust for production)
6. Consider using Facebook's long-lived tokens for production use
7. Regularly rotate your access tokens

## Troubleshooting

### Backend Issues
- Ensure port 8000 is not in use
- Check that all Python dependencies are installed
- Verify Python version (3.8+ required)
- Check `.env` file for proper token configuration

### Frontend Issues
- Ensure port 3000 is not in use
- Check that Node.js and npm are installed
- Run `npm install` in the frontend directory
- Clear browser cache if seeing old version

### Token Issues
- Verify your token in the `.env` file
- Check that your token has the required permissions
- Ensure the token hasn't expired

### Upload Issues
- Make sure the image is less than 10MB
- Only JPEG, PNG, and GIF formats are supported
- Check your internet connection
- Verify both backend and frontend are running

## Advantages of React + FastAPI Stack

| Feature | Benefit |
|---------|---------|
| **React** | Modern, component-based UI with great developer experience |
| **Vite** | Lightning-fast builds and HMR |
| **FastAPI** | High-performance async Python backend |
| **Type Safety** | Python type hints + PropTypes/TypeScript |
| **Auto Documentation** | Built-in Swagger UI at `/docs` |
| **Modern Stack** | Latest technologies and best practices |

## Commands Cheat Sheet

```bash
# Start backend
python3 server.py

# Start frontend (in frontend/ directory)
npm run dev

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install

# Build frontend for production
cd frontend && npm run build

# View API documentation
# Open http://localhost:8000/docs in browser
```

## License

ISC

## Support

For issues related to:
- **Facebook API**: [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api/)
- **FastAPI**: [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **React**: [React Documentation](https://react.dev/)
- **Vite**: [Vite Documentation](https://vitejs.dev/)
# Content_upload
