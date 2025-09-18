from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router
import logging

"""
ChatBet AI Assistant - FastAPI Application

Main application module for ChatBet AI, an intelligent conversational chatbot 
for sports betting analysis and recommendations.

Features:
- RESTful API endpoints for chat interactions
- Real-time sports data integration with ChatBet API
- AI-powered responses using Google Gemini
- Conversation context management
- CORS-enabled for web client integration
- Health monitoring and status endpoints
- Session-based user interactions
- JSON response formatting with UTF-8 support
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )