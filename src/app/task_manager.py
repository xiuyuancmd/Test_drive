"""
任务管理器
负责任务的创建、执行和管理
"""
import os
import uuid
from typing import Optional, Callable
from datetime import datetime
import pandas as pd

from .config_manager import ConfigManager
from .progress_tracker import ProgressTracker, TaskStatus
from ..core.parsers import ParserFactory
from ..core.llm import LLMProviderFactory, PromptTemplate
from ..core.processors import RowProcessor, BatchProcessor, StreamProcessor
from ..core.output import OutputWriterFactory


class TaskManager:
    """任务管理器"""

    def __init__(self, config_manager: ConfigManager):
        """
        初始化任务管理器

        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.task_id = str(uuid.uuid4())
        self.progress_tracker: Optional[ProgressTracker] = None

    def execute(
        self,
        progress_callback: Optional[Callable] = None
    ) -> dict:
        """
        执行任务

        Args:
            progress_callback: 进度回调函数

        Returns:
            dict: 执行结果
        """
        try:
            # 1. 解析输入文件
            print("📄 解析输入文件...")
            input_data = self._parse_input()
            print(f"✓ 成功加载 {len(input_data)} 行数据")

            # 2. 初始化进度追踪
            self.progress_tracker = ProgressTracker(
                task_id=self.task_id,
                total=len(input_data),
                callback=progress_callback
            )
            self.progress_tracker.start()

            # 3. 创建LLM提供商
            print("\n🤖 初始化LLM提供商...")
            llm_provider = self._create_llm_provider()
            print(f"✓ 使用 {self.config_manager.llm_config.provider} - {self.config_manager.llm_config.model}")

            # 4. 创建处理器
            print("\n⚙️  初始化数据处理器...")
            processor = self._create_processor(llm_provider)
            print(f"✓ 使用 {self.config_manager.processing_config.mode} 模式")

            # 5. 处理数据
            print("\n🔄 开始处理数据...")
            results = self._process_data(processor, input_data)
            print(f"\n✓ 处理完成: {self.progress_tracker.progress.success_count} 成功, {self.progress_tracker.progress.failed_count} 失败")

            # 6. 输出结果
            print("\n💾 保存结果...")
            self._save_results(results)
            print(f"✓ 结果已保存到: {self.config_manager.output_config.file}")

            # 7. 完成任务
            self.progress_tracker.complete()

            # 返回执行摘要
            return self._create_summary(results)

        except Exception as e:
            if self.progress_tracker:
                self.progress_tracker.fail(str(e))

            print(f"\n❌ 任务执行失败: {str(e)}")
            raise

    def _parse_input(self) -> pd.DataFrame:
        """解析输入文件"""
        input_config = self.config_manager.input_config

        # 检查文件是否存在
        if not os.path.exists(input_config.file):
            raise FileNotFoundError(f"输入文件不存在: {input_config.file}")

        # 创建解析器
        parser = ParserFactory.create(input_config.file)

        # 解析参数
        parse_kwargs = {}
        if input_config.sheet:
            parse_kwargs['sheet_name'] = input_config.sheet
        if input_config.encoding:
            parse_kwargs['encoding'] = input_config.encoding
        if input_config.skip_rows:
            parse_kwargs['skip_rows'] = input_config.skip_rows

        # 解析文件
        document = parser.parse(input_config.file, **parse_kwargs)

        # 筛选列
        df = document.data
        if input_config.columns:
            df = df[input_config.columns]

        # 应用过滤条件
        if input_config.filter and input_config.filter.get('enabled'):
            filter_config = input_config.filter
            column = filter_config['column']
            operator = filter_config.get('operator', 'equals')
            value = filter_config['value']

            if operator == 'equals':
                df = df[df[column] == value]
            elif operator == 'not_equals':
                df = df[df[column] != value]
            elif operator == 'contains':
                df = df[df[column].str.contains(value, na=False)]
            elif operator == 'greater_than':
                df = df[df[column] > value]
            elif operator == 'less_than':
                df = df[df[column] < value]

        return df

    def _create_llm_provider(self):
        """创建LLM提供商"""
        llm_config = self.config_manager.llm_config

        provider = LLMProviderFactory.create(
            provider_name=llm_config.provider,
            **self.config_manager.get_llm_provider_params()
        )

        return provider

    def _create_processor(self, llm_provider):
        """创建处理器"""
        processing_config = self.config_manager.processing_config
        llm_config = self.config_manager.llm_config

        # 创建提示词模板
        prompt_template = PromptTemplate(
            template=llm_config.prompt_template,
            system_prompt=llm_config.system_prompt,
            output_format=llm_config.output_format
        )

        # 添加few-shot示例
        for example in llm_config.few_shot_examples:
            prompt_template.add_example(
                input_data=example.get('input', {}),
                output=example.get('output', '')
            )

        # 根据模式创建处理器
        mode = processing_config.mode

        if mode == 'row':
            return RowProcessor(llm_provider, prompt_template)
        elif mode == 'batch':
            return BatchProcessor(
                llm_provider,
                prompt_template,
                batch_size=processing_config.batch_size
            )
        elif mode == 'stream':
            return StreamProcessor(llm_provider, prompt_template)
        else:
            raise ValueError(f"不支持的处理模式: {mode}")

    def _process_data(self, processor, data: pd.DataFrame) -> pd.DataFrame:
        """处理数据"""
        def progress_callback(current, total):
            if self.progress_tracker:
                # 假设成功（实际成功失败在结果中判断）
                self.progress_tracker.update(current, success=True, tokens=0)
                self.progress_tracker.print_progress_bar()

        # 处理数据
        results = processor.process_dataframe(
            data,
            progress_callback=progress_callback
        )

        # 更新token统计
        if self.progress_tracker:
            total_tokens = results['tokens_used'].sum()
            self.progress_tracker.progress.total_tokens = int(total_tokens)

            success_count = len(results[results['status'] == 'success'])
            failed_count = len(results[results['status'] == 'failed'])
            self.progress_tracker.progress.success_count = success_count
            self.progress_tracker.progress.failed_count = failed_count

        return results

    def _save_results(self, results: pd.DataFrame):
        """保存结果"""
        output_config = self.config_manager.output_config

        # 准备输出数据
        output_data = results.copy()

        # 根据配置选择列
        if output_config.columns:
            # 只保留指定的列
            available_columns = [col for col in output_config.columns if col in output_data.columns]
            output_data = output_data[available_columns]
        else:
            # 默认列选择
            if not output_config.include_original:
                if 'original_data' in output_data.columns:
                    output_data = output_data.drop(columns=['original_data'])

            if not output_config.include_raw_response:
                if 'llm_response' in output_data.columns:
                    output_data = output_data.drop(columns=['llm_response'])

            if not output_config.include_metadata:
                metadata_cols = ['tokens_used', 'model']
                for col in metadata_cols:
                    if col in output_data.columns:
                        output_data = output_data.drop(columns=[col])

        # 创建输出目录
        output_dir = os.path.dirname(output_config.file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 写入文件
        writer = OutputWriterFactory.create(output_config.format)
        writer.write(output_data, output_config.file)

    def _create_summary(self, results: pd.DataFrame) -> dict:
        """创建执行摘要"""
        if not self.progress_tracker:
            return {}

        progress = self.progress_tracker.progress

        return {
            'task_id': self.task_id,
            'status': progress.status.value,
            'total_rows': progress.total,
            'success_count': progress.success_count,
            'failed_count': progress.failed_count,
            'total_tokens': progress.total_tokens,
            'estimated_cost': progress.estimated_cost,
            'elapsed_time': progress.elapsed_time,
            'output_file': self.config_manager.output_config.file,
            'start_time': progress.start_time.isoformat() if progress.start_time else None,
            'end_time': progress.end_time.isoformat() if progress.end_time else None,
        }

    def get_progress(self) -> Optional[dict]:
        """获取当前进度"""
        if self.progress_tracker:
            return self.progress_tracker.progress.to_dict()
        return None
