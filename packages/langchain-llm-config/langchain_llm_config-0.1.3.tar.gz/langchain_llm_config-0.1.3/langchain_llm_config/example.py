"""
Example usage of langchain-llm-config package
"""

import asyncio
import os
import warnings
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from .config import init_config, load_config
from .factory import create_assistant, create_embedding_provider


class ChatResponse(BaseModel):
    """Example response model for chat assistant"""

    message: str = Field(..., description="The assistant's response message")
    confidence: float = Field(
        ..., description="Confidence score of the response", ge=0.0, le=1.0
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )


def setup_environment() -> bool:
    """
    Set up the environment for the example.
    This function demonstrates how to handle missing environment variables gracefully.
    """
    print("🔧 Setting up environment...")

    # Check if configuration file exists
    config_path = Path.cwd() / "api.yaml"
    if not config_path.exists():
        print("📝 Creating configuration file...")
        init_config(str(config_path))
        print("✅ Configuration file created. Please edit api.yaml with your settings.")
        return False

    # Try to load configuration
    try:
        print("📖 Loading configuration...")
        load_config(str(config_path), strict=False)
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False


def example_chat_assistant_sync() -> None:
    """
    Example of creating and using a chat assistant (synchronous)
    """
    print("\n🤖 Chat Assistant Example (Synchronous)")
    print("=" * 50)

    try:
        # Create assistant with response model
        assistant = create_assistant(
            response_model=ChatResponse,
            provider="openai",  # or "gemini", "vllm"
            system_prompt=(
                "You are a helpful AI assistant. "
                "Provide clear and concise responses."
            ),
        )

        # Example conversation
        user_message = "What is the capital of France?"

        print(f"👤 User: {user_message}")

        # Get response (synchronous)
        response = assistant.ask(user_message)

        print(f"🤖 Assistant: {response['message']}")
        print(f"📊 Confidence: {response['confidence']:.2f}")
        if response["suggestions"]:
            print(f"💡 Suggestions: {', '.join(response['suggestions'])}")

    except Exception as e:
        print(f"❌ Error with chat assistant: {e}")
        print(
            "💡 Make sure your API keys are set in environment variables or .env file"
        )


async def example_chat_assistant_async() -> None:
    """
    Example of creating and using a chat assistant (asynchronous)
    """
    print("\n🤖 Chat Assistant Example (Asynchronous)")
    print("=" * 50)

    try:
        # Create assistant with response model
        assistant = create_assistant(
            response_model=ChatResponse,
            provider="openai",  # or "gemini", "vllm"
            system_prompt=(
                "You are a helpful AI assistant. "
                "Provide clear and concise responses."
            ),
        )

        # Example conversation
        user_message = "What is the capital of Japan?"

        print(f"👤 User: {user_message}")

        # Get response (asynchronous)
        response = await assistant.ask_async(user_message)

        print(f"🤖 Assistant: {response['message']}")
        print(f"📊 Confidence: {response['confidence']:.2f}")
        if response["suggestions"]:
            print(f"💡 Suggestions: {', '.join(response['suggestions'])}")

    except Exception as e:
        print(f"❌ Error with chat assistant: {e}")
        print(
            "💡 Make sure your API keys are set in environment variables or .env file"
        )


def example_embedding_provider_sync() -> None:
    """
    Example of creating and using an embedding provider (synchronous)
    """
    print("\n🔗 Embedding Provider Example (Synchronous)")
    print("=" * 50)

    try:
        # Create embedding provider
        provider = create_embedding_provider(provider="openai")  # or "infinity", "vllm"

        # Example texts to embed
        texts = [
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning is a subset of artificial intelligence.",
            "Python is a popular programming language.",
        ]

        print(f"📝 Embedding {len(texts)} texts...")

        # Get embeddings (synchronous)
        embeddings = provider.embed_texts(texts)

        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"📊 Each embedding has {len(embeddings[0])} dimensions")

        # Example similarity calculation
        if len(embeddings) >= 2:
            from numpy import dot
            from numpy.linalg import norm

            # Calculate cosine similarity between first two embeddings
            similarity = dot(embeddings[0], embeddings[1]) / (
                norm(embeddings[0]) * norm(embeddings[1])
            )
            print(f"🔍 Similarity between texts 1 and 2: {similarity:.3f}")

    except Exception as e:
        print(f"❌ Error with embedding provider: {e}")
        print(
            "💡 Make sure your API keys are set in environment variables or .env file"
        )


