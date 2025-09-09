"""
Tests for LLM client module.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch
from llm_client import LLMClient, LLMRequest, LLMResponse


class TestLLMClient:
    """Test cases for LLMClient."""
    
    @pytest.fixture
    def mock_openai_provider(self):
        """Create a mock OpenAI provider."""
        with patch('llm_client.OpenAIProvider') as mock:
            provider = Mock()
            provider.generate.return_value = LLMResponse(
                content="Test response",
                model="gpt-4",
                provider="openai",
                usage={"total_tokens": 100}
            )
            provider.get_available_models.return_value = ["gpt-4", "gpt-3.5-turbo"]
            mock.return_value = provider
            yield provider
    
    @pytest.fixture
    def mock_ollama_provider(self):
        """Create a mock Ollama provider."""
        with patch('llm_client.OllamaProvider') as mock:
            provider = Mock()
            provider.generate.return_value = LLMResponse(
                content="Test response",
                model="llama2",
                provider="ollama",
                usage={"total_tokens": 100}
            )
            provider.get_available_models.return_value = ["llama2", "codellama"]
            mock.return_value = provider
            yield provider
    
    def test_init_with_openai(self, mock_openai_provider):
        """Test initialization with OpenAI provider."""
        client = LLMClient(
            primary_provider="openai",
            openai_api_key="test_key"
        )
        
        assert client.primary_provider == "openai"
        assert "openai" in client.providers
    
    def test_init_with_ollama(self, mock_ollama_provider):
        """Test initialization with Ollama provider."""
        client = LLMClient(
            primary_provider="ollama",
            ollama_url="http://localhost:11434"
        )
        
        assert client.primary_provider == "ollama"
        assert "ollama" in client.providers
    
    def test_init_without_providers(self):
        """Test initialization without any providers."""
        with pytest.raises(ValueError, match="No LLM providers available"):
            LLMClient()
    
    @pytest.mark.asyncio
    async def test_generate_with_openai(self, mock_openai_provider):
        """Test text generation with OpenAI."""
        client = LLMClient(
            primary_provider="openai",
            openai_api_key="test_key"
        )
        
        response = await client.generate(
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.7
        )
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"
        assert response.provider == "openai"
        mock_openai_provider.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_with_ollama(self, mock_ollama_provider):
        """Test text generation with Ollama."""
        client = LLMClient(
            primary_provider="ollama",
            ollama_url="http://localhost:11434"
        )
        
        response = await client.generate(
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.7
        )
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"
        assert response.provider == "ollama"
        mock_ollama_provider.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_with_fallback(self, mock_openai_provider, mock_ollama_provider):
        """Test generation with fallback provider."""
        # Make OpenAI provider fail
        mock_openai_provider.generate.side_effect = Exception("OpenAI failed")
        
        client = LLMClient(
            primary_provider="openai",
            openai_api_key="test_key",
            fallback_provider="ollama",
            ollama_url="http://localhost:11434"
        )
        
        response = await client.generate(
            prompt="Test prompt",
            use_fallback=True
        )
        
        assert isinstance(response, LLMResponse)
        assert response.provider == "ollama"
        mock_ollama_provider.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_stream(self, mock_openai_provider):
        """Test streaming generation."""
        # Mock streaming response
        async def mock_stream():
            yield "chunk1"
            yield "chunk2"
            yield "chunk3"
        
        mock_openai_provider.generate_stream.return_value = mock_stream()
        
        client = LLMClient(
            primary_provider="openai",
            openai_api_key="test_key"
        )
        
        chunks = []
        async for chunk in client.generate_stream(prompt="Test prompt"):
            chunks.append(chunk)
        
        assert chunks == ["chunk1", "chunk2", "chunk3"]
        mock_openai_provider.generate_stream.assert_called_once()
    
    def test_get_available_models(self, mock_openai_provider, mock_ollama_provider):
        """Test getting available models."""
        client = LLMClient(
            primary_provider="openai",
            openai_api_key="test_key",
            ollama_url="http://localhost:11434"
        )
        
        models = client.get_available_models()
        
        assert isinstance(models, dict)
        assert "openai" in models
        assert "ollama" in models
        assert models["openai"] == ["gpt-4", "gpt-3.5-turbo"]
        assert models["ollama"] == ["llama2", "codellama"]
    
    def test_switch_provider(self, mock_openai_provider, mock_ollama_provider):
        """Test switching providers."""
        client = LLMClient(
            primary_provider="openai",
            openai_api_key="test_key",
            ollama_url="http://localhost:11434"
        )
        
        assert client.primary_provider == "openai"
        
        client.switch_provider("ollama")
        assert client.primary_provider == "ollama"
        
        with pytest.raises(ValueError, match="Provider unknown not available"):
            client.switch_provider("unknown")
    
    def test_get_provider_info(self, mock_openai_provider, mock_ollama_provider):
        """Test getting provider information."""
        client = LLMClient(
            primary_provider="openai",
            openai_api_key="test_key",
            ollama_url="http://localhost:11434"
        )
        
        info = client.get_provider_info()
        
        assert isinstance(info, dict)
        assert "openai" in info
        assert "ollama" in info
        assert info["openai"]["type"] == "OpenAIProvider"
        assert info["ollama"]["type"] == "OllamaProvider"
    
    def test_llm_request_validation(self):
        """Test LLM request validation."""
        request = LLMRequest(
            prompt="Test prompt",
            model="gpt-4",
            max_tokens=100,
            temperature=0.7,
            system_message="You are a helpful assistant."
        )
        
        assert request.prompt == "Test prompt"
        assert request.model == "gpt-4"
        assert request.max_tokens == 100
        assert request.temperature == 0.7
        assert request.system_message == "You are a helpful assistant."
    
    def test_llm_response_validation(self):
        """Test LLM response validation."""
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            provider="openai",
            usage={"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50},
            metadata={"finish_reason": "stop"}
        )
        
        assert response.content == "Test response"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.usage["total_tokens"] == 100
        assert response.metadata["finish_reason"] == "stop"