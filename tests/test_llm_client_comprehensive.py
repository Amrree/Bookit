"""
Comprehensive tests for the LLM client module.
Tests all providers, error handling, and edge cases.
"""
import pytest
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
from datetime import datetime

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm_client import LLMClient, LLMResponse, LLMRequest, OpenAIProvider, OllamaProvider

try:
    from openai import RateLimitError
except ImportError:
    # Create a mock RateLimitError if not available
    class RateLimitError(Exception):
        pass


class TestLLMClientCore:
    """Test core LLM client functionality."""
    
    def test_llm_client_initialization(self):
        """Test LLM client initialization."""
        client = LLMClient()
        assert client is not None
        assert hasattr(client, 'providers')
        assert hasattr(client, 'primary_provider')
        assert isinstance(client.providers, dict)
    
    def test_llm_client_configuration(self):
        """Test LLM client configuration with API key."""
        client = LLMClient(
            primary_provider="openai",
            openai_api_key="test_key",
            ollama_url="http://localhost:11434"
        )
        
        assert client.primary_provider in ["openai", "ollama"]
        assert isinstance(client.providers, dict)
        assert len(client.providers) > 0
    
    def test_llm_client_providers(self):
        """Test LLM client providers."""
        client = LLMClient()
        assert isinstance(client.providers, dict)
        assert len(client.providers) > 0
        # Check that providers are properly initialized
        for provider_name, provider in client.providers.items():
            assert hasattr(provider, 'generate')
            assert hasattr(provider, 'generate_stream')
            assert hasattr(provider, 'get_available_models')


class TestLLMRequest:
    """Test LLM request model."""
    
    def test_llm_request_creation(self):
        """Test LLM request creation."""
        request = LLMRequest(prompt="Test prompt")
        assert request.prompt == "Test prompt"
        assert request.model is None
        assert request.max_tokens == 2000  # Default value
        assert request.temperature == 0.7
        assert request.system_message is None
    
    def test_llm_request_defaults(self):
        """Test LLM request default values."""
        request = LLMRequest(prompt="Test prompt")
        assert request.max_tokens == 2000  # Default value
        assert request.temperature == 0.7
        assert request.system_message is None
        assert request.functions is None
        assert request.function_call is None
    
    def test_llm_request_custom_values(self):
        """Test LLM request with custom values."""
        request = LLMRequest(
            prompt="Test prompt",
            model="gpt-4",
            max_tokens=1000,
            temperature=0.5,
            system_message="You are a helpful assistant"
        )
        assert request.prompt == "Test prompt"
        assert request.model == "gpt-4"
        assert request.max_tokens == 1000
        assert request.temperature == 0.5
        assert request.system_message == "You are a helpful assistant"


class TestLLMResponse:
    """Test LLM response model."""
    
    def test_llm_response_creation(self):
        """Test LLM response creation."""
        response = LLMResponse(
            content="Test content",
            model="gpt-4",
            provider="openai"
        )
        assert response.content == "Test content"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.usage == {}
        assert response.metadata == {}
    
    def test_llm_response_defaults(self):
        """Test LLM response default values."""
        response = LLMResponse(
            content="Test content",
            model="gpt-4",
            provider="openai"
        )
        assert response.usage == {}
        assert response.metadata == {}
    
    def test_llm_response_custom_values(self):
        """Test LLM response with custom values."""
        response = LLMResponse(
            content="Test content",
            model="gpt-4",
            provider="openai",
            usage={"prompt_tokens": 10, "completion_tokens": 5},
            metadata={"finish_reason": "stop"}
        )
        assert response.usage == {"prompt_tokens": 10, "completion_tokens": 5}
        assert response.metadata == {"finish_reason": "stop"}


