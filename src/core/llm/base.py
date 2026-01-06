"""
LLM提供商基类
定义所有LLM提供商的统一接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass
from enum import Enum


class LLMProvider(str, Enum):
    """支持的LLM提供商"""
    OPENAI = "openai"
    CLAUDE = "claude"
    QWEN = "qwen"
    ERNIE = "ernie"
    LOCAL = "local"


@dataclass
class LLMMessage:
    """LLM消息结构"""
    role: str  # 'system', 'user', 'assistant'
    content: str


@dataclass
class LLMResponse:
    """LLM响应结构"""
    content: str                    # 响应内容
    model: str                      # 使用的模型
    tokens_used: Optional[int]      # 使用的token数量
    finish_reason: Optional[str]    # 完成原因
    metadata: Dict[str, Any]        # 额外元数据


class BaseLLMProvider(ABC):
    """LLM提供商基类"""

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ):
        """
        初始化LLM提供商

        Args:
            api_key: API密钥
            model: 模型名称
            temperature: 温度参数 (0-1)
            max_tokens: 最大token数
            **kwargs: 其他参数
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_params = kwargs

    @abstractmethod
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
            **kwargs: 额外参数

        Returns:
            LLMResponse: 响应对象
        """
        pass

    @abstractmethod
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
        pass

    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[LLMResponse]:
        """
        批量生成文本

        Args:
            prompts: 提示词列表
            system_prompt: 系统提示词
            **kwargs: 额外参数

        Returns:
            list: 响应对象列表
        """
        # 默认实现：逐个调用generate
        return [self.generate(prompt, system_prompt, **kwargs) for prompt in prompts]

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        计算文本的token数量

        Args:
            text: 文本内容

        Returns:
            int: token数量
        """
        pass

    def validate_api_key(self) -> bool:
        """
        验证API密钥是否有效

        Returns:
            bool: API密钥是否有效
        """
        try:
            # 尝试一个简单的请求
            self.generate("test", max_tokens=1)
            return True
        except Exception:
            return False


class LLMProviderFactory:
    """LLM提供商工厂类"""

    _providers: Dict[str, type] = {}

    @classmethod
    def register(cls, provider_name: str, provider_class: type):
        """
        注册LLM提供商

        Args:
            provider_name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[provider_name.lower()] = provider_class

    @classmethod
    def create(
        cls,
        provider_name: str,
        api_key: str,
        model: str,
        **kwargs
    ) -> BaseLLMProvider:
        """
        创建LLM提供商实例

        Args:
            provider_name: 提供商名称
            api_key: API密钥
            model: 模型名称
            **kwargs: 其他参数

        Returns:
            BaseLLMProvider: LLM提供商实例

        Raises:
            ValueError: 不支持的提供商
        """
        provider_name = provider_name.lower()

        if provider_name not in cls._providers:
            raise ValueError(f"不支持的LLM提供商: {provider_name}")

        return cls._providers[provider_name](
            api_key=api_key,
            model=model,
            **kwargs
        )

    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取所有支持的提供商"""
        return list(cls._providers.keys())
