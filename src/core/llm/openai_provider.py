"""
OpenAI LLM提供商实现
"""
from typing import Optional, Generator
from .base import BaseLLMProvider, LLMResponse, LLMProviderFactory


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM提供商"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        初始化OpenAI提供商

        Args:
            api_key: OpenAI API密钥
            model: 模型名称 (gpt-3.5-turbo, gpt-4, gpt-4-turbo等)
            temperature: 温度参数
            max_tokens: 最大token数
            base_url: API基础URL（用于自定义端点）
            **kwargs: 其他参数
        """
        super().__init__(api_key, model, temperature, max_tokens, **kwargs)
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        """获取或创建OpenAI客户端"""
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise ImportError("请安装openai库: pip install openai")

        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成文本

        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            **kwargs: 额外参数（覆盖默认配置）

        Returns:
            LLMResponse: 响应对象
        """
        client = self._get_client()

        # 构建消息列表
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # 合并参数
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.extra_params,
            **kwargs
        }

        try:
            response = client.chat.completions.create(**params)

            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                    "completion_tokens": response.usage.completion_tokens if response.usage else None,
                }
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI API调用失败: {str(e)}")

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        流式生成文本

        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            **kwargs: 额外参数

        Yields:
            str: 生成的文本片段
        """
        client = self._get_client()

        # 构建消息列表
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # 合并参数
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True,
            **self.extra_params,
            **kwargs
        }

        try:
            response = client.chat.completions.create(**params)

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise RuntimeError(f"OpenAI流式调用失败: {str(e)}")

    def get_token_count(self, text: str) -> int:
        """
        计算文本的token数量

        Args:
            text: 文本内容

        Returns:
            int: token数量
        """
        try:
            import tiktoken

            # 根据模型选择编码器
            if "gpt-4" in self.model:
                encoding = tiktoken.encoding_for_model("gpt-4")
            elif "gpt-3.5" in self.model:
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                encoding = tiktoken.get_encoding("cl100k_base")

            return len(encoding.encode(text))

        except ImportError:
            # 如果tiktoken未安装，使用简单估算
            # 平均每个token约4个字符（英文）或1.5个字符（中文）
            # 这里取一个中间值
            return len(text) // 3

    def count_messages_tokens(self, messages: list) -> int:
        """
        计算消息列表的token数量

        Args:
            messages: 消息列表

        Returns:
            int: token数量
        """
        total = 0
        for message in messages:
            total += self.get_token_count(message.get("content", ""))
            total += 4  # 每条消息的格式开销

        total += 2  # 对话的起始和结束token
        return total


# 注册提供商
LLMProviderFactory.register("openai", OpenAIProvider)
