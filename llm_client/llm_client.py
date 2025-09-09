"""
LLM Client Module

Provides provider adapters with a clear selection mechanism for chosen backends.
Supports both local (Ollama) and remote (OpenAI) LLM providers.

Chosen libraries:
- OpenAI: Remote LLM API access
- requests: HTTP client for Ollama API
- pydantic: Data validation and type safety
- asyncio: Asynchronous operations

Adapted from: OpenAI Cookbook (https://github.com/openai/openai-cookbook)
Pattern: Modular LLM integration with provider abstraction
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

import openai
import pydantic
import requests

logger = logging.getLogger(__name__)


class LLMResponse(pydantic.BaseModel):
    """Model for LLM responses."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = {}
    metadata: Dict[str, str] = {}


class LLMRequest(pydantic.BaseModel):
    """Model for LLM requests."""
    prompt: str
    model: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    system_message: Optional[str] = None
    functions: Optional[List[Dict]] = None
    function_call: Optional[Union[str, Dict]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_completion(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion using the provider."""
        pass
    
    @abstractmethod
    async def generate_completion_stream(self, request: LLMRequest):
        """Generate a streaming completion using the provider."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            base_url: Optional custom base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.available_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
    
    async def generate_completion(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using OpenAI API."""
        try:
            messages = []
            
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            
            messages.append({"role": "user", "content": request.prompt})
            
            response = await self.client.chat.completions.create(
                model=request.model or "gpt-4o-mini",
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                functions=request.functions,
                function_call=request.function_call
            )
            
            content = response.choices[0].message.content or ""
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model": response.model
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_completion_stream(self, request: LLMRequest):
        """Generate streaming completion using OpenAI API."""
        try:
            messages = []
            
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            
            messages.append({"role": "user", "content": request.prompt})
            
            stream = await self.client.chat.completions.create(
                model=request.model or "gpt-4o-mini",
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        return self.available_models


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Ollama API base URL
        """
        self.base_url = base_url
        self.available_models = [
            "llama2",
            "codellama",
            "mistral",
            "neural-chat",
            "starling-lm"
        ]
    
    async def generate_completion(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using Ollama API."""
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": request.model or "llama2",
                "prompt": request.prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            }
            
            if request.system_message:
                payload["system"] = request.system_message
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            
            return LLMResponse(
                content=data.get("response", ""),
                model=data.get("model", request.model or "llama2"),
                provider="ollama",
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                },
                metadata={
                    "model": data.get("model", ""),
                    "created_at": data.get("created_at", "")
                }
            )
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def generate_completion_stream(self, request: LLMRequest):
        """Generate streaming completion using Ollama API."""
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": request.model or "llama2",
                "prompt": request.prompt,
                "stream": True,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            }
            
            if request.system_message:
                payload["system"] = request.system_message
            
            response = requests.post(url, json=payload, stream=True, timeout=120)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    if "response" in data:
                        yield data["response"]
                        
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.warning(f"Failed to fetch Ollama models: {e}")
            return self.available_models


class LLMClient:
    """
    Unified LLM client that manages different providers.
    
    Responsibilities:
    - Provider selection and management
    - Request/response handling
    - Error handling and retries
    - Model management
    """
    
    def __init__(
        self,
        provider: str = "openai",
        openai_api_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
        openai_base_url: Optional[str] = None
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: Primary provider to use ("openai" or "ollama")
            openai_api_key: OpenAI API key
            ollama_base_url: Ollama API base URL
            openai_base_url: Optional custom OpenAI base URL
        """
        self.provider_name = provider
        self.providers = {}
        
        # Initialize OpenAI provider
        if openai_api_key:
            self.providers["openai"] = OpenAIProvider(
                api_key=openai_api_key,
                base_url=openai_base_url
            )
        
        # Initialize Ollama provider
        self.providers["ollama"] = OllamaProvider(base_url=ollama_base_url)
        
        # Set primary provider
        if provider in self.providers:
            self.primary_provider = self.providers[provider]
        else:
            # Fallback to available provider
            available_providers = list(self.providers.keys())
            if available_providers:
                self.primary_provider = self.providers[available_providers[0]]
                self.provider_name = available_providers[0]
                logger.warning(f"Requested provider '{provider}' not available. Using '{self.provider_name}'")
            else:
                raise ValueError("No LLM providers available. Please configure API keys.")
        
        logger.info(f"LLM client initialized with provider: {self.provider_name}")
    
    async def generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
        functions: Optional[List[Dict]] = None,
        function_call: Optional[Union[str, Dict]] = None
    ) -> LLMResponse:
        """
        Generate a completion using the primary provider.
        
        Args:
            prompt: Input prompt
            model: Model to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System message (optional)
            functions: Function definitions (optional)
            function_call: Function call specification (optional)
            
        Returns:
            LLM response
        """
        request = LLMRequest(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_message=system_message,
            functions=functions,
            function_call=function_call
        )
        
        return await self.primary_provider.generate_completion(request)
    
    async def generate_completion_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_message: Optional[str] = None
    ):
        """
        Generate a streaming completion using the primary provider.
        
        Args:
            prompt: Input prompt
            model: Model to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System message (optional)
            
        Yields:
            Chunks of generated text
        """
        request = LLMRequest(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_message=system_message
        )
        
        async for chunk in self.primary_provider.generate_completion_stream(request):
            yield chunk
    
    def get_available_models(self) -> List[str]:
        """Get available models from the primary provider."""
        return self.primary_provider.get_available_models()
    
    def switch_provider(self, provider: str) -> bool:
        """
        Switch to a different provider.
        
        Args:
            provider: Provider name to switch to
            
        Returns:
            True if successful, False otherwise
        """
        if provider in self.providers:
            self.primary_provider = self.providers[provider]
            self.provider_name = provider
            logger.info(f"Switched to provider: {provider}")
            return True
        else:
            logger.error(f"Provider '{provider}' not available")
            return False
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about available providers."""
        return {
            "current_provider": self.provider_name,
            "available_providers": list(self.providers.keys()),
            "available_models": self.get_available_models()
        }