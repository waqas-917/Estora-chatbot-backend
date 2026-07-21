from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional

# Initialize FastAPI
app = FastAPI()

# CORS Configuration - Allow your frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourusername.github.io",  # Your GitHub Pages URL
        "http://localhost:5500",
        "http://localhost:3000",
        "*"  # For testing only - remove in production!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"

# Response model
class ChatResponse(BaseModel):
    response: str
    status: str

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "🤖 Chatbot API is running!",
        "status": "active",
        "endpoints": {
            "/": "This info",
            "/health": "Health check",
            "/chat": "Send messages (POST)"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

# Chat endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # For now, just echo the message back
        # Later we'll add the real AI logic
        response = f"You said: '{request.message}'"
        
        return ChatResponse(
            response=response,
            status="success"
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"Error: {str(e)}",
            status="error"
        )

# For local testing
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)