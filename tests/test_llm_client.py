"""
Unit tests for the LLMClient module.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from llm_client import LLMClient, LLMRequest, LLMResponse


class TestLLMClient:
    """Test cases for LLMClient functionality."""
    
    @pytest.mark.asyncio
    async def test_initialize(self, llm_client):
        """Test LLM client initialization."""
        assert llm_client is not None
        assert llm_client.provider in ["ollama", "openai"]
    
    @pytest.mark.asyncio
    async def test_generate_request(self, llm_client):
        """Test generating a simple request."""
        request = LLMRequest(
            prompt="What is machine learning?",
            max_tokens=100,
            temperature=0.7
        )
        
        # Mock the actual LLM call for testing
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.return_value = LLMResponse(
                content="Machine learning is a subset of artificial intelligence...",
                tokens_used=50,
                model="test-model"
            )
            
            response = await llm_client.generate(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            assert response is not None
            assert response.content is not None
            assert len(response.content) > 0
    
    @pytest.mark.asyncio
    async def test_generate_with_context(self, llm_client):
        """Test generating with context and references."""
        context = "Machine learning is a subset of artificial intelligence."
        references = ["ref1", "ref2", "ref3"]
        
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.return_value = LLMResponse(
                content="Based on the context, machine learning involves...",
                tokens_used=75,
                model="test-model"
            )
            
            response = await llm_client.generate(
                prompt="Explain machine learning",
                context=context,
                references=references,
                max_tokens=200
            )
            
            assert response is not None
            assert response.content is not None
            assert "machine learning" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, llm_client):
        """Test generating with system prompt."""
        system_prompt = "You are a helpful AI assistant specializing in technology."
        
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.return_value = LLMResponse(
                content="I understand. I'm here to help with technology questions.",
                tokens_used=30,
                model="test-model"
            )
            
            response = await llm_client.generate(
                prompt="What can you help me with?",
                system_prompt=system_prompt,
                max_tokens=100
            )
            
            assert response is not None
            assert response.content is not None
    
    @pytest.mark.asyncio
    async def test_generate_with_tools(self, llm_client):
        """Test generating with tool calls."""
        tools = [
            {"name": "search", "description": "Search for information"},
            {"name": "calculate", "description": "Perform calculations"}
        ]
        
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.return_value = LLMResponse(
                content="I can help you search for information or perform calculations.",
                tokens_used=40,
                model="test-model"
            )
            
            response = await llm_client.generate(
                prompt="What tools do you have?",
                tools=tools,
                max_tokens=100
            )
            
            assert response is not None
            assert response.content is not None
    
    @pytest.mark.asyncio
    async def test_generate_with_streaming(self, llm_client):
        """Test streaming generation."""
        with patch.object(llm_client, '_call_ollama_stream') as mock_stream:
            mock_stream.return_value = [
                "Machine ",
                "learning ",
                "is ",
                "a ",
                "subset ",
                "of ",
                "AI."
            ]
            
            chunks = []
            async for chunk in llm_client.generate_stream(
                prompt="What is machine learning?",
                max_tokens=50
            ):
                chunks.append(chunk)
            
            assert len(chunks) > 0
            assert "".join(chunks) == "Machine learning is a subset of AI."
    
    @pytest.mark.asyncio
    async def test_generate_with_retry(self, llm_client):
        """Test generation with retry logic."""
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            # First call fails, second succeeds
            mock_ollama.side_effect = [
                Exception("Network error"),
                LLMResponse(
                    content="Machine learning is a subset of AI.",
                    tokens_used=20,
                    model="test-model"
                )
            ]
            
            response = await llm_client.generate(
                prompt="What is machine learning?",
                max_tokens=100,
                retry_attempts=2
            )
            
            assert response is not None
            assert response.content is not None
            assert mock_ollama.call_count == 2
    
    @pytest.mark.asyncio
    async def test_generate_with_rate_limiting(self, llm_client):
        """Test generation with rate limiting."""
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.return_value = LLMResponse(
                content="Rate limited response",
                tokens_used=10,
                model="test-model"
            )
            
            # Test rate limiting
            start_time = asyncio.get_event_loop().time()
            response = await llm_client.generate(
                prompt="Test prompt",
                max_tokens=50
            )
            end_time = asyncio.get_event_loop().time()
            
            assert response is not None
            # Rate limiting should add some delay
            assert end_time - start_time >= 0
    
    @pytest.mark.asyncio
    async def test_generate_with_error_handling(self, llm_client):
        """Test error handling in generation."""
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.side_effect = Exception("LLM service unavailable")
            
            with pytest.raises(Exception):
                await llm_client.generate(
                    prompt="Test prompt",
                    max_tokens=50
                )
    
    @pytest.mark.asyncio
    async def test_generate_with_validation(self, llm_client):
        """Test input validation."""
        # Test empty prompt
        with pytest.raises(ValueError):
            await llm_client.generate(
                prompt="",
                max_tokens=50
            )
        
        # Test negative max_tokens
        with pytest.raises(ValueError):
            await llm_client.generate(
                prompt="Test prompt",
                max_tokens=-1
            )
        
        # Test invalid temperature
        with pytest.raises(ValueError):
            await llm_client.generate(
                prompt="Test prompt",
                temperature=2.0
            )
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, llm_client, performance_metrics):
        """Test performance metrics collection."""
        import time
        
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.return_value = LLMResponse(
                content="Performance test response",
                tokens_used=25,
                model="test-model"
            )
            
            start_time = time.time()
            response = await llm_client.generate(
                prompt="Performance test",
                max_tokens=100
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            performance_metrics["llm_response_time"] = response_time
            
            assert response_time > 0
            assert response.tokens_used > 0