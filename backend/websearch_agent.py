#!/usr/bin/env python3
"""
Web-Searching Agent with Amplitude Analytics

This script demonstrates a web-searching agent that:
1. Uses Langchain with OpenAI for natural language processing
2. Searches the web for information to answer questions
3. Tracks all interactions using Amplitude agent analytics
4. Provides detailed cost and performance metrics

Requirements:
pip install langchain langchain-community langchain-openai beautifulsoup4 requests google-search-results python-dotenv

Usage:
1. Set your OpenAI API key in environment or .env file
2. Set your Amplitude API key in the script below
3. Run the script and ask questions!
"""

import os
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# External dependencies
import openai
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from langchain_openai import ChatOpenAI
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from functools import wraps
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# Mock Amplitude analytics for simplified setup
class MockAgentAnalyticsTracker:
    """Mock analytics tracker for demonstration."""
    def __init__(self, run_context):
        self.run_context = run_context
    
    def emit_agent_run_started(self, **kwargs):
        print(f"📊 Analytics: Run started with {kwargs}")
    
    def emit_user_message(self, **kwargs):
        print(f"📊 Analytics: User message tracked")
    
    def emit_agent_message(self, **kwargs):
        print(f"📊 Analytics: Agent message tracked")
    
    def emit_agent_tool_called(self, **kwargs):
        print(f"📊 Analytics: Tool called - {kwargs.get('tool_name', 'unknown')}")
    
    def emit_agent_run_completed(self, **kwargs):
        print(f"📊 Analytics: Run completed with quality score {kwargs.get('completion_quality_score', 0)}")
    
    def estimate_cost_from_text(self, model_name, input_text, output_text):
        # Rough cost estimation for GPT-4o-mini
        input_tokens = len(input_text.split()) * 1.3
        output_tokens = len(output_text.split()) * 1.3
        # GPT-4o-mini pricing: $0.15 per 1M input tokens, $0.60 per 1M output tokens
        cost = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
        return cost

def configure_agent_analytics(**kwargs):
    """Mock configure function."""
    print("📊 Analytics configured (mock)")

# Use mock analytics
AgentAnalyticsTracker = MockAgentAnalyticsTracker

# Mock run context for demonstration - in production, use actual LangleyRunContext
@dataclass
class MockSession:
    app_id: str = "web_search_agent_app"
    org_id: str = "demo_org_123"
    user_id: str = "demo_user_456"
    session_id: str = "demo_session_789"
    device_id: str = "demo_device_abc"

@dataclass
class MockRunContext:
    session: MockSession
    logger: Any = None

    def __post_init__(self):
        if self.logger is None:
            import logging
            self.logger = logging.getLogger(__name__)


class AgentAnalyticsCallbackHandler(BaseCallbackHandler):
    """Callback handler to track agent analytics during Langchain execution."""
    
    def __init__(self, analytics_tracker: AgentAnalyticsTracker, run_id: str, model_name: str):
        self.analytics_tracker = analytics_tracker
        self.run_id = run_id
        self.model_name = model_name
        self.current_tokens = {"input": 0, "output": 0}
        self.tool_start_time = None
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Called when a tool starts running."""
        self.tool_start_time = time.time()
        tool_name = serialized.get("name", "unknown_tool")
        print(f"🔧 Tool started: {tool_name}")
        
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when a tool finishes running."""
        if self.tool_start_time:
            latency_ms = (time.time() - self.tool_start_time) * 1000
            tool_name = kwargs.get("name", "web_search")
            
            # Estimate tokens used by tool (rough estimate)
            estimated_tokens = len(output.split()) * 1.3  # Rough token estimation
            
            self.analytics_tracker.emit_agent_tool_called(
                run_id=self.run_id,
                tool_name=tool_name,
                tool_success=True,
                latency_ms=latency_ms,
                tokens=int(estimated_tokens)
            )
            print(f"✅ Tool completed: {tool_name} ({latency_ms:.0f}ms)")
            
    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when a tool errors."""
        if self.tool_start_time:
            latency_ms = (time.time() - self.tool_start_time) * 1000
            tool_name = kwargs.get("name", "web_search")
            
            self.analytics_tracker.emit_agent_tool_called(
                run_id=self.run_id,
                tool_name=tool_name,
                tool_success=False,
                latency_ms=latency_ms,
                tokens=0
            )
            print(f"❌ Tool failed: {tool_name} - {error}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM finishes running."""
        # Extract token usage if available
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            if token_usage:
                self.current_tokens['input'] = token_usage.get('prompt_tokens', 0)
                self.current_tokens['output'] = token_usage.get('completion_tokens', 0)


