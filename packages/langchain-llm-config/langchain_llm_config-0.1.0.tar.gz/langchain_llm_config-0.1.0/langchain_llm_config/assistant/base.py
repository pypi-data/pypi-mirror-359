from typing import Type, Optional, Dict, Any
from pydantic import BaseModel
import os

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


class Assistant:
    """
    AI助手基类，处理结构化问答

    Attributes:
        system_prompt: 系统提示
        response_model: 响应模型类型
        llm: 语言模型实例
        parser: 输出解析器
        prompt: 提示模板
        chain: 处理链
    """

    def __init__(
        self,
        model_name: str,
        response_model: Type[BaseModel],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        top_p: float = 1.0,
        connect_timeout: Optional[int] = None,
        read_timeout: Optional[int] = None,
        model_kwargs: Optional[Dict] = None,
    ):
        """
        初始化AI助手

        Args:
            model_name: 使用的模型名称
            response_model: 响应模型类型
            temperature: 采样温度
            max_tokens: 最大生成token数
            base_url: API基础URL
            api_key: API密钥
            system_prompt: 系统提示
            top_p: 采样参数
            connect_timeout: 连接超时时间
            read_timeout: 读取超时时间
            model_kwargs: 额外的模型参数
        """
        self.system_prompt = system_prompt
        self.response_model = response_model

        # 初始化LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url,
            top_p=top_p,
            api_key=api_key or os.getenv("OPENAI_API_KEY", "dummy-key"),
            model_kwargs=model_kwargs or {},
            timeout=(connect_timeout, read_timeout),
        )

        # 设置解析器
        self._setup_prompt_and_chain()

    def _setup_prompt_and_chain(self):
        """设置提示模板和处理链"""
        # 创建基础解析器
        base_parser = PydanticOutputParser(pydantic_object=self.response_model)

        # 获取格式说明
        format_instructions = base_parser.get_format_instructions()
        escaped_format_instructions = format_instructions.replace("{", "{{").replace(
            "}", "}}"
        )

        # 创建带重试的解析器
        self.parser = base_parser.with_retry(
            stop_after_attempt=3,
            retry_if_exception_type=(ValueError, KeyError),
        )

        # 创建提示模板
        self.prompt = PromptTemplate(
            template=(
                "{system_prompt}\n"
                "请严格按照以下格式提供您的回答。您的回答必须：\n"
                "1. 完全符合指定的JSON格式\n"
                "2. 不要添加任何额外的解释或注释\n"
                "3. 对于有默认值的字段（如intension、language），如果不知道具体值，请直接省略该字段，不要使用null\n"
                "4. 对于没有默认值的可选字段，如果确实没有值，才使用null\n"
                "5. 必须使用标准ASCII字符作为JSON语法（如 : 而不是 ：）\n"
                "格式要求：\n"
                "{format_instructions}\n\n"
                "{context}\n"
                "用户: {question}\n"
                "助手:"
            ),
            input_variables=["question", "system_prompt", "context"],
            partial_variables={"format_instructions": escaped_format_instructions},
        )

        # 构建链
        self.chain = RunnablePassthrough() | self.prompt | self.llm | self.parser

    def ask(
        self,
        query: str,
        extra_system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        处理用户查询并返回结构化响应（同步版本）

        Args:
            query: 用户查询文本
            extra_system_prompt: 额外的系统提示
            context: 可选的上下文信息
            **kwargs: 额外参数

        Returns:
            解析并验证后的结构化响应

        Raises:
            ValueError: 当处理查询时发生错误
        """
        try:
            # 构建系统提示
            system_prompt = self.system_prompt or ""
            if extra_system_prompt:
                system_prompt = (
                    f"{system_prompt}\n{extra_system_prompt}"
                    if system_prompt
                    else extra_system_prompt
                )

            # 构建上下文信息
            context_str = f"背景信息：{context}" if context else ""

            # 获取原始输出
            raw_output = self.chain.invoke(
                {
                    "question": query,
                    "system_prompt": system_prompt,
                    "context": context_str,
                }
            )

            return raw_output.model_dump()

        except Exception as e:
            raise ValueError(f"处理查询时出错: {str(e)}") from e

    async def ask_async(
        self,
        query: str,
        extra_system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        处理用户查询并返回结构化响应（异步版本）

        Args:
            query: 用户查询文本
            extra_system_prompt: 额外的系统提示
            context: 可选的上下文信息
            **kwargs: 额外参数

        Returns:
            解析并验证后的结构化响应

        Raises:
            ValueError: 当处理查询时发生错误
        """
        try:
            # 构建系统提示
            system_prompt = self.system_prompt or ""
            if extra_system_prompt:
                system_prompt = (
                    f"{system_prompt}\n{extra_system_prompt}"
                    if system_prompt
                    else extra_system_prompt
                )

            # 构建上下文信息
            context_str = f"背景信息：{context}" if context else ""

            # 获取原始输出
            raw_output = await self.chain.ainvoke(
                {
                    "question": query,
                    "system_prompt": system_prompt,
                    "context": context_str,
                }
            )

            return raw_output.model_dump()

        except Exception as e:
            raise ValueError(f"处理查询时出错: {str(e)}") from e
