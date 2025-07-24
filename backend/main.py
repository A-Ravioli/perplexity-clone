from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from datetime import datetime
from websearch_agent import WebSearchAgent
import uuid
import re

app = FastAPI(title="Perplexity Clone API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # NextJS default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the web search agent
web_agent = None

def get_web_agent():
    """Initialize and return the web search agent."""
    global web_agent
    if web_agent is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY not configured. Please set this environment variable."
            )
        
        amplitude_api_key = os.getenv("AMPLITUDE_API_KEY", "demo_key")
        amplitude_server_url = os.getenv("AMPLITUDE_SERVER_URL")  # Optional: for local development
        
        web_agent = WebSearchAgent(
            openai_api_key=openai_api_key,
            amplitude_api_key=amplitude_api_key,
            model_name="gpt-4o-mini",
            temperature=0.1,
            amplitude_server_url=amplitude_server_url
        )
        web_agent.start_conversation()
    
    return web_agent

# Pydantic models
class SearchQuery(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    domain: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    ai_summary: str
    sources: List[str]
    conversation_id: str
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="healthy", message="Perplexity Clone API is running")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", message="API is operational")

def extract_sources_from_response(response_text: str) -> List[str]:
    """Extract domain sources from the agent response."""
    # Simple regex to find URLs in the response
    url_pattern = r'https?://([^\s/]+)'
    matches = re.findall(url_pattern, response_text)
    
    # Extract unique domains
    domains = list(set([match.split('/')[0] for match in matches]))
    
    # If no URLs found, return some common sources (fallback)
    if not domains:
        domains = ["web search results", "duckduckgo.com"]
    
    return domains[:5]  # Limit to 5 sources

def create_mock_search_results(query: str, response_text: str) -> List[SearchResult]:
    """Create mock search results based on the agent response."""
    # For now, create some generic search results
    # In a more sophisticated implementation, you could parse the actual search results
    # from the agent's internal search calls
    
    sources = extract_sources_from_response(response_text)
    results = []
    
    # Create mock results based on sources found
    for i, source in enumerate(sources[:3], 1):
        results.append(SearchResult(
            title=f"Search Result {i} for '{query}'",
            url=f"https://{source}",
            snippet=f"Information from {source} related to your query about {query}.",
            domain=source
        ))
    
    # If no sources, create a generic result
    if not results:
        results.append(SearchResult(
            title=f"Web Search Results for '{query}'",
            url="https://web-search-results.com",
            snippet="Comprehensive information gathered from web search.",
            domain="web-search-results.com"
        ))
    
    return results

@app.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery):
    """
    Main search endpoint that combines web search with AI-powered summarization
    """
    try:
        # Get the web search agent
        agent = get_web_agent()
        
        # Perform the actual web search and get AI response
        ai_response = agent.ask_question(query.query)
        
        # Extract sources from the response
        sources = extract_sources_from_response(ai_response)
        
        # Create mock search results (in a full implementation, you'd extract actual search results)
        search_results = create_mock_search_results(query.query, ai_response)
        
        return SearchResponse(
            query=query.query,
            results=search_results,
            ai_summary=ai_response,
            sources=sources,
            conversation_id=query.conversation_id or str(uuid.uuid4()),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        # Fallback to basic response if agent fails
        return SearchResponse(
            query=query.query,
            results=[SearchResult(
                title="Search Error",
                url="https://error.com",
                snippet=f"Unable to perform web search: {str(e)}",
                domain="error.com"
            )],
            ai_summary=f"I apologize, but I encountered an error while searching for information about '{query.query}'. Please make sure the OpenAI API key is configured correctly. Error: {str(e)}",
            sources=["error"],
            conversation_id=query.conversation_id or str(uuid.uuid4()),
            timestamp=datetime.now()
        )

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Retrieve conversation history
    """
    # Mock implementation
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "created_at": datetime.now()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 