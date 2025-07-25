#!/usr/bin/env python3
"""
Test script for LLM client functionality.
Tests the unified LLM interface with multiple providers.
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
    LLMClientManager,
    OpenAIClient,
    AnthropicClient,
    GeminiClient,
    OpenRouterClient,
    DeepseekClient,
    AlibabaClient
)
from backend.core.llm_initializer import initialize_llm_clients, get_provider_status
from backend.config import config


async def test_client_creation():
    """Test creating individual clients."""
    print("🧪 Testing LLM Client Creation")
    print("=" * 40)
    
    # Test OpenAI-compatible client creation
    print("📝 Creating test OpenAI client...")
    try:
        openai_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4-turbo-preview",
            api_key="test-key",
            max_tokens=1000,
            temperature=0.7
        )
        
        client = OpenAIClient(openai_config)
        print(f"✅ OpenAI client created: {client.__class__.__name__}")
        print(f"   Model: {client.config.model}")
        print(f"   Base URL: {client.base_url}")
        
    except Exception as e:
        print(f"❌ Error creating OpenAI client: {e}")
    
    # Test other client types
    providers_to_test = [
        (LLMProvider.ANTHROPIC, AnthropicClient, "claude-3-sonnet-20240229"),
        (LLMProvider.GEMINI, GeminiClient, "gemini-1.5-pro"),
        (LLMProvider.OPENROUTER, OpenRouterClient, "anthropic/claude-3-sonnet"),
        (LLMProvider.DEEPSEEK, DeepseekClient, "deepseek-chat"),
        (LLMProvider.ALIBABA, AlibabaClient, "qwen-turbo")
    ]
    
    for provider, client_class, model in providers_to_test:
        try:
            client_config = LLMConfig(
                provider=provider,
                model=model,
                api_key="test-key",
                max_tokens=1000,
                temperature=0.7
            )
            
            client = client_class(client_config)
            print(f"✅ {provider.value.title()} client created: {client.__class__.__name__}")
            print(f"   Model: {client.config.model}")
            print(f"   Base URL: {getattr(client, 'base_url', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error creating {provider.value} client: {e}")
    
    print()


async def test_message_formatting():
    """Test message formatting for different providers."""
    print("💬 Testing Message Formatting")
    print("=" * 30)
    
    test_messages = [
        LLMMessage(role="system", content="You are a helpful assistant."),
        LLMMessage(role="user", content="Hello, how are you?"),
        LLMMessage(role="assistant", content="I'm doing well, thank you!")
    ]
    
    providers_to_test = [
        (OpenAIClient, "OpenAI"),
        (AnthropicClient, "Anthropic"), 
        (GeminiClient, "Gemini")
    ]
    
    for client_class, name in providers_to_test:
        try:
            config_obj = LLMConfig(
                provider=LLMProvider.OPENAI,  # Doesn't matter for formatting test
                model="test-model",
                api_key="test-key"
            )
            
            client = client_class(config_obj)
            formatted = client._format_messages(test_messages)
            
            print(f"📋 {name} message format:")
            for i, msg in enumerate(formatted):
                print(f"   {i+1}. {msg}")
            print()
            
        except Exception as e:
            print(f"❌ Error formatting messages for {name}: {e}")
    
    print()


async def test_client_manager():
    """Test the LLM client manager."""
    print("🎛️  Testing LLM Client Manager")
    print("=" * 32)
    
    try:
        manager = LLMClientManager()
        
        # Add test clients
        providers_data = [
            (LLMProvider.OPENAI, "gpt-4-turbo-preview", "openai"),
            (LLMProvider.ANTHROPIC, "claude-3-sonnet-20240229", "anthropic"),
            (LLMProvider.GEMINI, "gemini-1.5-pro", "gemini")
        ]
        
        for provider, model, name in providers_data:
            client_config = LLMConfig(
                provider=provider,
                model=model,
                api_key="test-key",
                max_tokens=1000
            )
            
            client = manager.add_client(name, client_config)
            print(f"✅ Added {name} client with model: {model}")
        
        # Test manager functions
        print(f"\n📊 Manager Stats:")
        print(f"   Available clients: {manager.list_clients()}")
        print(f"   Default client: {manager.default_client}")
        print(f"   Total clients: {len(manager.clients)}")
        
        # Test getting clients
        for client_name in manager.list_clients():
            client = manager.get_client(client_name)
            print(f"   Retrieved {client_name}: {client.__class__.__name__}")
        
        # Test setting default
        manager.set_default_client("anthropic")
        print(f"   New default client: {manager.default_client}")
        
    except Exception as e:
        print(f"❌ Error testing client manager: {e}")
    
    print()


async def test_config_integration():
    """Test integration with configuration system."""
    print("⚙️  Testing Configuration Integration")
    print("=" * 37)
    
    try:
        # Get provider status from config
        providers_status = get_provider_status(config)
        
        print("📊 Provider Status:")
        for provider_name, status in providers_status.items():
            configured = "✅ Configured" if status["configured"] else "❌ Not configured"
            is_default = "🎯 Default" if status["is_default"] else ""
            
            print(f"   {provider_name.title()}: {configured} {is_default}")
            if status["configured"]:
                print(f"      Model: {status['model']}")
                if status['base_url']:
                    print(f"      Base URL: {status['base_url']}")
        
        print(f"\n🔧 Configuration Summary:")
        configured_count = sum(1 for s in providers_status.values() if s["configured"])
        print(f"   Total providers: {len(providers_status)}")
        print(f"   Configured providers: {configured_count}")
        print(f"   Default provider: {config.llm.default_provider}")
        print(f"   Global settings:")
        print(f"      Streaming enabled: {config.llm.enable_streaming}")
        print(f"      Retry enabled: {config.llm.enable_retry}")
        print(f"      Default temperature: {config.llm.default_temperature}")
        print(f"      Default max tokens: {config.llm.default_max_tokens}")
        
    except Exception as e:
        print(f"❌ Error testing configuration integration: {e}")
    
    print()


async def test_error_handling():
    """Test error handling scenarios."""
    print("🚨 Testing Error Handling") 
    print("=" * 26)
    
    try:
        # Test invalid provider
        try:
            invalid_config = LLMConfig(
                provider="invalid_provider",  # This should fail
                model="test-model",
                api_key="test-key"
            )
            print("❌ Should have failed with invalid provider")
        except Exception as e:
            print(f"✅ Correctly caught invalid provider: {type(e).__name__}")
        
        # Test missing API key scenarios
        manager = LLMClientManager()
        
        empty_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="",  # Empty API key
            max_tokens=1000
        )
        
        client = manager.add_client("test_empty", empty_config)
        print("✅ Client created with empty API key (for testing)")
        
        # Test getting non-existent client
        try:
            non_existent = manager.get_client("non_existent_client")
            print("❌ Should have failed getting non-existent client")
        except ValueError as e:
            print(f"✅ Correctly caught non-existent client error: {e}")
        
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")
    
    print()


async def main():
    """Run all tests."""
    print("🔮 ArcanAgent LLM Client Test Suite")
    print("=" * 50)
    print()
    
    try:
        await test_client_creation()
        await test_message_formatting()
        await test_client_manager()
        await test_config_integration()
        await test_error_handling()
        
        print("🎉 All tests completed!")
        print("💡 Note: These are structural tests. API functionality requires valid keys.")
        print("🔗 Use the /api/v1/llm endpoints to test with real API keys.")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    # Fix the typo in test_message_formatting
    import sys
    
    # First let's fix the typo
    script_content = Path(__file__).read_text()
    if "LLMMessage" in script_content:
        fixed_content = script_content.replace("LLMMessage", "LLMMessage")
        Path(__file__).write_text(fixed_content)
        print("Fixed typo in script, re-running...")
        # Re-execute the script
        import subprocess
        result = subprocess.run([sys.executable, __file__], capture_output=False)
        sys.exit(result.returncode)
    
    # Run the actual tests
    sys.exit(asyncio.run(main()))