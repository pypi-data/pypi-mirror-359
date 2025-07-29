import os
from typing import Any, Dict, Optional, Type

from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr

from ..base import Assistant


class GeminiAssistant(Assistant):
    """Gemini model assistant implementation."""

    def __init__(
        self,
        config: Dict[str, Any],
        response_model: Type[BaseModel],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        初始化VLLM助手

        Args:
            config: 配置字典
            response_model: 响应模型类
            system_prompt: 系统提示
            **kwargs: 额外参数
        """
        # 保存config作为实例变量，但不传递给父类
        self.config = config

        # 设置系统提示和响应模型
        self.system_prompt = system_prompt
        self.response_model = response_model

        # 从config中提取参数
        model_name = config["model_name"]
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 2000)
        api_key = config.get("api_key")
        top_p = config.get("top_p", 1.0)
        connect_timeout = config.get("connect_timeout", 30)
        model_kwargs = config.get("model_kwargs", {})

        # Ensure model_kwargs is a dictionary
        if model_kwargs is None:
            model_kwargs = {}

        # Add model-specific parameters to model_kwargs
        if max_tokens is not None:
            model_kwargs["max_output_tokens"] = max_tokens
        if top_p is not None:
            model_kwargs["top_p"] = top_p

        # 初始化Gemini LLM with only top-level accepted parameters
        self.llm: Any = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=SecretStr(
                api_key or os.getenv("GEMINI_API_KEY", "dummy-key") or ""
            ),
            timeout=float(connect_timeout) if connect_timeout else None,
            **model_kwargs,
        )

        # 设置解析器
        self.parser = PydanticOutputParser(pydantic_object=response_model)

        # 设置提示模板和处理链
        self._setup_prompt_and_chain()
