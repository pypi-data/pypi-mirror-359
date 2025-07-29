"""
Chat Streaming Assistant for real-time streaming responses
"""

import os
import time
from typing import Any, AsyncGenerator, Dict, Optional, Union

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


class ChatStreaming:
    """Pure streaming chat assistant without response model constraints"""

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        top_p: float = 1.0,
        connect_timeout: Optional[int] = None,
        read_timeout: Optional[int] = None,
        model_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the Chat Streaming Assistant"""
        self.model_name = model_name
        self.system_prompt = system_prompt or ""

        # Ensure model_kwargs is a dictionary
        if model_kwargs is None:
            model_kwargs = {}

        # Add model-specific parameters to model_kwargs
        if max_tokens is not None:
            model_kwargs["max_tokens"] = max_tokens
        if top_p is not None:
            model_kwargs["top_p"] = top_p

        # Initialize LLM with only top-level accepted parameters
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            base_url=base_url,
            api_key=SecretStr(
                api_key or os.getenv("OPENAI_API_KEY", "dummy-key") or ""
            ),
            model_kwargs=model_kwargs,
            timeout=(connect_timeout, read_timeout),
        )

        self._setup_prompt()

    def _setup_prompt(self) -> None:
        """Set up prompt template for chat"""
        template = "{system_prompt}\n\n{context}\n用户: {question}\n助手:"

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["question", "system_prompt", "context"],
        )

    async def chat(
        self,
        query: str,
        extra_system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Process user query and return complete response"""
        start_time = time.time()

        try:
            # Build system prompt
            system_prompt = self.system_prompt or ""
            if extra_system_prompt:
                system_prompt = (
                    f"{system_prompt}\n{extra_system_prompt}"
                    if system_prompt
                    else extra_system_prompt
                )

            # Build context
            context_str = f"背景信息：{context}" if context else ""

            # Get response from LLM
            response = await self.llm.ainvoke(
                self.prompt.format(
                    question=query,
                    system_prompt=system_prompt,
                    context=context_str,
                )
            )

            processing_time = time.time() - start_time

            return {
                "content": response.content,
                "processing_time": processing_time,
                "model_used": self.model_name,
            }

        except Exception as e:
            raise ValueError(f"处理查询时出错: {str(e)}") from e

    async def chat_stream(
        self,
        query: str,
        extra_system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chat response in real-time

        This method streams the LLM response token by token without any
        response model constraints or structured output requirements
        """
        start_time = time.time()

        try:
            # Build system prompt
            system_prompt = self.system_prompt or ""
            if extra_system_prompt:
                system_prompt = (
                    f"{system_prompt}\n{extra_system_prompt}"
                    if system_prompt
                    else extra_system_prompt
                )

            # Build context
            context_str = f"背景信息：{context}" if context else ""

            # Initialize streaming state
            full_response = ""

            # Stream directly from LLM
            async for chunk in self.llm.astream(
                self.prompt.format(
                    question=query,
                    system_prompt=system_prompt,
                    context=context_str,
                )
            ):
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    # Ensure content is a string
                    if isinstance(content, list):
                        content = "".join(str(item) for item in content)

                    full_response += content

                    # Yield token-level streaming
                    yield {
                        "type": "stream",
                        "content": content,
                        "full_response": full_response,
                        "processing_time": time.time() - start_time,
                        "model_used": self.model_name,
                        "is_complete": False,
                    }

            # Yield final result
            processing_time = time.time() - start_time
            yield {
                "type": "final",
                "content": full_response,
                "processing_time": processing_time,
                "model_used": self.model_name,
                "is_complete": True,
            }

        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "processing_time": time.time() - start_time,
                "is_complete": True,
            }

    async def stream_async(
        self,
        query: str,
        extra_system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response as simple text chunks

        This is a simplified version that yields just the text content
        """
        async for chunk in self.chat_stream(
            query, extra_system_prompt, context, **kwargs
        ):
            if chunk["type"] == "stream":
                yield chunk["content"]
            elif chunk["type"] == "error":
                raise ValueError(chunk["error"])
