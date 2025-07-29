"""
Tests for example module
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
from io import StringIO

from langchain_llm_config.example import (
    setup_environment,
    example_chat_assistant_sync,
    example_chat_assistant_async,
    example_embedding_provider_sync,
    example_embedding_provider_async,
    main,
    main_async
)


class TestExample:
    """Test example functions"""

    def test_setup_environment_config_exists(self, tmp_path):
        """Test setup_environment when config file exists"""
        # Create a test config file
        config_path = tmp_path / "api.yaml"
        with open(config_path, "w") as f:
            f.write("test config content")
        
        with patch("pathlib.Path.cwd") as mock_cwd, \
             patch("langchain_llm_config.example.load_config") as mock_load:
            
            mock_cwd.return_value = tmp_path
            mock_load.return_value = {"default": {"chat_provider": "openai"}}
            
            # Capture stdout
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                result = setup_environment()
            
            assert result is True
            assert "📖 Loading configuration..." in mock_stdout.getvalue()
            assert "✅ Configuration loaded successfully" in mock_stdout.getvalue()

    def test_setup_environment_config_not_exists(self, tmp_path):
        """Test setup_environment when config file doesn't exist"""
        with patch("pathlib.Path.cwd") as mock_cwd, \
             patch("langchain_llm_config.example.init_config") as mock_init:
            
            mock_cwd.return_value = tmp_path
            mock_init.return_value = tmp_path / "api.yaml"
            
            # Capture stdout
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                result = setup_environment()
            
            assert result is False
            assert "📝 Creating configuration file..." in mock_stdout.getvalue()
            assert "✅ Configuration file created" in mock_stdout.getvalue()
            mock_init.assert_called_once()

    def test_setup_environment_load_error(self, tmp_path):
        """Test setup_environment when loading config fails"""
        # Create a test config file
        config_path = tmp_path / "api.yaml"
        with open(config_path, "w") as f:
            f.write("test config content")
        
        with patch("pathlib.Path.cwd") as mock_cwd, \
             patch("langchain_llm_config.example.load_config") as mock_load:
            
            mock_cwd.return_value = tmp_path
            mock_load.side_effect = Exception("Config error")
            
            # Capture stdout
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                result = setup_environment()
            
            assert result is False
            assert "❌ Error loading configuration:" in mock_stdout.getvalue()
            assert "Config error" in mock_stdout.getvalue()

    @patch("langchain_llm_config.example.create_assistant")
    def test_example_chat_assistant_sync_success(self, mock_create_assistant):
        """Test successful example_chat_assistant_sync"""
        # Mock assistant
        mock_assistant = MagicMock()
        mock_assistant.ask.return_value = {
            "message": "Paris is the capital of France.",
            "confidence": 0.95,
            "suggestions": ["What about other French cities?", "Tell me about French history"]
        }
        mock_create_assistant.return_value = mock_assistant
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            example_chat_assistant_sync()
        
        output = mock_stdout.getvalue()
        assert "🤖 Chat Assistant Example (Synchronous)" in output
        assert "👤 User: What is the capital of France?" in output
        assert "🤖 Assistant: Paris is the capital of France." in output
        assert "📊 Confidence: 0.95" in output
        # Check that suggestions are mentioned (the exact format may vary)
        assert "suggestions" in output.lower() or "💡" in output

    @patch("langchain_llm_config.example.create_assistant")
    def test_example_chat_assistant_sync_error(self, mock_create_assistant):
        """Test example_chat_assistant_sync with error"""
        mock_create_assistant.side_effect = Exception("API key error")
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            example_chat_assistant_sync()
        
        output = mock_stdout.getvalue()
        assert "🤖 Chat Assistant Example (Synchronous)" in output
        assert "❌ Error with chat assistant:" in output
        assert "API key error" in output
        assert "💡 Make sure your API keys are set" in output

    @patch("langchain_llm_config.example.create_assistant")
    @pytest.mark.asyncio
    async def test_example_chat_assistant_async_success(self, mock_create_assistant):
        """Test successful example_chat_assistant_async"""
        # Mock assistant
        mock_assistant = MagicMock()
        mock_assistant.ask_async = AsyncMock(return_value={
            "message": "Tokyo is the capital of Japan.",
            "confidence": 0.98,
            "suggestions": ["What about Japanese culture?", "Tell me about Japan's geography"]
        })
        mock_create_assistant.return_value = mock_assistant
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            await example_chat_assistant_async()
        
        output = mock_stdout.getvalue()
        assert "🤖 Chat Assistant Example (Asynchronous)" in output
        assert "👤 User: What is the capital of Japan?" in output
        assert "🤖 Assistant: Tokyo is the capital of Japan." in output
        assert "📊 Confidence: 0.98" in output
        # Check that suggestions are mentioned (the exact format may vary)
        assert "suggestions" in output.lower() or "💡" in output

    @patch("langchain_llm_config.example.create_assistant")
    @pytest.mark.asyncio
    async def test_example_chat_assistant_async_error(self, mock_create_assistant):
        """Test example_chat_assistant_async with error"""
        mock_create_assistant.side_effect = Exception("API key error")
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            await example_chat_assistant_async()
        
        output = mock_stdout.getvalue()
        assert "🤖 Chat Assistant Example (Asynchronous)" in output
        assert "❌ Error with chat assistant:" in output
        assert "API key error" in output
        assert "💡 Make sure your API keys are set" in output

    @patch("langchain_llm_config.example.create_embedding_provider")
    @patch("numpy.dot")
    @patch("numpy.linalg.norm")
    def test_example_embedding_provider_sync_success(self, mock_norm, mock_dot, mock_create_provider):
        """Test successful example_embedding_provider_sync"""
        # Mock embedding provider
        mock_provider = MagicMock()
        mock_provider.embed_texts.return_value = [
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.9, 1.0, 1.1, 1.2]
        ]
        mock_create_provider.return_value = mock_provider
        
        # Mock numpy functions
        mock_dot.return_value = 0.5
        mock_norm.side_effect = [1.0, 1.0]
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            example_embedding_provider_sync()
        
        output = mock_stdout.getvalue()
        assert "🔗 Embedding Provider Example (Synchronous)" in output
        assert "📝 Embedding 3 texts..." in output
        assert "✅ Generated 3 embeddings" in output
        assert "📊 Each embedding has 4 dimensions" in output
        assert "🔍 Similarity between texts 1 and 2: 0.500" in output

    @patch("langchain_llm_config.example.create_embedding_provider")
    def test_example_embedding_provider_sync_error(self, mock_create_provider):
        """Test example_embedding_provider_sync with error"""
        mock_create_provider.side_effect = Exception("API key error")
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            example_embedding_provider_sync()
        
        output = mock_stdout.getvalue()
        assert "🔗 Embedding Provider Example (Synchronous)" in output
        assert "❌ Error with embedding provider:" in output
        assert "API key error" in output
        assert "💡 Make sure your API keys are set" in output

    @patch("langchain_llm_config.example.create_embedding_provider")
    @patch("numpy.dot")
    @patch("numpy.linalg.norm")
    @pytest.mark.asyncio
    async def test_example_embedding_provider_async_success(self, mock_norm, mock_dot, mock_create_provider):
        """Test successful example_embedding_provider_async"""
        # Mock embedding provider
        mock_provider = MagicMock()
        mock_provider.embed_texts_async = AsyncMock(return_value=[
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.9, 1.0, 1.1, 1.2]
        ])
        mock_create_provider.return_value = mock_provider
        
        # Mock numpy functions
        mock_dot.return_value = 0.7
        mock_norm.side_effect = [1.0, 1.0]
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            await example_embedding_provider_async()
        
        output = mock_stdout.getvalue()
        assert "🔗 Embedding Provider Example (Asynchronous)" in output
        assert "📝 Embedding 3 texts..." in output
        assert "✅ Generated 3 embeddings" in output
        assert "📊 Each embedding has 4 dimensions" in output
        assert "🔍 Similarity between texts 1 and 2: 0.700" in output

    @patch("langchain_llm_config.example.create_embedding_provider")
    @pytest.mark.asyncio
    async def test_example_embedding_provider_async_error(self, mock_create_provider):
        """Test example_embedding_provider_async with error"""
        mock_create_provider.side_effect = Exception("API key error")
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            await example_embedding_provider_async()
        
        output = mock_stdout.getvalue()
        assert "🔗 Embedding Provider Example (Asynchronous)" in output
        assert "❌ Error with embedding provider:" in output
        assert "API key error" in output
        assert "💡 Make sure your API keys are set" in output

    @patch("langchain_llm_config.example.setup_environment")
    @patch("langchain_llm_config.example.example_chat_assistant_sync")
    @patch("langchain_llm_config.example.example_embedding_provider_sync")
    def test_main_success(self, mock_embedding, mock_chat, mock_setup):
        """Test successful main function"""
        mock_setup.return_value = True
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            main()
        
        output = mock_stdout.getvalue()
        assert "🚀 Langchain LLM Config Example" in output
        assert "✅ Synchronous examples completed!" in output
        assert "💡 Tips:" in output
        
        # Verify functions were called
        mock_setup.assert_called_once()
        mock_chat.assert_called_once()
        mock_embedding.assert_called_once()

    @patch("langchain_llm_config.example.setup_environment")
    def test_main_setup_failed(self, mock_setup):
        """Test main function when setup fails"""
        mock_setup.return_value = False
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            main()
        
        output = mock_stdout.getvalue()
        assert "🚀 Langchain LLM Config Example" in output
        assert "📋 To get started:" in output
        assert "1. Run: llm-config init" in output
        assert "2. Run: llm-config setup-env" in output
        assert "3. Edit .env file with your API keys" in output
        assert "4. Run this example again" in output

    @patch("langchain_llm_config.example.setup_environment")
    @patch("langchain_llm_config.example.example_chat_assistant_async")
    @patch("langchain_llm_config.example.example_embedding_provider_async")
    @pytest.mark.asyncio
    async def test_main_async_success(self, mock_embedding, mock_chat, mock_setup):
        """Test successful main_async function"""
        mock_setup.return_value = True
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            await main_async()
        
        output = mock_stdout.getvalue()
        assert "🚀 Langchain LLM Config Example (Async)" in output
        assert "✅ Asynchronous examples completed!" in output
        assert "💡 Tips:" in output
        
        # Verify functions were called
        mock_setup.assert_called_once()
        mock_chat.assert_called_once()
        mock_embedding.assert_called_once()

    @patch("langchain_llm_config.example.setup_environment")
    @pytest.mark.asyncio
    async def test_main_async_setup_failed(self, mock_setup):
        """Test main_async function when setup fails"""
        mock_setup.return_value = False
        
        # Capture stdout
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            await main_async()
        
        output = mock_stdout.getvalue()
        assert "🚀 Langchain LLM Config Example (Async)" in output
        assert "📋 To get started:" in output
        assert "1. Run: llm-config init" in output
        assert "2. Run: llm-config setup-env" in output
        assert "3. Edit .env file with your API keys" in output
        assert "4. Run this example again" in output

    def test_example_embedding_provider_sync_insufficient_embeddings(self, tmp_path):
        """Test example_embedding_provider_sync with insufficient embeddings for similarity calculation"""
        with patch("langchain_llm_config.example.create_embedding_provider") as mock_create_provider:
            # Mock embedding provider with only one embedding
            mock_provider = MagicMock()
            mock_provider.embed_texts.return_value = [[0.1, 0.2, 0.3]]
            mock_create_provider.return_value = mock_provider
            
            # Capture stdout
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                example_embedding_provider_sync()
            
            output = mock_stdout.getvalue()
            assert "🔗 Embedding Provider Example (Synchronous)" in output
            assert "📝 Embedding 3 texts..." in output
            assert "✅ Generated 1 embeddings" in output
            assert "📊 Each embedding has 3 dimensions" in output
            # Should not have similarity calculation
            assert "🔍 Similarity between texts 1 and 2:" not in output

    @pytest.mark.asyncio
    async def test_example_embedding_provider_async_insufficient_embeddings(self, tmp_path):
        """Test example_embedding_provider_async with insufficient embeddings for similarity calculation"""
        with patch("langchain_llm_config.example.create_embedding_provider") as mock_create_provider:
            # Mock embedding provider with only one embedding
            mock_provider = MagicMock()
            mock_provider.embed_texts_async = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
            mock_create_provider.return_value = mock_provider
            
            # Capture stdout
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                await example_embedding_provider_async()
            
            output = mock_stdout.getvalue()
            assert "🔗 Embedding Provider Example (Asynchronous)" in output
            assert "📝 Embedding 3 texts..." in output
            assert "✅ Generated 1 embeddings" in output
            assert "📊 Each embedding has 3 dimensions" in output
            # Should not have similarity calculation
            assert "🔍 Similarity between texts 1 and 2:" not in output 