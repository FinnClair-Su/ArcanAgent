#!/usr/bin/env python3
"""
Simple test for LLM client functionality.
"""

import sys
import asyncio
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.core.llm_client import (
    LLMConfig, 
    LLMProvider, 
    LLMMessage,
    OpenAIClient
)

async def test_basic_functionality():
    """Test basic LLM client functionality."""
    print("🔮 Simple LLM Client Test")
    print("=" * 30)
    
    # Test client creation
    try:
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4-turbo-preview",
            api_key="test-key",
            max_tokens=1000,
            temperature=0.7
        )
        
        client = OpenAIClient(config)
        print(f"✅ OpenAI client created successfully")
        print(f"   Model: {client.config.model}")
        print(f"   Base URL: {client.base_url}")
        
        # Test message formatting
        messages = [
            LLMMessage(role="user", content="Hello!")
        ]
        
        formatted = client._format_messages(messages)
        print(f"✅ Message formatting works: {formatted}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("🎉 Basic functionality test passed!")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(test_basic_functionality()))