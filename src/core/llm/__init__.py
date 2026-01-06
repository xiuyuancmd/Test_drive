"""
LLM集成模块
提供统一的LLM接口和多提供商支持
"""
from .base import (
    BaseLLMProvider,
    LLMProvider,
    LLMMessage,
    LLMResponse,
    LLMProviderFactory
)
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .prompt_template import PromptTemplate, FewShotExample, PromptTemplateLibrary

__all__ = [
    'BaseLLMProvider',
    'LLMProvider',
    'LLMMessage',
    'LLMResponse',
    'LLMProviderFactory',
    'OpenAIProvider',
    'GeminiProvider',
    'PromptTemplate',
    'FewShotExample',
    'PromptTemplateLibrary',
]