class WebSearchAgent:
    """A web-searching agent with Amplitude analytics tracking."""
    
    def __init__(
        self, 
        openai_api_key: str,
        amplitude_api_key: str = "demo_key",
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.1
    ):
        self.openai_api_key = openai_api_key
        self.amplitude_api_key = amplitude_api_key
        self.model_name = model_name
        self.temperature = temperature
        
        # Configure Amplitude analytics
        configure_agent_analytics(
            custom_api_key=amplitude_api_key,
            custom_app_id="web_search_agent_demo",
            enabled=True,
            debug=True
        )
        
        # Initialize mock run context
        self.run_context = MockRunContext(session=MockSession())
        self.analytics_tracker = AgentAnalyticsTracker(self.run_context)
        
        # Initialize OpenAI
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=openai_api_key
        )
        
        # Set up search tools (DuckDuckGo only)
        self.search_tools = self._setup_search_tools()
        
        # Initialize memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Track conversation state
        self.current_run_id = None
        self.session_start_time = None
        self.conversation_history = []
        self.search_count = 0  # Track searches per query
        
    def _setup_search_tools(self, use_serpapi: bool = False, serpapi_key: Optional[str] = None) -> List[Tool]:
        """Set up web search tools using only DuckDuckGo."""
        tools = []
        
        # Use DuckDuckGo search (free)
        ddg_search = DuckDuckGoSearchAPIWrapper(max_results=3)  # Limit to 3 results per search
        
        def limited_search(query: str) -> str:
            """Wrapper to limit searches per conversation."""
            if self.search_count >= 3:
                return "Search limit reached (3 searches per query). Please use the information already gathered or ask a new question."
            
            self.search_count += 1
            print(f"🔍 Search {self.search_count}/3: {query}")
            try:
                result = ddg_search.run(query)
                return result
            except Exception as e:
                return f"Search failed: {str(e)}"
        
        tools.append(
            Tool(
                name="DuckDuckGo Search",
                description="Search the web using DuckDuckGo. Use this for current information, facts, and general knowledge. You have a maximum of 3 searches per user query - use them wisely!",
                func=limited_search,
            )
        )
        
        return tools
    
    def start_conversation(self) -> str:
        """Start a new conversation session."""
        self.current_run_id = str(uuid.uuid4())
        self.session_start_time = time.time()
        session_id = str(uuid.uuid4())
        
        # Emit run started event
        self.analytics_tracker.emit_agent_run_started(
            agent_id="web_search_agent",
            session_id=session_id,
            run_id=self.current_run_id,
            model_name=self.model_name,
            temperature=self.temperature,
            agent_type="web_search",
            tools_available=len(self.search_tools)
        )
        
        print(f"🤖 Web Search Agent started!")
        print(f"📊 Analytics tracking enabled with run ID: {self.current_run_id}")
        print(f"🔍 Available search tools: {[tool.name for tool in self.search_tools]}")
        print(f"🧠 Using model: {self.model_name} (temp: {self.temperature})")
        print("-" * 60)
        
        return self.current_run_id
    
    def ask_question(self, question: str) -> str:
        """Ask the agent a question and get a response with web search."""
        if not self.current_run_id:
            self.start_conversation()
        
        print(f"👤 User: {question}")
        
        # Track user message
        user_message_id = str(uuid.uuid4())
        self.analytics_tracker.emit_user_message(
            run_id=self.current_run_id,
            message_id=user_message_id,
            message_content=question
        )
        
        # Set up callback handler for this interaction
        callback_handler = AgentAnalyticsCallbackHandler(
            self.analytics_tracker, 
            self.current_run_id, 
            self.model_name
        )
        
        # Initialize agent with tools and memory
        agent = initialize_agent(
            tools=self.search_tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            callbacks=[callback_handler],
            verbose=True,
            handle_parsing_errors=True
        )
        
        # Reset search count for new query
        self.search_count = 0
        
        # Measure response time
        start_time = time.time()
        
        try:
            # Get response from agent
            response = agent.run(question)
            
            # Calculate timing
            response_latency_ms = (time.time() - start_time) * 1000
            
            # Estimate tokens (since we don't have exact counts from the agent)
            estimated_input_tokens = len(question.split()) * 1.3
            estimated_output_tokens = len(response.split()) * 1.3
            
            # Track agent message
            agent_message_id = str(uuid.uuid4())
            self.analytics_tracker.emit_agent_message(
                run_id=self.current_run_id,
                message_id=agent_message_id,
                message_content=response,
                model_name=self.model_name,
                temperature=self.temperature,
                input_tokens=int(estimated_input_tokens),
                output_tokens=int(estimated_output_tokens),
                latency_ms=response_latency_ms
            )
            
            print(f"🤖 Agent: {response}")
            print(f"⏱️  Response time: {response_latency_ms:.0f}ms")
            print(f"💰 Estimated cost: ${self.analytics_tracker.estimate_cost_from_text(self.model_name, question, response):.6f}")
            print("-" * 60)
            
            # Store in conversation history
            self.conversation_history.append({
                'user_message': question,
                'agent_response': response,
                'timestamp': datetime.now(),
                'latency_ms': response_latency_ms
            })
            
            return response
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            print(f"❌ Error: {error_msg}")
            
            # Still track the failed interaction
            agent_message_id = str(uuid.uuid4())
            self.analytics_tracker.emit_agent_message(
                run_id=self.current_run_id,
                message_id=agent_message_id,
                message_content=error_msg,
                model_name=self.model_name,
                temperature=self.temperature,
                input_tokens=int(len(question.split()) * 1.3),
                output_tokens=int(len(error_msg.split()) * 1.3),
                latency_ms=(time.time() - start_time) * 1000,
                error_occurred="true",
                error_message=str(e)
            )
            
            return error_msg
    
    def end_conversation(self) -> None:
        """End the current conversation and emit completion event."""
        if not self.current_run_id or not self.session_start_time:
            return
        
        # Calculate session metrics
        total_session_time = (time.time() - self.session_start_time) * 1000
        
        # Calculate p95 TTFB (time to first byte) - simplified calculation
        response_times = [conv['latency_ms'] for conv in self.conversation_history]
        p95_ttfb = sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
        
        # Simple quality score based on successful responses
        successful_responses = len([conv for conv in self.conversation_history])
        quality_score = min(1.0, successful_responses / max(1, len(self.conversation_history)))
        
        # Emit completion event
        self.analytics_tracker.emit_agent_run_completed(
            run_id=self.current_run_id,
            p95_ttfb_ms=p95_ttfb,
            completion_quality_score=quality_score,
            total_session_time_ms=str(total_session_time),
            total_interactions=str(len(self.conversation_history))
        )
        
        print(f"📊 Session completed!")
        print(f"🔢 Total interactions: {len(self.conversation_history)}")
        print(f"⏱️  Total session time: {total_session_time/1000:.1f}s")
        print(f"🎯 Quality score: {quality_score:.2f}")
        print(f"📈 P95 response time: {p95_ttfb:.0f}ms")
        
        # Reset state
        self.current_run_id = None
        self.session_start_time = None
        self.conversation_history = []


