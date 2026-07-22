# Chatbot Backend API

FastAPI backend for my RAG chatbot.

## Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /chat` - Send messages

## Local Development

```bash
pip install -r requirements.txt
uvicorn app:app --reload