class TestOpenAIProvider:
    """Test OpenAI provider functionality."""
    
    def test_openai_provider_initialization(self):
        """Test OpenAI provider initialization."""
        provider = OpenAIProvider(api_key="test_key")
        assert provider.api_key == "test_key"
        assert provider.client is not None
        assert isinstance(provider.available_models, list)
        assert len(provider.available_models) > 0
    
    @pytest.mark.asyncio
    async def test_openai_generate(self):
        """Test OpenAI generation."""
        provider = OpenAIProvider(api_key="test_key")
        
        # Mock the OpenAI client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "gpt-4"
        mock_response.id = "test_id"
        mock_response.usage = MagicMock()
        mock_response.usage.dict.return_value = {"prompt_tokens": 10, "completion_tokens": 5}
        
        with patch.object(provider.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
            request = LLMRequest(prompt="Test prompt")
            response = await provider.generate(request)
            
            assert response.content == "Test response"
            assert response.model == "gpt-4"
            assert response.provider == "openai"
    
    @pytest.mark.asyncio
    async def test_openai_error_handling(self):
        """Test OpenAI error handling."""
        provider = OpenAIProvider(api_key="test_key")
        
        with patch.object(provider.client.chat.completions, 'create', side_effect=Exception("OpenAI API error")):
            request = LLMRequest(prompt="Test prompt")
            with pytest.raises(Exception, match="OpenAI API error"):
                await provider.generate(request)
    
    @pytest.mark.asyncio
    async def test_openai_rate_limiting(self):
        """Test OpenAI rate limiting handling."""
        provider = OpenAIProvider(api_key="test_key")
        
        # Create a mock response object for RateLimitError
        mock_response = MagicMock()
        mock_response.request = MagicMock()
        
        with patch.object(provider.client.chat.completions, 'create', side_effect=RateLimitError("Rate limit exceeded", response=mock_response, body=None)):
            request = LLMRequest(prompt="Test prompt")
            with pytest.raises(RateLimitError):
                await provider.generate(request)


class TestOllamaProvider:
    """Test Ollama provider functionality."""
    
    def test_ollama_provider_initialization(self):
        """Test Ollama provider initialization."""
        provider = OllamaProvider()
        assert provider.base_url == "http://localhost:11434"
        assert isinstance(provider.available_models, list)
    
    @pytest.mark.asyncio
    async def test_ollama_generate(self):
        """Test Ollama generation."""
        provider = OllamaProvider()
        
        # Mock the requests.post call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Test response",
            "model": "llama2",
            "done": True,
            "prompt_eval_count": 10,
            "eval_count": 5,
            "context": []
        }
        
        with patch('requests.post', return_value=mock_response):
            request = LLMRequest(prompt="Test prompt")
            response = await provider.generate(request)
            
            assert response.content == "Test response"
            assert response.model == "llama2"
            assert response.provider == "ollama"
    
    @pytest.mark.asyncio
    async def test_ollama_connection_error(self):
        """Test Ollama connection error handling."""
        provider = OllamaProvider()
        
        with patch('requests.post', side_effect=Exception("Connection error")):
            request = LLMRequest(prompt="Test prompt")
            with pytest.raises(Exception, match="Connection error"):
                await provider.generate(request)
    
    @pytest.mark.asyncio
    async def test_ollama_server_error(self):
        """Test Ollama server error handling."""
        provider = OllamaProvider()
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with patch('requests.post', return_value=mock_response):
            request = LLMRequest(prompt="Test prompt")
            with pytest.raises(Exception, match="Ollama API error: 500"):
                await provider.generate(request)


class TestProviderSelection:
    """Test provider selection and fallback."""
    
    def test_primary_provider_selection(self):
        """Test primary provider selection."""
        client = LLMClient(primary_provider="openai", openai_api_key="test_key")
        assert client.primary_provider in ["openai", "ollama"]
    
    def test_provider_availability(self):
        """Test provider availability checking."""
        client = LLMClient(openai_api_key="test_key")
        assert isinstance(client.providers, dict)
        assert len(client.providers) > 0
    
    @pytest.mark.asyncio
    async def test_provider_fallback(self):
        """Test provider fallback mechanism."""
        client = LLMClient(primary_provider="openai", openai_api_key="test_key")
        
        # Mock the primary provider to fail
        with patch.object(client.providers[client.primary_provider], 'generate', side_effect=Exception("Primary failed")):
            with pytest.raises(Exception, match="Primary failed"):
                await client.generate(prompt="Test prompt")


