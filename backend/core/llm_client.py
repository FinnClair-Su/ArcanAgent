"""
LLM Client Interface

Unified interface for multiple LLM providers including:
- OpenAI GPT models
- Anthropic Claude models  
- Google Gemini models
- OpenRouter API
- Deepseek models
- Alibaba Cloud (DashScope) models

Supports streaming responses and implements retry logic with exponential backoff.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, AsyncGenerator, Any, Union
import aiohttp
import time
from urllib.parse import urljoin

logger = logging.getLogger("ArcanAgent.LLMClient")


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    DEEPSEEK = "deepseek"
    ALIBABA = "alibaba"


@dataclass
class LLMMessage:
    """Standard message format for all LLM providers."""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None


@dataclass
class LLMResponse:
    """Standard response format from LLM providers."""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    response_time: Optional[float] = None


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: LLMProvider
    model: str
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 60
    max_retries: int = 3


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class LLMRateLimitError(LLMClientError):
    """Rate limit exceeded error."""
    pass


class LLMAuthenticationError(LLMClientError):
    """Authentication error."""
    pass


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()
    
    async def _ensure_session(self):
        """Ensure HTTP session is created."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        stream: bool = False
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """Generate chat completion."""
        pass
    
    @abstractmethod
    def _format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Format messages for the specific provider."""
        pass
    
    async def _retry_request(self, request_func, *args, **kwargs):
        """Retry request with exponential backoff."""
        for attempt in range(self.config.max_retries):
            try:
                return await request_func(*args, **kwargs)
            except (LLMRateLimitError, aiohttp.ClientError) as e:
                if attempt == self.config.max_retries - 1:
                    raise
                
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)


class OpenAIClient(BaseLLMClient):
    """OpenAI API client."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.openai.com/v1"
    
    def _format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Format messages for OpenAI API."""
        formatted = []
        for msg in messages:
            formatted_msg = {"role": msg.role, "content": msg.content}
            if msg.name:
                formatted_msg["name"] = msg.name
            formatted.append(formatted_msg)
        return formatted
    
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        stream: bool = False
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """Generate chat completion using OpenAI API."""
        await self._ensure_session()
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": self._format_messages(messages),
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": stream
        }
        
        return await self._retry_request(self._make_request, headers, payload, stream)
    
    async def _make_request(self, headers, payload, stream):
        """Make the actual API request."""
        url = urljoin(self.base_url, "/chat/completions")
        start_time = time.time()
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 401:
                raise LLMAuthenticationError("Invalid API key")
            elif response.status == 429:
                raise LLMRateLimitError("Rate limit exceeded")
            elif response.status != 200:
                error_text = await response.text()
                raise LLMClientError(f"API request failed: {response.status} - {error_text}")
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                data = await response.json()
                response_time = time.time() - start_time
                
                return LLMResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=data["model"],
                    provider=self.config.provider.value,
                    usage=data.get("usage"),
                    finish_reason=data["choices"][0].get("finish_reason"),
                    response_time=response_time
                )
    
    async def _handle_streaming_response(self, response):
        """Handle streaming response from OpenAI."""
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                data_str = line[6:]  # Remove 'data: ' prefix
                if data_str == '[DONE]':
                    break
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        if 'content' in delta:
                            yield delta['content']
                except json.JSONDecodeError:
                    continue


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API client."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.anthropic.com"
    
    def _format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Format messages for Anthropic API."""
        formatted = []
        for msg in messages:
            formatted.append({"role": msg.role, "content": msg.content})
        return formatted
    
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        stream: bool = False
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """Generate chat completion using Anthropic API."""
        await self._ensure_session()
        
        headers = {
            "X-API-Key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Separate system message from conversation
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append(msg)
        
        payload = {
            "model": self.config.model,
            "messages": self._format_messages(conversation_messages),
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": stream
        }
        
        if system_message:
            payload["system"] = system_message
        
        return await self._retry_request(self._make_request, headers, payload, stream)
    
    async def _make_request(self, headers, payload, stream):
        """Make the actual API request."""
        url = urljoin(self.base_url, "/v1/messages")
        start_time = time.time()
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 401:
                raise LLMAuthenticationError("Invalid API key")
            elif response.status == 429:
                raise LLMRateLimitError("Rate limit exceeded")
            elif response.status != 200:
                error_text = await response.text()
                raise LLMClientError(f"API request failed: {response.status} - {error_text}")
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                data = await response.json()
                response_time = time.time() - start_time
                
                return LLMResponse(
                    content=data["content"][0]["text"],
                    model=data["model"],
                    provider=self.config.provider.value,
                    usage=data.get("usage"),
                    finish_reason=data.get("stop_reason"),
                    response_time=response_time
                )
    
    async def _handle_streaming_response(self, response):
        """Handle streaming response from Anthropic."""
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    if data.get("type") == "content_block_delta":
                        yield data["delta"]["text"]
                except json.JSONDecodeError:
                    continue


class GeminiClient(BaseLLMClient):
    """Google Gemini API client."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://generativelanguage.googleapis.com/v1beta"
    
    def _format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Format messages for Gemini API."""
        formatted = []
        for msg in messages:
            # Gemini uses different role names
            role = "model" if msg.role == "assistant" else msg.role
            formatted.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        return formatted
    
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        stream: bool = False
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """Generate chat completion using Gemini API."""
        await self._ensure_session()
        
        # Separate system message
        system_instruction = None
        conversation_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            else:
                conversation_messages.append(msg)
        
        payload = {
            "contents": self._format_messages(conversation_messages),
            "generationConfig": {
                "maxOutputTokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        
        endpoint = "streamGenerateContent" if stream else "generateContent"
        return await self._retry_request(self._make_request, payload, stream, endpoint)
    
    async def _make_request(self, payload, stream, endpoint):
        """Make the actual API request."""
        url = f"{self.base_url}/models/{self.config.model}:{endpoint}?key={self.config.api_key}"
        start_time = time.time()
        
        headers = {"Content-Type": "application/json"}
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 401:
                raise LLMAuthenticationError("Invalid API key")
            elif response.status == 429:
                raise LLMRateLimitError("Rate limit exceeded")
            elif response.status != 200:
                error_text = await response.text()
                raise LLMClientError(f"API request failed: {response.status} - {error_text}")
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                data = await response.json()
                response_time = time.time() - start_time
                
                if "candidates" not in data or not data["candidates"]:
                    raise LLMClientError("No response generated")
                
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                
                return LLMResponse(
                    content=content,
                    model=self.config.model,
                    provider=self.config.provider.value,
                    usage=data.get("usageMetadata"),
                    finish_reason=data["candidates"][0].get("finishReason"),
                    response_time=response_time
                )
    
    async def _handle_streaming_response(self, response):
        """Handle streaming response from Gemini."""
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    if "candidates" in data and data["candidates"]:
                        parts = data["candidates"][0]["content"]["parts"]
                        if parts:
                            yield parts[0]["text"]
                except json.JSONDecodeError:
                    continue


class OpenRouterClient(OpenAIClient):
    """OpenRouter API client (inherits from OpenAI as it uses compatible API)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://openrouter.ai/api/v1"
    
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        stream: bool = False
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """Generate chat completion using OpenRouter API."""
        await self._ensure_session()
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/arcanagent/arcanagent",
            "X-Title": "ArcanAgent"
        }
        
        payload = {
            "model": self.config.model,
            "messages": self._format_messages(messages),
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": stream
        }
        
        return await self._retry_request(self._make_request, headers, payload, stream)


class DeepseekClient(OpenAIClient):
    """Deepseek API client (uses OpenAI-compatible API)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.deepseek.com/v1"


class AlibabaClient(OpenAIClient):
    """Alibaba Cloud DashScope API client (uses OpenAI-compatible API)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"


class LLMClientManager:
    """Manager for multiple LLM clients."""
    
    def __init__(self):
        self.clients: Dict[str, BaseLLMClient] = {}
        self.default_client: Optional[str] = None
    
    def add_client(self, name: str, config: LLMConfig) -> BaseLLMClient:
        """Add a new LLM client."""
        client_classes = {
            LLMProvider.OPENAI: OpenAIClient,
            LLMProvider.ANTHROPIC: AnthropicClient,
            LLMProvider.GEMINI: GeminiClient,
            LLMProvider.OPENROUTER: OpenRouterClient,
            LLMProvider.DEEPSEEK: DeepseekClient,
            LLMProvider.ALIBABA: AlibabaClient
        }
        
        client_class = client_classes.get(config.provider)
        if not client_class:
            raise ValueError(f"Unsupported provider: {config.provider}")
        
        client = client_class(config)
        self.clients[name] = client
        
        if self.default_client is None:
            self.default_client = name
        
        logger.info(f"Added LLM client: {name} ({config.provider.value})")
        return client
    
    def get_client(self, name: Optional[str] = None) -> BaseLLMClient:
        """Get a client by name or return the default client."""
        if name is None:
            name = self.default_client
        
        if name is None or name not in self.clients:
            raise ValueError(f"Client not found: {name}")
        
        return self.clients[name]
    
    def set_default_client(self, name: str):
        """Set the default client."""
        if name not in self.clients:
            raise ValueError(f"Client not found: {name}")
        self.default_client = name
    
    def list_clients(self) -> List[str]:
        """List all available clients."""
        return list(self.clients.keys())
    
    async def close_all(self):
        """Close all client sessions."""
        for client in self.clients.values():
            await client._close_session()


# Global client manager instance
_client_manager = LLMClientManager()


def get_llm_client_manager() -> LLMClientManager:
    """Get the global LLM client manager."""
    return _client_manager


def get_llm_client(name: Optional[str] = None) -> BaseLLMClient:
    """Get an LLM client from the global manager."""
    return _client_manager.get_client(name)


async def chat_completion(
    messages: List[LLMMessage],
    client_name: Optional[str] = None,
    stream: bool = False
) -> Union[LLMResponse, AsyncGenerator[str, None]]:
    """Convenience function for chat completion."""
    client = get_llm_client(client_name)
    async with client:
        return await client.chat_completion(messages, stream=stream)