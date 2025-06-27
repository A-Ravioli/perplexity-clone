#!/usr/bin/env python3
"""
Agent Analytics Mock Data Generator

This script generates mock agent analytics events for testing Amplitude charts and KPIs.
It emits all 5 agent event types defined in the agent analytics schema:

1. agent run started
2. agent run completed  
3. agent tool called
4. agent message (when available)
5. user message (when available)

Usage:
    python mock_events_script.py [--sessions=10] [--days=7] [--agents=3]

This script helps you test your Amplitude dashboards with realistic agent interaction data.
"""

import argparse
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

# Import the Ampli SDK (already configured in the project)
from ampli import ampli, LoadOptions, Environment
from ampli.ampli import (
    AgentRunStarted,
    AgentRunCompleted,
    AgentToolCalled,
    AgentMessage,
    LoadClientOptions,
    UserMessage,
)

# Configuration - Ampli is already configured with the API key
# API Key: dd9b69458da7276206d45eafd58f4174 (configured in ampli setup)


# Mock data constants
AGENT_TYPES = ["coding-assistant", "data-analyst", "content-writer", "customer-support", "research-helper"]

MODEL_NAMES = [
    "gpt-4o",
    "gpt-4o-mini",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]

TOOL_NAMES = [
    "codebase_search",
    "read_file",
    "edit_file",
    "run_terminal_cmd",
    "web_search",
    "create_diagram",
    "grep_search",
    "list_dir",
]

USER_MESSAGES = [
    "Help me debug this function",
    "Can you explain this code?",
    "Write a unit test for this class",
    "Refactor this to be more efficient",
    "How do I implement this feature?",
    "What's the best practice here?",
    "Can you review my code?",
    "Help me fix this bug",
]

AGENT_MESSAGES = [
    "I'll help you debug that function. Let me examine the code first.",
    "Looking at this code, I can see a few potential issues.",
    "Here's a unit test that covers the main functionality.",
    "I can refactor this to improve performance and readability.",
    "To implement this feature, I recommend the following approach.",
    "The best practice here would be to use defensive programming.",
    "I've reviewed your code and have some suggestions.",
    "I found the bug - it's in the error handling logic.",
]

ORG_IDS = ["org_123", "org_456", "org_789"]
APP_IDS = ["langley-prod", "langley-dev", "langley-staging"]