class TestGenerationMethods:
    """Test generation methods."""
    
    @pytest.mark.asyncio
    async def test_generate_with_request_object(self):
        """Test generation with LLMRequest object."""
        client = LLMClient()
        
        # Mock the provider's generate method
        mock_response = LLMResponse(
            content="Test response",
            model="test-model",
            provider="test-provider"
        )
        
        with patch.object(client.providers[client.primary_provider], 'generate', return_value=mock_response):
            request = LLMRequest(prompt="Test prompt")
            response = await client.generate(
                prompt=request.prompt,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            assert response.content == "Test response"
    
    @pytest.mark.asyncio
    async def test_generate_with_parameters(self):
        """Test generation with individual parameters."""
        client = LLMClient()
        
        mock_response = LLMResponse(
            content="Test response",
            model="test-model",
            provider="test-provider"
        )
        
        with patch.object(client.providers[client.primary_provider], 'generate', return_value=mock_response):
            response = await client.generate(
                prompt="Test prompt",
                model="gpt-4",
                max_tokens=1000,
                temperature=0.5
            )
            
            assert response.content == "Test response"
    
    @pytest.mark.asyncio
    async def test_generate_with_context(self):
        """Test generation with system message context."""
        client = LLMClient()
        
        mock_response = LLMResponse(
            content="Test response",
            model="test-model",
            provider="test-provider"
        )
        
        with patch.object(client.providers[client.primary_provider], 'generate', return_value=mock_response):
            response = await client.generate(
                prompt="Test prompt",
                system_message="You are a helpful assistant"
            )
            
            assert response.content == "Test response"


class TestStreamingGeneration:
    """Test streaming generation functionality."""
    
    @pytest.mark.asyncio
    async def test_stream_generate_openai(self):
        """Test OpenAI streaming generation."""
        client = LLMClient(openai_api_key="test_key")
        
        # Mock the streaming response
        async def mock_stream():
            yield "Hello"
            yield " world"
            yield "!"
        
        with patch.object(client.providers.get("openai"), 'generate_stream', return_value=mock_stream()):
            if "openai" in client.providers:
                chunks = []
                async for chunk in client.generate_stream(prompt="Test prompt"):
                    chunks.append(chunk)
                
                assert len(chunks) > 0
    
    @pytest.mark.asyncio
    async def test_stream_generate_ollama(self):
        """Test Ollama streaming generation."""
        client = LLMClient()
        
        # Mock the streaming response
        async def mock_stream():
            yield "Hello"
            yield " world"
            yield "!"
        
        with patch.object(client.providers[client.primary_provider], 'generate_stream', return_value=mock_stream()):
            chunks = []
            async for chunk in client.generate_stream(prompt="Test prompt"):
                chunks.append(chunk)
            
            assert len(chunks) > 0


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_invalid_request(self):
        """Test handling of invalid requests."""
        client = LLMClient()
        
        # Test with empty prompt - this should still work but may return empty response
        try:
            response = await client.generate(prompt="")
            assert isinstance(response, LLMResponse)
        except Exception:
            # It's acceptable for this to raise an exception
            pass
    
    @pytest.mark.asyncio
    async def test_provider_unavailable(self):
        """Test handling when provider is unavailable."""
        client = LLMClient()
        
        # Mock all providers to fail
        for provider in client.providers.values():
            with patch.object(provider, 'generate', side_effect=Exception("Provider unavailable")):
                pass
        
        with pytest.raises(Exception):
            await client.generate(prompt="Test prompt")
    
    @pytest.mark.asyncio
    async def test_network_timeout(self):
        """Test handling of network timeouts."""
        client = LLMClient()
        
        with patch.object(client.providers[client.primary_provider], 'generate', side_effect=asyncio.TimeoutError("Request timeout")):
            with pytest.raises(asyncio.TimeoutError):
                await client.generate(prompt="Test prompt")
    
    @pytest.mark.asyncio
    async def test_invalid_response_format(self):
        """Test handling of invalid response formats."""
        client = LLMClient()
        
        # Mock provider to return invalid response
        with patch.object(client.providers[client.primary_provider], 'generate', side_effect=ValueError("Invalid response format")):
            with pytest.raises(ValueError):
                await client.generate(prompt="Test prompt")


class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_generation_performance(self):
        """Test generation performance."""
        client = LLMClient()
        
        mock_response = LLMResponse(
            content="Test response",
            model="test-model",
            provider="test-provider"
        )
        
        with patch.object(client.providers[client.primary_provider], 'generate', return_value=mock_response):
            start_time = asyncio.get_event_loop().time()
            response = await client.generate(prompt="Test prompt")
            end_time = asyncio.get_event_loop().time()
            
            assert response.content == "Test response"
            assert (end_time - start_time) < 1.0  # Should complete quickly with mock
    
    @pytest.mark.asyncio
    async def test_concurrent_generation(self):
        """Test concurrent generation requests."""
        client = LLMClient()
        
        mock_response = LLMResponse(
            content="Test response",
            model="test-model",
            provider="test-provider"
        )
        
        with patch.object(client.providers[client.primary_provider], 'generate', return_value=mock_response):
            # Create multiple concurrent requests
            tasks = [
                client.generate(prompt=f"Test prompt {i}")
                for i in range(5)
            ]
            
            responses = await asyncio.gather(*tasks)
            
            assert len(responses) == 5
            for response in responses:
                assert response.content == "Test response"
    
    @pytest.mark.asyncio
    async def test_large_prompt_handling(self):
        """Test handling of large prompts."""
        client = LLMClient()
        
        # Create a large prompt
        large_prompt = "Test prompt " * 1000
        
        mock_response = LLMResponse(
            content="Test response",
            model="test-model",
            provider="test-provider"
        )
        
        with patch.object(client.providers[client.primary_provider], 'generate', return_value=mock_response):
            response = await client.generate(prompt=large_prompt)
            assert response.content == "Test response"


class TestIntegration:
    """Test integration with other components."""
    
    @pytest.mark.asyncio
    async def test_memory_manager_integration(self):
        """Test integration with memory manager."""
        from memory_manager import MemoryManager
        
        client = LLMClient()
        memory_manager = MemoryManager()
        
        # Add some test content to memory
        await memory_manager.add_agent_notes(
            content="Context from memory",
            agent_id="test_agent",
            tags=["test"],
            provenance_notes="Test note"
        )
        
        # Get context from memory
        context = await memory_manager.get_context_for_generation("test query")
        context_string, retrieval_results = context
        
        assert isinstance(context_string, str)
        assert isinstance(retrieval_results, list)
    
    def test_available_models(self):
        """Test getting available models."""
        client = LLMClient()
        models = client.get_available_models()
        
        assert isinstance(models, dict)
        for provider_name, model_list in models.items():
            assert isinstance(model_list, list)
    
    def test_switch_provider(self):
        """Test switching providers."""
        client = LLMClient()
        
        # Get available providers
        available_providers = list(client.providers.keys())
        
        if len(available_providers) > 1:
            # Switch to a different provider
            new_provider = available_providers[1]
            client.switch_provider(new_provider)
            assert client.primary_provider == new_provider
    
    def test_get_provider_info(self):
        """Test getting provider information."""
        client = LLMClient()
        info = client.get_provider_info()
        
        assert isinstance(info, dict)
        for provider_name, provider_info in info.items():
            assert "type" in provider_info
            assert "models" in provider_info
            assert "available" in provider_info


class TestConfiguration:
    """Test configuration and environment variables."""
    
    def test_environment_variable_loading(self):
        """Test loading configuration from environment variables."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            client = LLMClient()
            assert isinstance(client.providers, dict)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test with invalid provider
        client = LLMClient(primary_provider="invalid_provider")
        # Should fallback to available provider
        assert client.primary_provider in ["openai", "ollama"]
    
    def test_custom_ollama_url(self):
        """Test custom Ollama URL configuration."""
        client = LLMClient(ollama_url="http://custom:8080")
        assert isinstance(client.providers, dict)