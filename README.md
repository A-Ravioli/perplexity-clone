# Perplexity Clone

A modern Perplexity-like search application built with NextJS and FastAPI.

## Architecture

- **Frontend**: NextJS 14 with TypeScript, Tailwind CSS, and modern React hooks
- **Backend**: FastAPI with Python, providing search and AI summarization APIs
- **UI**: Modern, responsive design similar to Perplexity AI

## Features

- 🔍 Real-time search interface
- 💬 Conversational UI with chat history
- 📱 Responsive design for all devices
- 🎨 Modern dark/light theme support
- ⚡ Fast API responses with mock data
- 🔗 Source citations and result display

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the FastAPI server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
Interactive docs at http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health status
- `POST /search` - Main search endpoint
- `GET /conversations/{conversation_id}` - Get conversation history

## Development

Make sure both servers are running:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

The frontend will communicate with the backend API to provide search functionality.

## Next Steps

To enhance this application, you can:

1. **Add real search providers** (Google, Bing, DuckDuckGo APIs)
2. **Integrate AI/LLM services** (OpenAI, Anthropic, local models)
3. **Add authentication** and user management
4. **Implement database** for conversation history
5. **Add caching** with Redis for better performance
6. **Deploy to production** (Vercel + Railway/Render)

## License

MIT License
