"""
Langchain LLM Config - A comprehensive LLM configuration package

This package provides a unified interface for working with multiple LLM providers
including OpenAI, VLLM, Gemini, and Infinity for both chat assistants and embeddings.
"""

import os
from pathlib import Path

__version__ = "0.1.0"
__author__ = "Xingbang Liu"
__email__ = "xingbangliu48@gmail.com"

# Define the tiktoken cache directory path
TIKTOKEN_CACHE_DIR = str(Path(__file__).parent / ".tiktoken_cache")

# Import main factory functions
from .factory import (
    create_assistant,
    create_chat_streaming,
    create_embedding_provider,
)

# Import configuration functions
from .config import (
    load_config,
    init_config,
    get_default_config_path,
)

# Import base classes for extensibility
from .assistant.base import Assistant
from .assistant.chat_streaming import ChatStreaming
from .embeddings.base import BaseEmbeddingProvider

# Import provider classes
from .assistant.providers.vllm import VLLMAssistant
from .assistant.providers.gemini import GeminiAssistant
from .embeddings.providers.openai import OpenAIEmbeddingProvider
from .embeddings.providers.vllm import VLLMEmbeddingProvider
from .embeddings.providers.infinity import InfinityEmbeddingProvider

__all__ = [
    # Constants
    "TIKTOKEN_CACHE_DIR",
    # Factory functions
    "create_assistant",
    "create_chat_streaming",
    "create_embedding_provider",
    # Configuration functions
    "load_config",
    "init_config",
    "get_default_config_path",
    # Base classes
    "Assistant",
    "ChatStreaming",
    "BaseEmbeddingProvider",
    # Provider classes
    "VLLMAssistant",
    "GeminiAssistant",
    "OpenAIEmbeddingProvider",
    "VLLMEmbeddingProvider",
    "InfinityEmbeddingProvider",
]
