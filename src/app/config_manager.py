"""
配置管理器
负责加载和验证配置文件
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from dataclasses import dataclass, field


@dataclass
class TaskConfig:
    """任务配置"""
    name: str
    description: str = ""
    task_id: Optional[str] = None


@dataclass
class InputConfig:
    """输入配置"""
    file: str
    sheet: Optional[str] = None
    encoding: str = "utf-8"
    skip_rows: list = field(default_factory=list)
    columns: list = field(default_factory=list)
    filter: Optional[Dict[str, Any]] = None


@dataclass
class ProcessingConfig:
    """处理配置"""
    mode: str = "row"  # row, batch, stream
    batch_size: int = 10
    input_columns: list = field(default_factory=list)
    column_mapping: Dict[str, str] = field(default_factory=dict)
    concurrent: bool = False
    max_workers: int = 5


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    prompt_template: str = ""
    system_prompt: Optional[str] = None
    few_shot_examples: list = field(default_factory=list)
    output_format: Optional[str] = None


@dataclass
class OutputConfig:
    """输出配置"""
    file: str
    format: str = "xlsx"
    columns: list = field(default_factory=list)
    include_original: bool = True
    include_raw_response: bool = False
    include_metadata: bool = True


@dataclass
class RetryConfig:
    """重试配置"""
    enabled: bool = True
    max_attempts: int = 3
    backoff_factor: float = 2.0
    timeout: int = 30


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self.config: Optional[Dict[str, Any]] = None
        self.task_config: Optional[TaskConfig] = None
        self.input_config: Optional[InputConfig] = None
        self.processing_config: Optional[ProcessingConfig] = None
        self.llm_config: Optional[LLMConfig] = None
        self.output_config: Optional[OutputConfig] = None
        self.retry_config: Optional[RetryConfig] = None

    def load_from_file(self, config_path: str):
        """
        从YAML文件加载配置

        Args:
            config_path: 配置文件路径
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self._parse_config()
        self._resolve_env_vars()
        self._validate_config()

    def load_from_dict(self, config_dict: Dict[str, Any]):
        """
        从字典加载配置

        Args:
            config_dict: 配置字典
        """
        self.config = config_dict
        self._parse_config()
        self._resolve_env_vars()
        self._validate_config()

    def _parse_config(self):
        """解析配置为数据类"""
        if not self.config:
            return

        # 任务配置
        task_data = self.config.get('task', {})
        self.task_config = TaskConfig(**task_data)

        # 输入配置
        input_data = self.config.get('input', {})
        self.input_config = InputConfig(**input_data)

        # 处理配置
        processing_data = self.config.get('processing', {})
        self.processing_config = ProcessingConfig(**processing_data)

        # LLM配置
        llm_data = self.config.get('llm', {})
        self.llm_config = LLMConfig(**llm_data)

        # 输出配置
        output_data = self.config.get('output', {})
        self.output_config = OutputConfig(**output_data)

        # 重试配置
        retry_data = self.config.get('retry', {})
        self.retry_config = RetryConfig(**retry_data)

    def _resolve_env_vars(self):
        """解析环境变量"""
        if self.llm_config and self.llm_config.api_key:
            # 解析 ${VAR_NAME} 格式的环境变量
            api_key = self.llm_config.api_key
            if api_key.startswith('${') and api_key.endswith('}'):
                var_name = api_key[2:-1]
                self.llm_config.api_key = os.getenv(var_name)

                if not self.llm_config.api_key:
                    raise ValueError(f"环境变量未设置: {var_name}")

    def _validate_config(self):
        """验证配置"""
        # 验证输入文件
        if self.input_config:
            if not self.input_config.file:
                raise ValueError("输入文件路径不能为空")

        # 验证处理模式
        if self.processing_config:
            valid_modes = ['row', 'batch', 'stream']
            if self.processing_config.mode not in valid_modes:
                raise ValueError(f"无效的处理模式: {self.processing_config.mode}")

        # 验证LLM配置
        if self.llm_config:
            if not self.llm_config.provider:
                raise ValueError("LLM提供商不能为空")

            if not self.llm_config.model:
                raise ValueError("LLM模型不能为空")

            if not self.llm_config.prompt_template:
                raise ValueError("提示词模板不能为空")

        # 验证输出配置
        if self.output_config:
            if not self.output_config.file:
                raise ValueError("输出文件路径不能为空")

    def get_llm_provider_params(self) -> Dict[str, Any]:
        """获取LLM提供商初始化参数"""
        if not self.llm_config:
            raise ValueError("LLM配置未加载")

        params = {
            'api_key': self.llm_config.api_key,
            'model': self.llm_config.model,
            'temperature': self.llm_config.temperature,
            'max_tokens': self.llm_config.max_tokens,
        }

        if self.llm_config.base_url:
            params['base_url'] = self.llm_config.base_url

        return params

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config

    def save_to_file(self, output_path: str):
        """
        保存配置到文件

        Args:
            output_path: 输出路径
        """
        if not self.config:
            raise ValueError("配置为空")

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)

    @staticmethod
    def create_default_config() -> Dict[str, Any]:
        """创建默认配置"""
        return {
            'task': {
                'name': '默认任务',
                'description': '使用默认配置的处理任务'
            },
            'input': {
                'file': 'input.xlsx',
                'encoding': 'utf-8'
            },
            'processing': {
                'mode': 'row',
                'batch_size': 10
            },
            'llm': {
                'provider': 'openai',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 1000,
                'api_key': '${OPENAI_API_KEY}',
                'prompt_template': '请处理以下数据: {data}'
            },
            'output': {
                'file': 'output.xlsx',
                'format': 'xlsx'
            },
            'retry': {
                'enabled': True,
                'max_attempts': 3,
                'backoff_factor': 2.0
            }
        }