def main():
    """Main function to run the web search agent demo."""
    
    # Load environment variables
    load_dotenv()
    
    # Configuration - EDIT THESE VALUES
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Should be set in your environment
    AMPLITUDE_API_KEY = "YOUR_AMPLITUDE_API_KEY_HERE"  # 👈 REPLACE WITH YOUR AMPLITUDE API KEY
    
    # Optional: SerpAPI for Google Search (more reliable than DuckDuckGo)
    SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")  # Optional - get from https://serpapi.com/
    USE_SERPAPI = bool(SERPAPI_KEY)
    
    # Validate required keys
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file or environment variable")
        return
    
    if AMPLITUDE_API_KEY == "YOUR_AMPLITUDE_API_KEY_HERE":
        print("⚠️  Warning: Using placeholder Amplitude API key")
        print("Please replace AMPLITUDE_API_KEY with your actual key for analytics tracking")
        print("Analytics events will still be generated but may not be sent successfully")
        print()
    
    # Initialize the agent
    print("🚀 Initializing Web Search Agent...")
    agent = WebSearchAgent(
        openai_api_key=OPENAI_API_KEY,
        amplitude_api_key=AMPLITUDE_API_KEY,
        model_name="gpt-4o-mini",  # Fast and cost-effective
        temperature=0.1,  # Low temperature for factual responses
        use_serpapi=USE_SERPAPI,
        serpapi_key=SERPAPI_KEY
    )
    
    # Start conversation
    run_id = agent.start_conversation()
    
    # Demo questions - you can modify or replace these
    demo_questions = [
        "What are the latest developments in artificial intelligence this week?",
        "What is the current weather in San Francisco?",
        "Tell me about the recent SpaceX launches",
        "What are the top trending topics on social media today?",
    ]
    
    try:
        # Interactive mode
        print("💬 Interactive mode - type 'quit' to exit, or press Enter for demo questions")
        
        while True:
            user_input = input("\n👤 Ask a question (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input == "":
                # Run demo questions
                print("🎬 Running demo questions...")
                for i, question in enumerate(demo_questions, 1):
                    print(f"\n--- Demo Question {i}/{len(demo_questions)} ---")
                    agent.ask_question(question)
                    time.sleep(1)  # Brief pause between questions
                break
            else:
                agent.ask_question(user_input)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Session interrupted by user")
    
    finally:
        # End the conversation and emit completion analytics
        agent.end_conversation()
        print("\n👋 Thanks for using the Web Search Agent!")


if __name__ == "__main__":
    main()
    