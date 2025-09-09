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
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_stream(self, request: LLMRequest):
        """Generate a streaming response from the LLM."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            base_url: Custom base URL for OpenAI API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.available_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response using OpenAI API."""
        try:
            messages = []
            
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            
            messages.append({"role": "user", "content": request.prompt})
            
            # Prepare function calling if specified
            kwargs = {
                "model": request.model or "gpt-4",
                "messages": messages,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            }
            
            if request.functions:
                kwargs["functions"] = request.functions
                if request.function_call:
                    kwargs["function_call"] = request.function_call
            
            response = await self.client.chat.completions.create(**kwargs)
            
            # Extract content and usage
            content = response.choices[0].message.content or ""
            usage = response.usage.dict() if response.usage else {}
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider="openai",
                usage=usage,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_stream(self, request: LLMRequest):
        """Generate a streaming response using OpenAI API."""
        try:
            messages = []
            
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            
            messages.append({"role": "user", "content": request.prompt})
            
            kwargs = {
                "model": request.model or "gpt-4",
                "messages": messages,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": True
            }
            
            if request.functions:
                kwargs["functions"] = request.functions
                if request.function_call:
                    kwargs["function_call"] = request.function_call
            
            stream = await self.client.chat.completions.create(**kwargs)
            
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
            base_url: Ollama server URL
        """
        self.base_url = base_url
        self.available_models = []
        self._load_available_models()
    
    def _load_available_models(self):
        """Load available models from Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model["name"] for model in data.get("models", [])]
            else:
                logger.warning(f"Failed to load Ollama models: {response.status_code}")
                self.available_models = ["llama2", "codellama", "mistral"]  # Default fallback
        except Exception as e:
            logger.warning(f"Failed to connect to Ollama: {e}")
            self.available_models = ["llama2", "codellama", "mistral"]  # Default fallback
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response using Ollama API."""
        try:
            # Prepare the request payload
            payload = {
                "model": request.model or self.available_models[0] if self.available_models else "llama2",
                "prompt": request.prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            }
            
            # Add system message if provided
            if request.system_message:
                payload["system"] = request.system_message
            
            # Make the request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            return LLMResponse(
                content=data.get("response", ""),
                model=data.get("model", request.model or "unknown"),
                provider="ollama",
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                },
                metadata={
                    "done": str(data.get("done", False)),
                    "context": str(data.get("context", []))
                }
            )
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def generate_stream(self, request: LLMRequest):
        """Generate a streaming response using Ollama API."""
        try:
            payload = {
                "model": request.model or self.available_models[0] if self.available_models else "llama2",
                "prompt": request.prompt,
                "stream": True,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            }
            
            if request.system_message:
                payload["system"] = request.system_message
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if "response" in data:
                            yield data["response"]
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available Ollama models."""
        return self.available_models


class LLMClient:
    """
    Main LLM client that manages different providers.
    
    Responsibilities:
    - Manage multiple LLM providers (OpenAI, Ollama)
    - Provide unified interface for LLM operations
    - Handle provider selection and fallback
    - Support both local and remote LLM access
    """
    
    def __init__(
        self,
        primary_provider: str = "openai",
        openai_api_key: Optional[str] = None,
        ollama_url: Optional[str] = None,
        fallback_provider: Optional[str] = None
    ):
        """
        Initialize the LLM client.
        
        Args:
            primary_provider: Primary provider to use ("openai" or "ollama")
            openai_api_key: OpenAI API key
            ollama_url: Ollama server URL
            fallback_provider: Fallback provider if primary fails
        """
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        self.providers = {}
        
        # Initialize providers
        if openai_api_key:
            self.providers["openai"] = OpenAIProvider(openai_api_key)
        
        if ollama_url:
            self.providers["ollama"] = OllamaProvider(ollama_url)
        else:
            # Try default Ollama URL
            try:
                self.providers["ollama"] = OllamaProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama: {e}")
        
        # Validate primary provider
        if primary_provider not in self.providers:
            available = list(self.providers.keys())
            if available:
                self.primary_provider = available[0]
                logger.warning(f"Primary provider {primary_provider} not available, using {self.primary_provider}")
            else:
                raise ValueError("No LLM providers available")
        
        logger.info(f"LLM client initialized with primary provider: {self.primary_provider}")
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
        functions: Optional[List[Dict]] = None,
        function_call: Optional[Union[str, Dict]] = None,
        use_fallback: bool = True
    ) -> LLMResponse:
        """
        Generate a response using the primary provider.
        
        Args:
            prompt: Input prompt
            model: Model to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System message for context
            functions: Available functions for function calling
            function_call: Function call specification
            use_fallback: Whether to use fallback provider on failure
            
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
        
        # Try primary provider
        try:
            provider = self.providers[self.primary_provider]
            return await provider.generate(request)
        except Exception as e:
            logger.error(f"Primary provider {self.primary_provider} failed: {e}")
            
            # Try fallback provider
            if use_fallback and self.fallback_provider and self.fallback_provider in self.providers:
                try:
                    provider = self.providers[self.fallback_provider]
                    logger.info(f"Using fallback provider: {self.fallback_provider}")
                    return await provider.generate(request)
                except Exception as fallback_error:
                    logger.error(f"Fallback provider {self.fallback_provider} also failed: {fallback_error}")
                    raise Exception(f"All providers failed. Primary: {e}, Fallback: {fallback_error}")
            else:
                raise
    
    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
        functions: Optional[List[Dict]] = None,
        function_call: Optional[Union[str, Dict]] = None
    ):
        """
        Generate a streaming response using the primary provider.
        
        Args:
            prompt: Input prompt
            model: Model to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: System message for context
            functions: Available functions for function calling
            function_call: Function call specification
            
        Yields:
            Response chunks
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
        
        provider = self.providers[self.primary_provider]
        async for chunk in provider.generate_stream(request):
            yield chunk
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models from all providers."""
        models = {}
        for name, provider in self.providers.items():
            try:
                models[name] = provider.get_available_models()
            except Exception as e:
                logger.warning(f"Failed to get models from {name}: {e}")
                models[name] = []
        return models
    
    def switch_provider(self, provider_name: str):
        """Switch the primary provider."""
        if provider_name in self.providers:
            self.primary_provider = provider_name
            logger.info(f"Switched to provider: {provider_name}")
        else:
            raise ValueError(f"Provider {provider_name} not available")
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about available providers."""
        info = {}
        for name, provider in self.providers.items():
            info[name] = {
                "type": type(provider).__name__,
                "models": len(provider.get_available_models()),
                "available": True
            }
        return info