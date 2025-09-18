from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.models import ChatMessage, ChatResponse
from app.chatbot_service import ChatBotService
import logging
import json

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

chatbot_service = ChatBotService()


@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "ChatBet AI Assistant API",
            "version": settings.api_version,
            "status": "running"
        },
        media_type="application/json; charset=utf-8"
    )


@app.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": settings.api_version
        },
        media_type="application/json; charset=utf-8"
    )


@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    try:
        message.session_id = "1"
        logger.info(f"Processing message from session {message.session_id}: {message.message}")
        response = await chatbot_service.process_message(message)
        logger.info(f"Generated response with intent: {response.intent}")
        return JSONResponse(
            content=response.dict(),
            media_type="application/json; charset=utf-8"
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error processing your message. Please try again."
        )


@app.get("/chat/context/{session_id}")
async def get_conversation_context(session_id: str):
    try:
        context = await chatbot_service._get_user_context(session_id)
        return {
            "session_id": context.session_id,
            "conversation_history": context.conversation_history[-5:],
            "mentioned_teams": context.mentioned_teams,
            "last_intent": context.last_intent,
            "user_balance": context.user_balance
        }
    except Exception as e:
        logger.error(f"Error getting conversation context: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving conversation context"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )