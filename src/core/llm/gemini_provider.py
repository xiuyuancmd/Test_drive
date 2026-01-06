"""
Google Gemini LLM提供商实现
支持 Gemini Pro, Gemini Flash 等模型
"""
from typing import Optional, Generator
from .base import BaseLLMProvider, LLMResponse, LLMProviderFactory


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM提供商"""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ):
        """
        初始化Gemini提供商

        Args:
            api_key: Google API密钥
            model: 模型名称 (gemini-1.5-pro, gemini-1.5-flash, gemini-pro等)
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
        """
        super().__init__(api_key, model, temperature, max_tokens, **kwargs)
        self._client = None

    def _get_client(self):
        """获取或创建Gemini客户端"""
        if self._client is None:
            try:
                import google.generativeai as genai

                # 配置API密钥
                genai.configure(api_key=self.api_key)

                # 创建生成配置
                generation_config = {
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }

                # 创建模型实例
                self._client = genai.GenerativeModel(
                    model_name=self.model,
                    generation_config=generation_config
                )

            except ImportError:
                raise ImportError(
                    "请安装google-generativeai库: pip install google-generativeai"
                )

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
            system_prompt: 系统提示词（Gemini会将其添加到prompt前面）
            **kwargs: 额外参数

        Returns:
            LLMResponse: 响应对象
        """
        client = self._get_client()

        try:
            # 合并system_prompt和prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # 调用API
            response = client.generate_content(full_prompt)

            # 提取响应文本
            response_text = response.text

            # 估算token使用（Gemini API没有直接返回token数）
            tokens_used = self.get_token_count(full_prompt) + self.get_token_count(response_text)

            return LLMResponse(
                content=response_text,
                model=self.model,
                tokens_used=tokens_used,
                finish_reason=response.candidates[0].finish_reason.name if response.candidates else None,
                metadata={
                    'prompt_tokens': self.get_token_count(full_prompt),
                    'completion_tokens': self.get_token_count(response_text),
                    'safety_ratings': [
                        {
                            'category': rating.category.name,
                            'probability': rating.probability.name
                        }
                        for rating in response.candidates[0].safety_ratings
                    ] if response.candidates else []
                }
            )

        except Exception as e:
            raise RuntimeError(f"Gemini API调用失败: {str(e)}")

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

        try:
            # 合并system_prompt和prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # 流式调用API
            response = client.generate_content(full_prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            raise RuntimeError(f"Gemini流式调用失败: {str(e)}")

    def get_token_count(self, text: str) -> int:
        """
        计算文本的token数量（估算）

        Gemini使用类似的分词方式，可以用近似方法估算
        平均每个token约3.5个字符（英文）或1.5个字符（中文）

        Args:
            text: 文本内容

        Returns:
            int: token数量
        """
        # 简单估算：按字符数除以平均字符/token比例
        # 对于混合中英文，使用2.5作为平均值
        return int(len(text) / 2.5)

    def count_tokens_precise(self, text: str) -> int:
        """
        使用Gemini API精确计算token数

        Args:
            text: 文本内容

        Returns:
            int: 精确的token数量
        """
        try:
            client = self._get_client()
            # Gemini提供count_tokens方法
            result = client.count_tokens(text)
            return result.total_tokens
        except Exception:
            # 如果API调用失败，回退到估算
            return self.get_token_count(text)


# 注册提供商
LLMProviderFactory.register("gemini", GeminiProvider)
