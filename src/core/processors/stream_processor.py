"""
流式处理器
边处理边输出，适合大文件处理和实时反馈
"""
from typing import Dict, Any, Optional, Callable, Generator
import pandas as pd
from ..llm.base import BaseLLMProvider
from ..llm.prompt_template import PromptTemplate


class StreamProcessor:
    """流式数据处理器"""

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        prompt_template: PromptTemplate,
        result_parser: Optional[Callable[[str], Dict]] = None,
    ):
        """
        初始化流式处理器

        Args:
            llm_provider: LLM提供商实例
            prompt_template: 提示词模板
            result_parser: 结果解析函数（可选）
        """
        self.llm_provider = llm_provider
        self.prompt_template = prompt_template
        self.result_parser = result_parser or self._default_parser

    def process_row_stream(
        self,
        row: pd.Series,
        row_index: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        流式处理单行数据

        Args:
            row: 数据行
            row_index: 行索引
            **kwargs: 额外参数传递给LLM

        Returns:
            dict: 处理结果（包含流式响应的累积结果）
        """
        try:
            # 将行数据转换为字典
            row_data = row.to_dict()

            # 渲染提示词
            prompt = self.prompt_template.render(row_data)

            # 累积流式响应
            full_response = ""

            # 调用LLM流式生成
            for chunk in self.llm_provider.generate_stream(
                prompt=prompt,
                system_prompt=self.prompt_template.system_prompt,
                **kwargs
            ):
                full_response += chunk

            # 解析最终结果
            parsed_result = self.result_parser(full_response)

            return {
                'row_index': row_index,
                'original_data': row_data,
                'llm_response': full_response,
                'parsed_result': parsed_result,
                'tokens_used': self.llm_provider.get_token_count(full_response),
                'model': self.llm_provider.model,
                'status': 'success',
                'error': None,
            }

        except Exception as e:
            return {
                'row_index': row_index,
                'original_data': row.to_dict(),
                'llm_response': None,
                'parsed_result': None,
                'tokens_used': 0,
                'model': self.llm_provider.model,
                'status': 'failed',
                'error': str(e),
            }

    def process_stream(
        self,
        df: pd.DataFrame,
        **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式处理DataFrame，边处理边返回结果

        Args:
            df: 要处理的DataFrame
            **kwargs: 额外参数传递给LLM

        Yields:
            dict: 每一行的处理结果
        """
        for idx, row in df.iterrows():
            result = self.process_row_stream(row, idx, **kwargs)
            yield result

    def process_dataframe(
        self,
        df: pd.DataFrame,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        处理整个DataFrame（流式处理，但收集所有结果）

        Args:
            df: 要处理的DataFrame
            progress_callback: 进度回调函数 (current, total)
            **kwargs: 额外参数传递给LLM

        Returns:
            DataFrame: 包含处理结果的DataFrame
        """
        results = []
        total_rows = len(df)

        for current, result in enumerate(self.process_stream(df, **kwargs), 1):
            results.append(result)

            if progress_callback:
                progress_callback(current, total_rows)

        return pd.DataFrame(results)

    def _default_parser(self, response: str) -> Dict[str, Any]:
        """
        默认的结果解析器

        Args:
            response: LLM响应文本

        Returns:
            dict: 解析后的结果
        """
        import json
        import re

        # 尝试提取JSON
        json_pattern = r'\{[^\}]*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)

        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass

        # 无法解析为JSON，返回原始文本
        return {'result': response}
