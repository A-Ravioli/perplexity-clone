# Perplexity Clone

A modern Perplexity-like search application built with NextJS and FastAPI.

## Architecture

- **Frontend**: NextJS 14 with TypeScript, Tailwind CSS, and modern React hooks
- **Backend**: FastAPI with Python, providing search and AI summarization APIs
- **UI**: Modern, responsive design similar to Perplexity AI

## Features

- 🔍 Real-time web search using DuckDuckGo (free)
- 💬 Conversational UI with chat history
- 📱 Responsive design for all devices
- 🎨 Modern dark/light theme support
- ⚡ AI-powered search responses with GPT-4o-mini
- 🔗 Source citations and result display
- 📊 Search limit: Max 3 searches per query for efficiency

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies using UV:
```bash
uv sync
```

3. Set up environment variables:
```bash
# Your OpenAI API key will be automatically detected from your environment
# The .env file is already configured to use it
```

4. Run the FastAPI server:
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
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

## How It Works

1. **Free Web Search**: Uses DuckDuckGo for web search (no API key required)
2. **AI Processing**: OpenAI GPT-4o-mini analyzes search results and provides comprehensive answers
3. **Search Optimization**: Limited to 3 searches per query to manage costs and improve response times
4. **Source Extraction**: Automatically extracts and displays sources from search results

## Next Steps

To enhance this application, you can:

1. **Add more search providers** (Bing, Google Custom Search)
2. **Add authentication** and user management
3. **Implement database** for conversation history
4. **Add caching** with Redis for better performance
5. **Deploy to production** (Vercel + Railway/Render)
6. **Add search result parsing** for better source extraction

## License

MIT License
