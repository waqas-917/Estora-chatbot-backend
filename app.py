# app.py
import os
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chatbot import ask_question
from db import save_chat_message, fetch_chat_history, init_database

app = FastAPI(title="Estora Chatbot API")

# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://localhost:3000", "http://127.0.0.1:5500", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"


class ChatResponse(BaseModel):
    response: str
    status: str


@app.get("/")
async def root():
    return {
        "message": "🤖 Estora chatbot API is running!",
        "status": "active",
        "endpoints": {
            "/": "This info",
            "/health": "Health check",
            "/chat": "Send messages (POST)",
            "/chat/history": "Retrieve recent history (GET)",
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database_ready": bool(os.getenv("MONGODB_URI")),
    }


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = ask_question(request.message)
        # Save to PostgreSQL
        save_chat_message(request.user_id or "anonymous", request.message, response)
        return ChatResponse(response=response, status="success")
    except Exception as exc:
        return ChatResponse(response=f"Error: {exc}", status="error")


@app.get("/chat/history")
async def chat_history(user_id: str = Query(default="anonymous", description="Unique user identifier")):
    return fetch_chat_history(user_id, limit=5)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)