async def example_embedding_provider_async() -> None:
    """
    Example of creating and using an embedding provider (asynchronous)
    """
    print("\n🔗 Embedding Provider Example (Asynchronous)")
    print("=" * 50)

    try:
        # Create embedding provider
        provider = create_embedding_provider(provider="openai")  # or "infinity", "vllm"

        # Example texts to embed
        texts = [
            "Artificial intelligence is transforming the world.",
            "Deep learning models are becoming more sophisticated.",
            "Natural language processing is advancing rapidly.",
        ]

        print(f"📝 Embedding {len(texts)} texts...")

        # Get embeddings (asynchronous)
        embeddings = await provider.embed_texts_async(texts)

        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"📊 Each embedding has {len(embeddings[0])} dimensions")

        # Example similarity calculation
        if len(embeddings) >= 2:
            from numpy import dot
            from numpy.linalg import norm

            # Calculate cosine similarity between first two embeddings
            similarity = dot(embeddings[0], embeddings[1]) / (
                norm(embeddings[0]) * norm(embeddings[1])
            )
            print(f"🔍 Similarity between texts 1 and 2: {similarity:.3f}")

    except Exception as e:
        print(f"❌ Error with embedding provider: {e}")
        print(
            "💡 Make sure your API keys are set in environment variables or .env file"
        )


def main() -> None:
    """
    Main example function (synchronous)
    """
    print("🚀 Langchain LLM Config Example")
    print("=" * 50)

    # Set up environment
    if not setup_environment():
        print("\n📋 To get started:")
        print("1. Run: llm-config init")
        print("2. Run: llm-config setup-env")
        print("3. Edit .env file with your API keys")
        print("4. Run this example again")
        return

    # Run synchronous examples
    example_chat_assistant_sync()
    example_embedding_provider_sync()

    print("\n✅ Synchronous examples completed!")

    tips_message = (
        "\n💡 Tips:\n"
        "• Use .env file for API keys (never commit to version control)\n"
        "• Set strict=False in load_config() for development\n"
        "• Use strict=True in production to catch missing environment variables\n"
        "• Use ask() for synchronous calls, ask_async() for asynchronous calls\n"
        "• Use embed_texts() for synchronous calls, embed_texts_async() "
        "for asynchronous calls"
    )

    print(tips_message)


async def main_async() -> None:
    """
    Main example function (asynchronous)
    """
    print("🚀 Langchain LLM Config Example (Async)")
    print("=" * 50)

    # Set up environment
    if not setup_environment():
        print("\n📋 To get started:")
        print("1. Run: llm-config init")
        print("2. Run: llm-config setup-env")
        print("3. Edit .env file with your API keys")
        print("4. Run this example again")
        return

    # Run asynchronous examples
    await example_chat_assistant_async()
    await example_embedding_provider_async()

    print("\n✅ Asynchronous examples completed!")

    tips_message = (
        "\n💡 Tips:\n"
        "• Use .env file for API keys (never commit to version control)\n"
        "• Set strict=False in load_config() for development\n"
        "• Use strict=True in production to catch missing environment variables\n"
        "• Use ask() for synchronous calls, ask_async() for asynchronous calls\n"
        "• Use embed_texts() for synchronous calls, embed_texts_async() "
        "for asynchronous calls"
    )

    print(tips_message)


if __name__ == "__main__":
    # Run synchronous examples by default
    main()

    # Uncomment the following lines to run asynchronous examples
    # asyncio.run(main_async())
