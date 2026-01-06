"""
单行处理器
逐行处理数据，每行单独调用LLM
"""
from typing import Dict, Any, Optional, Callable
import pandas as pd
from ..llm.base import BaseLLMProvider, LLMResponse
from ..llm.prompt_template import PromptTemplate


class RowProcessor:
    """单行数据处理器"""

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        prompt_template: PromptTemplate,
        result_parser: Optional[Callable[[str], Dict]] = None,
    ):
        """
        初始化处理器

        Args:
            llm_provider: LLM提供商实例
            prompt_template: 提示词模板
            result_parser: 结果解析函数（可选）
        """
        self.llm_provider = llm_provider
        self.prompt_template = prompt_template
        self.result_parser = result_parser or self._default_parser

    def process_row(
        self,
        row: pd.Series,
        row_index: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        处理单行数据

        Args:
            row: 数据行
            row_index: 行索引
            **kwargs: 额外参数传递给LLM

        Returns:
            dict: 处理结果
        """
        try:
            # 将行数据转换为字典
            row_data = row.to_dict()

            # 渲染提示词
            prompt = self.prompt_template.render(row_data)

            # 调用LLM
            response = self.llm_provider.generate(
                prompt=prompt,
                system_prompt=self.prompt_template.system_prompt,
                **kwargs
            )

            # 解析结果
            parsed_result = self.result_parser(response.content)

            return {
                'row_index': row_index,
                'original_data': row_data,
                'llm_response': response.content,
                'parsed_result': parsed_result,
                'tokens_used': response.tokens_used,
                'model': response.model,
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

    def process_dataframe(
        self,
        df: pd.DataFrame,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        处理整个DataFrame

        Args:
            df: 要处理的DataFrame
            progress_callback: 进度回调函数 (current, total)
            **kwargs: 额外参数传递给LLM

        Returns:
            DataFrame: 包含处理结果的DataFrame
        """
        results = []
        total_rows = len(df)

        for idx, row in df.iterrows():
            # 处理当前行
            result = self.process_row(row, idx, **kwargs)
            results.append(result)

            # 调用进度回调
            if progress_callback:
                progress_callback(idx + 1, total_rows)

        # 转换为DataFrame
        return pd.DataFrame(results)

    def _default_parser(self, response: str) -> Dict[str, Any]:
        """
        默认的结果解析器（尝试JSON解析）

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
                # 尝试解析第一个匹配的JSON
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass

        # 如果无法解析为JSON，返回原始文本
        return {'result': response}
