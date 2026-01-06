"""
批量处理器
多行数据一次调用LLM，降低API调用成本
"""
from typing import Dict, Any, Optional, Callable, List
import pandas as pd
from ..llm.base import BaseLLMProvider, LLMResponse
from ..llm.prompt_template import PromptTemplate


class BatchProcessor:
    """批量数据处理器"""

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        prompt_template: PromptTemplate,
        batch_size: int = 10,
        result_parser: Optional[Callable[[str], List[Dict]]] = None,
    ):
        """
        初始化批量处理器

        Args:
            llm_provider: LLM提供商实例
            prompt_template: 提示词模板
            batch_size: 批次大小
            result_parser: 结果解析函数（可选）
        """
        self.llm_provider = llm_provider
        self.prompt_template = prompt_template
        self.batch_size = batch_size
        self.result_parser = result_parser or self._default_parser

    def process_batch(
        self,
        rows: pd.DataFrame,
        batch_index: int,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        处理一批数据

        Args:
            rows: 数据批次
            batch_index: 批次索引
            **kwargs: 额外参数传递给LLM

        Returns:
            list: 处理结果列表
        """
        try:
            # 将批次数据转换为字典列表
            data_list = rows.to_dict('records')

            # 渲染批量提示词
            prompt = self.prompt_template.render_batch(data_list)

            # 调用LLM
            response = self.llm_provider.generate(
                prompt=prompt,
                system_prompt=self.prompt_template.system_prompt,
                **kwargs
            )

            # 解析结果
            parsed_results = self.result_parser(response.content)

            # 构建结果列表
            results = []
            for idx, (row_idx, row_data) in enumerate(zip(rows.index, data_list)):
                # 确保解析结果数量与输入匹配
                if idx < len(parsed_results):
                    parsed_result = parsed_results[idx]
                else:
                    parsed_result = {'error': 'Missing result from LLM'}

                results.append({
                    'row_index': row_idx,
                    'batch_index': batch_index,
                    'original_data': row_data,
                    'llm_response': response.content if idx == 0 else None,  # 只在第一行记录完整响应
                    'parsed_result': parsed_result,
                    'tokens_used': response.tokens_used // len(data_list) if response.tokens_used else 0,
                    'model': response.model,
                    'status': 'success',
                    'error': None,
                })

            return results

        except Exception as e:
            # 批次处理失败，为每一行创建失败记录
            results = []
            for row_idx, row in rows.iterrows():
                results.append({
                    'row_index': row_idx,
                    'batch_index': batch_index,
                    'original_data': row.to_dict(),
                    'llm_response': None,
                    'parsed_result': None,
                    'tokens_used': 0,
                    'model': self.llm_provider.model,
                    'status': 'failed',
                    'error': str(e),
                })
            return results

    def process_dataframe(
        self,
        df: pd.DataFrame,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        处理整个DataFrame（分批处理）

        Args:
            df: 要处理的DataFrame
            progress_callback: 进度回调函数 (current, total)
            **kwargs: 额外参数传递给LLM

        Returns:
            DataFrame: 包含处理结果的DataFrame
        """
        all_results = []
        total_rows = len(df)
        processed_rows = 0

        # 计算批次数量
        num_batches = (total_rows + self.batch_size - 1) // self.batch_size

        for batch_idx in range(num_batches):
            # 获取当前批次
            start_idx = batch_idx * self.batch_size
            end_idx = min(start_idx + self.batch_size, total_rows)
            batch = df.iloc[start_idx:end_idx]

            # 处理批次
            batch_results = self.process_batch(batch, batch_idx, **kwargs)
            all_results.extend(batch_results)

            # 更新进度
            processed_rows = end_idx
            if progress_callback:
                progress_callback(processed_rows, total_rows)

        # 转换为DataFrame
        return pd.DataFrame(all_results)

    def _default_parser(self, response: str) -> List[Dict[str, Any]]:
        """
        默认的批量结果解析器

        Args:
            response: LLM响应文本

        Returns:
            list: 解析后的结果列表
        """
        import json
        import re

        results = []

        # 尝试解析为JSON数组
        try:
            # 查找JSON数组
            array_pattern = r'\[\s*\{.*?\}\s*\]'
            matches = re.findall(array_pattern, response, re.DOTALL)

            if matches:
                parsed = json.loads(matches[0])
                if isinstance(parsed, list):
                    return parsed

            # 尝试查找多个独立的JSON对象
            obj_pattern = r'\{[^{}]*\}'
            matches = re.findall(obj_pattern, response, re.DOTALL)

            for match in matches:
                try:
                    obj = json.loads(match)
                    results.append(obj)
                except json.JSONDecodeError:
                    continue

            if results:
                return results

        except Exception:
            pass

        # 如果无法解析，按行分割
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                results.append({'result': line})

        return results if results else [{'result': response}]

    def estimate_tokens(self, df: pd.DataFrame) -> int:
        """
        估算处理整个DataFrame所需的token数量

        Args:
            df: 要处理的DataFrame

        Returns:
            int: 估算的token数量
        """
        total_tokens = 0
        num_batches = (len(df) + self.batch_size - 1) // self.batch_size

        # 估算一个批次的token数量
        if len(df) > 0:
            sample_size = min(self.batch_size, len(df))
            sample_batch = df.head(sample_size)
            data_list = sample_batch.to_dict('records')
            sample_prompt = self.prompt_template.render_batch(data_list)

            # 计算样本token数
            sample_tokens = self.llm_provider.get_token_count(sample_prompt)

            # 估算总token数
            total_tokens = sample_tokens * num_batches

            # 加上预期的响应token
            total_tokens += num_batches * 500  # 假设每批次响应约500 tokens

        return total_tokens
