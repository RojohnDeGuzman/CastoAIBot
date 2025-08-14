# CASI AI Bot Backend

A Flask-based backend for the CASI AI chatbot that integrates with Microsoft Teams and provides intelligent responses using Groq's LLM API.

## Features

- 🤖 AI-powered chatbot using Groq's LLM API
- 🔐 Microsoft Teams authentication integration
- 📚 Knowledge base management system (simplified for hosting)
- 🌐 Web scraping capabilities for CASTO website
- 🚀 Rate limiting and security features
- 📊 Conversation logging and analytics

## Project Structure

```
CastoAIBot/
├── backend.py              # Main Flask backend (local development)
├── api/                    # Vercel deployment files
│   ├── index.py           # Vercel-compatible Flask app
│   └── requirements.txt   # Vercel dependencies
├── vercel.json            # Vercel configuration
├── requirements.txt       # Local development dependencies
├── chatbot_ui.py         # PyQt5 desktop application
├── config.py             # Configuration settings
└── README.md             # This file
```

## Deployment Options

### Option 1: Vercel Deployment (Recommended for API Hosting)

Perfect for hosting your backend API to connect with your local app:
- ✅ Fast deployment and scaling
- ✅ Free tier available
- ✅ Automatic HTTPS and CDN
- ✅ Easy GitHub integration
- ✅ Perfect for API endpoints
- ⚠️ Simplified knowledge base (no persistent storage)

### Option 2: Traditional Hosting (Full Features)

For full functionality including database and file storage:
- ✅ Full Flask app support
- ✅ SQLite database support
- ✅ File storage capabilities
- ❌ Requires server management

## Vercel Deployment Instructions

### 1. Prepare Your Repository

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/CastoAIBot.git
   git push -u origin main
   ```

2. **Set Environment Variables:**
   - Go to your Vercel project dashboard
   - Add `GROQ_API_KEY` with your actual Groq API key
   - Add any other sensitive configuration

### 2. Deploy to Vercel

1. **Connect GitHub to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Build Settings:**
   - Framework Preset: `Other`
   - Build Command: Leave empty (Vercel will auto-detect)
   - Output Directory: Leave empty

3. **Deploy:**
   - Click "Deploy"
   - Vercel will automatically build and deploy your app

### 3. Connect Your Local App

Once deployed, your backend will be available at:
```
https://your-project-name.vercel.app
```

**Update your local app configuration** to use the Vercel URL instead of localhost:
```python
# In your local app config
BACKEND_URL = "https://your-project-name.vercel.app"
```

## Traditional Hosting Deployment

### 1. VPS/Cloud Server (DigitalOcean, AWS, etc.)

1. **Set up your server:**
   ```bash
   # Install Python and dependencies
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Run the backend:**
   ```bash
   # For production, use gunicorn
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:9000 backend:app
   ```

### 2. Railway/Heroku

1. **Create `Procfile`:**
   ```
   web: gunicorn backend:app
   ```

2. **Update `requirements.txt`:**
   ```
   gunicorn==21.2.0
   ```

3. **Deploy:**
   - Connect your GitHub repo
   - Set environment variables
   - Deploy automatically

## Environment Variables

Create a `.env` file for local development:

```env
GROQ_API_KEY=your_groq_api_key_here
FLASK_ENV=development
FLASK_DEBUG=1
```

## API Endpoints

- `GET /` - Health check with endpoint information
- `POST /chat` - Chat with the AI bot
- `GET /knowledge` - Retrieve knowledge base entries (simplified)
- `POST /knowledge` - Add new knowledge base entry (simplified)

## How It Works

1. **Your local app** connects to the Vercel-hosted backend
2. **Backend processes** chat requests using Groq's LLM API
3. **Web scraping** provides additional context from CASTO website
4. **Authentication** validates Microsoft Teams users
5. **Responses** are sent back to your local app

## Security Considerations

1. **API Keys:** Never commit API keys to GitHub
2. **Authentication:** Implement proper JWT or session management
3. **Rate Limiting:** Already implemented with Flask-Limiter
4. **CORS:** Configure CORS properly for production

## Troubleshooting

### Common Issues

1. **Vercel Build Failures:**
   - Check `api/requirements.txt` for correct dependencies
   - Ensure `vercel.json` is properly configured

2. **Connection Issues:**
   - Verify your Vercel URL is correct
   - Check CORS configuration
   - Ensure environment variables are set

3. **API Errors:**
   - Check Vercel function logs
   - Verify GROQ_API_KEY is set correctly
   - Test endpoints with Postman or similar tool

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary software for CASTO Travel.

## Support

For issues and questions:
- Check the troubleshooting section
- Review Vercel/Flask documentation
- Contact the development team