class MockEventGenerator:
    """Generates realistic mock agent analytics events."""

    def __init__(self):
        self.user_counter = 1
        self.session_counter = 1

    def generate_user_id(self) -> str:
        """Generate a mock user ID."""
        user_id = f"user_{self.user_counter:04d}"
        self.user_counter += 1
        return user_id

    def generate_session_id(self) -> str:
        """Generate a mock session ID."""
        session_id = f"session_{self.session_counter:06d}"
        self.session_counter += 1
        return session_id

    def generate_run_id(self) -> str:
        """Generate a unique run ID."""
        return f"run_{uuid.uuid4().hex[:8]}"

    def generate_message_id(self) -> str:
        """Generate a unique message ID."""
        return f"msg_{uuid.uuid4().hex[:8]}"

    def generate_device_id(self) -> str:
        """Generate a mock device ID."""
        return f"device_{uuid.uuid4().hex[:12]}"

    def generate_prompt_hash(self) -> str:
        """Generate a mock prompt hash."""
        return f"prompt_{uuid.uuid4().hex[:16]}"

    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate mock cost based on model and tokens."""
        # Simplified cost calculation based on common pricing
        cost_per_token = {
            "gpt-4o": 0.00001,
            "gpt-4o-mini": 0.000001,
            "claude-3-5-sonnet-20241022": 0.000005,
            "claude-3-5-haiku-20241022": 0.000002,
            "gemini-1.5-pro": 0.000003,
            "gemini-1.5-flash": 0.000001,
        }

        rate = cost_per_token.get(model_name, 0.000003)
        return round((input_tokens + output_tokens) * rate, 6)

    def emit_agent_run_started(self, run_data: Dict[str, Any]) -> None:
        """Emit agent run started event using Ampli SDK."""
        event = AgentRunStarted(
            agent_id=run_data["agent_id"],
            agent_run_id=run_data["run_id"],
            app_id=run_data["app_id"],
            device_id=run_data["device_id"],
            model_name=run_data["model_name"],
            org_id=run_data["org_id"],
            prompt_hash=run_data["prompt_hash"],
            session_id=run_data["session_id"],
            temperature=str(run_data["temperature"]),
            timestamp=run_data["start_time"].isoformat(),
        )

        ampli.agent_run_started(
            run_data["user_id"],
            event,
            {
                "groups": {
                    "org id": run_data["org_id"],
                    "app id": run_data["app_id"],
                }
            },
        )
        print(f"✅ Emitted: agent run started (run_id: {run_data['run_id']})")

    def emit_agent_run_completed(self, run_data: Dict[str, Any]) -> None:
        """Emit agent run completed event using Ampli SDK."""
        event = AgentRunCompleted(
            agent_run_id=run_data["run_id"],
            app_id=run_data["app_id"],
            completion_quality_score=str(run_data["quality_score"]),
            device_id=run_data["device_id"],
            org_id=run_data["org_id"],
            p_95_ttfb_ms=str(run_data["p95_ttfb_ms"]),
            session_id=run_data["session_id"],
            timestamp=run_data["end_time"].isoformat(),
            total_cost_usd=str(run_data["total_cost"]),
            total_tokens=str(run_data["total_tokens"]),
        )

        ampli.agent_run_completed(
            run_data["user_id"],
            event,
            {
                "groups": {
                    "org id": run_data["org_id"],
                    "app id": run_data["app_id"],
                }
            },
        )
        print(f"✅ Emitted: agent run completed (run_id: {run_data['run_id']}, cost: ${run_data['total_cost']:.4f})")

    def emit_agent_tool_called(self, tool_data: Dict[str, Any]) -> None:
        """Emit agent tool called event using Ampli SDK."""
        event = AgentToolCalled(
            agent_run_id=tool_data["run_id"],
            app_id=tool_data["app_id"],
            device_id=tool_data["device_id"],
            latency_ms=str(tool_data["latency_ms"]),
            org_id=tool_data["org_id"],
            session_id=tool_data["session_id"],
            timestamp=tool_data["timestamp"].isoformat(),
            tokens=str(tool_data["tokens"]),
            tool_name=tool_data["tool_name"],
            tool_success=str(tool_data["success"]).lower(),
        )

        ampli.agent_tool_called(
            tool_data["user_id"],
            event,
            {
                "groups": {
                    "org id": tool_data["org_id"],
                    "app id": tool_data["app_id"],
                }
            },
        )
        print(f"✅ Emitted: agent tool called (tool: {tool_data['tool_name']}, success: {tool_data['success']})")

    def emit_agent_message(self, message_data: Dict[str, Any]) -> None:
        """Emit agent message event using Ampli SDK."""
        event = AgentMessage(
            agent_run_id=message_data["run_id"],
            app_id=message_data["app_id"],
            cost_usd=str(message_data["cost"]),
            device_id=message_data["device_id"],
            input_tokens=str(message_data["input_tokens"]),
            latency_ms=str(message_data["latency_ms"]),
            message_content=message_data["content"],
            message_id=message_data["message_id"],
            model_name=message_data["model_name"],
            org_id=message_data["org_id"],
            output_tokens=str(message_data["output_tokens"]),
            session_id=message_data["session_id"],
            temperature=str(message_data["temperature"]),
            timestamp=message_data["timestamp"].isoformat(),
        )

        ampli.agent_message(
            message_data["user_id"],
            event,
            {
                "groups": {
                    "org id": message_data["org_id"],
                    "app id": message_data["app_id"],
                }
            },
        )
        print(
            f"✅ Emitted: agent message (tokens: {message_data['input_tokens']}+{message_data['output_tokens']}, cost: ${message_data['cost']:.4f})"
        )

    def emit_user_message(self, message_data: Dict[str, Any]) -> None:
        """Emit user message event using Ampli SDK."""
        event = UserMessage(
            agent_run_id=message_data["run_id"],
            app_id=message_data["app_id"],
            device_id=message_data["device_id"],
            message_content=message_data["content"],
            message_id=message_data["message_id"],
            org_id=message_data["org_id"],
            session_id=message_data["session_id"],
            timestamp=message_data["timestamp"].isoformat(),
        )

        ampli.user_message(
            message_data["user_id"],
            event,
            {
                "groups": {
                    "org id": message_data["org_id"],
                    "app id": message_data["app_id"],
                }
            },
        )
        print(f"✅ Emitted: user message (content: {message_data['content'][:50]}...)")

    def generate_mock_session(self, base_time: datetime) -> None:
        """Generate a complete mock agent session with all events."""

        # Generate session identifiers
        user_id = self.generate_user_id()
        session_id = self.generate_session_id()
        run_id = self.generate_run_id()
        device_id = self.generate_device_id()
        agent_id = random.choice(AGENT_TYPES)
        model_name = random.choice(MODEL_NAMES)
        org_id = random.choice(ORG_IDS)
        app_id = random.choice(APP_IDS)

        # Session timing
        start_time = base_time + timedelta(
            hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59)
        )

        # Session parameters
        temperature = round(random.uniform(0.0, 1.0), 1)
        prompt_hash = self.generate_prompt_hash()

        # Initialize session tracking
        total_cost = 0.0
        total_tokens = 0
        current_time = start_time

        # Common session data
        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "run_id": run_id,
            "device_id": device_id,
            "agent_id": agent_id,
            "model_name": model_name,
            "org_id": org_id,
            "app_id": app_id,
            "temperature": temperature,
            "prompt_hash": prompt_hash,
            "start_time": start_time,
        }

        print(f"\n🚀 Starting mock session: {run_id} (agent: {agent_id}, model: {model_name})")

        # 1. Emit agent run started
        self.emit_agent_run_started(session_data)
        current_time += timedelta(seconds=random.randint(1, 5))

        # 2. Generate conversation messages
        num_exchanges = random.randint(2, 8)

        for exchange in range(num_exchanges):
            # User message
            user_message_id = self.generate_message_id()
            user_content = random.choice(USER_MESSAGES)

            user_msg_data = {
                "user_id": user_id,
                "run_id": run_id,
                "device_id": device_id,
                "app_id": app_id,
                "org_id": org_id,
                "session_id": session_id,
                "message_id": user_message_id,
                "content": user_content,
                "timestamp": current_time,
            }

            self.emit_user_message(user_msg_data)
            current_time += timedelta(seconds=random.randint(1, 3))

            # Agent processing time
            processing_time = random.randint(500, 3000)

            # Generate tool calls (0-3 per agent response)
            num_tools = random.randint(0, 3)
            for tool_idx in range(num_tools):
                tool_name = random.choice(TOOL_NAMES)
                tool_success = random.choice([True, True, True, False])  # 75% success rate
                tool_latency = random.randint(100, 2000)
                tool_tokens = random.randint(50, 500)

                tool_data = {
                    "user_id": user_id,
                    "run_id": run_id,
                    "device_id": device_id,
                    "app_id": app_id,
                    "org_id": org_id,
                    "session_id": session_id,
                    "tool_name": tool_name,
                    "success": tool_success,
                    "latency_ms": tool_latency,
                    "tokens": tool_tokens,
                    "timestamp": current_time,
                }

                self.emit_agent_tool_called(tool_data)
                current_time += timedelta(milliseconds=tool_latency)
                total_tokens += tool_tokens

            # Agent message
            agent_message_id = self.generate_message_id()
            agent_content = random.choice(AGENT_MESSAGES)
            input_tokens = random.randint(200, 1500)
            output_tokens = random.randint(150, 800)
            message_cost = self.calculate_cost(model_name, input_tokens, output_tokens)

            agent_msg_data = {
                "user_id": user_id,
                "run_id": run_id,
                "device_id": device_id,
                "app_id": app_id,
                "org_id": org_id,
                "session_id": session_id,
                "message_id": agent_message_id,
                "content": agent_content,
                "model_name": model_name,
                "temperature": temperature,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": message_cost,
                "latency_ms": processing_time,
                "timestamp": current_time,
            }

            self.emit_agent_message(agent_msg_data)
            current_time += timedelta(milliseconds=processing_time)
            total_cost += message_cost
            total_tokens += input_tokens + output_tokens

            # Brief pause between exchanges
            current_time += timedelta(seconds=random.randint(2, 10))

        # 3. Emit agent run completed
        end_time = current_time
        session_duration = (end_time - start_time).total_seconds()

        completion_data = {
            **session_data,
            "end_time": end_time,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "quality_score": round(random.uniform(0.7, 1.0), 2),
            "p95_ttfb_ms": random.randint(200, 1500),
        }

        self.emit_agent_run_completed(completion_data)

        print(f"✅ Session completed: {session_duration:.1f}s, {total_tokens} tokens, ${total_cost:.4f}")

        # Small delay between sessions
        time.sleep(0.1)


def main():
    """Main function to generate mock agent analytics data."""
    parser = argparse.ArgumentParser(description="Generate mock agent analytics events for Amplitude")
    parser.add_argument("--sessions", type=int, default=20, help="Number of mock sessions to generate")
    parser.add_argument("--days", type=int, default=7, help="Number of days to spread events across")
    parser.add_argument("--agents", type=int, default=3, help="Number of different agents to simulate")

    args = parser.parse_args()

    print("🎯 Agent Analytics Mock Data Generator")
    print("=" * 50)
    print(f"📊 Generating {args.sessions} sessions across {args.days} days")
    print(f"🤖 Using {args.agents} different agent types")
    print(f"🔑 Using Ampli SDK with API Key: dd9b69458da7276206d45eafd58f4174")
    print()

    # Initialize Ampli
    print("🔧 Initializing Ampli SDK...")
    try:
        AMPLITUDE_API_KEY = "dd9b69458da7276206d45eafd58f4174"
        ampli.load(
            LoadOptions(
                client=LoadClientOptions(
                    api_key=AMPLITUDE_API_KEY,
                ),
                disabled=False,
                environment=Environment.DEVELOPMENT,
            )
        )
        print("✅ Ampli SDK initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Ampli SDK: {e}")
        print("💡 Make sure Ampli is properly configured in your project")
        return

    generator = MockEventGenerator()

    # Generate sessions across the specified time range
    end_time = datetime.now()
    start_time = end_time - timedelta(days=args.days)

    for session_num in range(args.sessions):
        # Distribute sessions across the time range
        progress = session_num / args.sessions
        session_time = start_time + timedelta(seconds=progress * (end_time - start_time).total_seconds())

        print(f"\n📅 Session {session_num + 1}/{args.sessions} - {session_time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            generator.generate_mock_session(session_time)
        except Exception as e:
            print(f"❌ Error generating session {session_num + 1}: {e}")
            continue

    # Flush all events to Amplitude
    print("\n🚀 Flushing events to Amplitude...")
    ampli.flush()

    print("\n" + "=" * 50)
    print("✅ Mock data generation completed!")
    print(f"📊 Generated {args.sessions} agent sessions")
    print("🎯 Check your Amplitude dashboard for the new events:")
    print("   ✅ agent run started")
    print("   ✅ agent run completed")
    print("   ✅ agent tool called")
    print("   ✅ agent message")
    print("   ✅ user message")
    print("\n💡 You can now create comprehensive charts and KPIs using all 5 events!")
    print("\n📈 Available Analytics:")
    print("   • Total agent costs and token usage")
    print("   • Tool success rates and usage patterns")
    print("   • Daily active users per agent type")
    print("   • Message-level performance metrics")
    print("   • Conversation flow analysis")


if __name__ == "__main__":
    main()
