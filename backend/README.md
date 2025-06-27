# Perplexity Clone - FastAPI Backend

This is the backend API for the Perplexity clone application built with FastAPI.

## Features

- Search endpoint with AI-powered summarization
- CORS configuration for frontend integration
- Pydantic models for type safety
- Mock data for development and testing

## Setup

1. Install dependencies using UV:
```bash
uv sync
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. Run the development server:
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health status
- `POST /search` - Main search endpoint
- `GET /conversations/{conversation_id}` - Get conversation history

## Development

The API will be available at http://localhost:8000

Interactive API documentation (Swagger UI) will be available at http://localhost:8000/docs 