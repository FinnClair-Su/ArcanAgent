"""
LLM Client Initializer

Initializes and configures LLM clients based on configuration settings.
Sets up the global client manager with all configured providers.
"""

import logging
import time
from typing import Dict, Any

from .llm_client import (
    LLMClientManager, 
    LLMConfig as ClientConfig, 
    LLMProvider,
    get_llm_client_manager
)
from ..config import ArcanAgentConfig

logger = logging.getLogger("ArcanAgent.LLMInitializer")


def initialize_llm_clients(config: ArcanAgentConfig) -> LLMClientManager:
    """
    Initialize all LLM clients based on configuration.
    
    Args:
        config: Application configuration
        
    Returns:
        LLMClientManager: Configured client manager
    """
    manager = get_llm_client_manager()
    
    # Clear any existing clients
    manager.clients.clear()
    
    # Track which clients were successfully initialized
    initialized_clients = []
    
    # Initialize OpenAI client
    if _is_provider_configured(config.llm.openai):
        try:
            client_config = ClientConfig(
                provider=LLMProvider.OPENAI,
                model=config.llm.openai.model,
                api_key=config.llm.openai.api_key,
                base_url=config.llm.openai.base_url,
                max_tokens=config.llm.openai.max_tokens,
                temperature=config.llm.openai.temperature,
                timeout=config.llm.openai.timeout,
                max_retries=config.llm.openai.max_retries
            )
            manager.add_client("openai", client_config)
            initialized_clients.append("openai")
            logger.info(f"✅ OpenAI client initialized with model: {config.llm.openai.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
    
    # Initialize Anthropic client
    if _is_provider_configured(config.llm.anthropic):
        try:
            client_config = ClientConfig(
                provider=LLMProvider.ANTHROPIC,
                model=config.llm.anthropic.model,
                api_key=config.llm.anthropic.api_key,
                base_url=config.llm.anthropic.base_url,
                max_tokens=config.llm.anthropic.max_tokens,
                temperature=config.llm.anthropic.temperature,
                timeout=config.llm.anthropic.timeout,
                max_retries=config.llm.anthropic.max_retries
            )
            manager.add_client("anthropic", client_config)
            initialized_clients.append("anthropic")
            logger.info(f"✅ Anthropic client initialized with model: {config.llm.anthropic.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Anthropic client: {e}")
    
    # Initialize Gemini client
    if _is_provider_configured(config.llm.gemini):
        try:
            client_config = ClientConfig(
                provider=LLMProvider.GEMINI,
                model=config.llm.gemini.model,
                api_key=config.llm.gemini.api_key,
                base_url=config.llm.gemini.base_url,
                max_tokens=config.llm.gemini.max_tokens,
                temperature=config.llm.gemini.temperature,
                timeout=config.llm.gemini.timeout,
                max_retries=config.llm.gemini.max_retries
            )
            manager.add_client("gemini", client_config)
            initialized_clients.append("gemini")
            logger.info(f"✅ Gemini client initialized with model: {config.llm.gemini.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
    
    # Initialize OpenRouter client
    if _is_provider_configured(config.llm.openrouter):
        try:
            client_config = ClientConfig(
                provider=LLMProvider.OPENROUTER,
                model=config.llm.openrouter.model,
                api_key=config.llm.openrouter.api_key,
                base_url=config.llm.openrouter.base_url,
                max_tokens=config.llm.openrouter.max_tokens,
                temperature=config.llm.openrouter.temperature,
                timeout=config.llm.openrouter.timeout,
                max_retries=config.llm.openrouter.max_retries
            )
            manager.add_client("openrouter", client_config)
            initialized_clients.append("openrouter")
            logger.info(f"✅ OpenRouter client initialized with model: {config.llm.openrouter.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenRouter client: {e}")
    
    # Initialize Deepseek client
    if _is_provider_configured(config.llm.deepseek):
        try:
            client_config = ClientConfig(
                provider=LLMProvider.DEEPSEEK,
                model=config.llm.deepseek.model,
                api_key=config.llm.deepseek.api_key,
                base_url=config.llm.deepseek.base_url,
                max_tokens=config.llm.deepseek.max_tokens,
                temperature=config.llm.deepseek.temperature,
                timeout=config.llm.deepseek.timeout,
                max_retries=config.llm.deepseek.max_retries
            )
            manager.add_client("deepseek", client_config)
            initialized_clients.append("deepseek")
            logger.info(f"✅ Deepseek client initialized with model: {config.llm.deepseek.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Deepseek client: {e}")
    
    # Initialize Alibaba client
    if _is_provider_configured(config.llm.alibaba):
        try:
            client_config = ClientConfig(
                provider=LLMProvider.ALIBABA,
                model=config.llm.alibaba.model,
                api_key=config.llm.alibaba.api_key,
                base_url=config.llm.alibaba.base_url,
                max_tokens=config.llm.alibaba.max_tokens,
                temperature=config.llm.alibaba.temperature,
                timeout=config.llm.alibaba.timeout,
                max_retries=config.llm.alibaba.max_retries
            )
            manager.add_client("alibaba", client_config)
            initialized_clients.append("alibaba")
            logger.info(f"✅ Alibaba client initialized with model: {config.llm.alibaba.model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Alibaba client: {e}")
    
    # Set default client
    if initialized_clients:
        default_provider = config.llm.default_provider
        if default_provider in initialized_clients:
            manager.set_default_client(default_provider)
            logger.info(f"🎯 Default LLM client set to: {default_provider}")
        else:
            # If configured default is not available, use the first initialized client
            fallback_client = initialized_clients[0]
            manager.set_default_client(fallback_client)
            logger.warning(f"⚠️ Configured default provider '{default_provider}' not available, using: {fallback_client}")
    else:
        logger.error("❌ No LLM clients were successfully initialized!")
        raise RuntimeError("No LLM clients available - check your configuration")
    
    logger.info(f"🔮 LLM client manager initialized with {len(initialized_clients)} providers: {initialized_clients}")
    return manager


def _is_provider_configured(provider_config: Any) -> bool:
    """
    Check if a provider is properly configured.
    
    Args:
        provider_config: Provider configuration object
        
    Returns:
        bool: True if provider is configured with valid API key
    """
    if not hasattr(provider_config, 'api_key'):
        return False
    
    api_key = provider_config.api_key
    
    # Check if API key is set and not a placeholder
    if not api_key or api_key in [
        "sk-your-openai-api-key-here",
        "sk-ant-your-anthropic-api-key-here", 
        "your-gemini-api-key-here",
        "sk-or-your-openrouter-api-key-here",
        "sk-your-deepseek-api-key-here",
        "sk-your-alibaba-api-key-here",
        ""
    ]:
        return False
    
    return True


def get_provider_status(config: ArcanAgentConfig) -> Dict[str, Dict[str, Any]]:
    """
    Get the status of all LLM providers.
    
    Args:
        config: Application configuration
        
    Returns:
        Dict containing status information for each provider
    """
    providers_status = {}
    
    providers = [
        ("openai", config.llm.openai),
        ("anthropic", config.llm.anthropic),
        ("gemini", config.llm.gemini),
        ("openrouter", config.llm.openrouter),
        ("deepseek", config.llm.deepseek),
        ("alibaba", config.llm.alibaba)
    ]
    
    for name, provider_config in providers:
        is_configured = _is_provider_configured(provider_config)
        
        providers_status[name] = {
            "configured": is_configured,
            "model": provider_config.model if is_configured else None,
            "base_url": getattr(provider_config, 'base_url', None),
            "is_default": name == config.llm.default_provider
        }
    
    return providers_status


async def test_llm_client(client_name: str = None) -> Dict[str, Any]:
    """
    Test an LLM client with a simple request.
    
    Args:
        client_name: Name of the client to test (None for default)
        
    Returns:
        Dict containing test results
    """
    from .llm_client import LLMMessage, get_llm_client
    
    try:
        client = get_llm_client(client_name)
        
        test_messages = [
            LLMMessage(role="user", content="Hello! Please respond with just 'OK' to confirm you're working.")
        ]
        
        start_time = time.time()
        
        async with client:
            response = await client.chat_completion(test_messages)
        
        response_time = time.time() - start_time
        
        return {
            "success": True,
            "client_name": client_name or "default",
            "model": response.model,
            "provider": response.provider,
            "response_content": response.content[:100],  # First 100 chars
            "response_time": round(response_time, 2),
            "usage": response.usage
        }
        
    except Exception as e:
        return {
            "success": False,
            "client_name": client_name or "default",
            "error": str(e),
            "error_type": type(e).__name__
        }