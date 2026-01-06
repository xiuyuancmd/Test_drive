"""
结果输出模块基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd


class BaseOutputWriter(ABC):
    """输出写入器基类"""

    def __init__(self):
        self.supported_formats = []

    @abstractmethod
    def write(self, data: pd.DataFrame, output_path: str, **kwargs) -> bool:
        """
        写入数据

        Args:
            data: 要写入的数据
            output_path: 输出路径
            **kwargs: 额外参数

        Returns:
            bool: 是否写入成功
        """
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        验证数据是否有效

        Args:
            data: 要验证的数据

        Returns:
            bool: 数据是否有效
        """
        return data is not None and not data.empty


class OutputWriterFactory:
    """输出写入器工厂"""

    _writers: Dict[str, type] = {}

    @classmethod
    def register(cls, format_name: str, writer_class: type):
        """
        注册写入器

        Args:
            format_name: 格式名称（如xlsx）
            writer_class: 写入器类
        """
        cls._writers[format_name.lower()] = writer_class

    @classmethod
    def create(cls, format_name: str) -> BaseOutputWriter:
        """
        创建写入器实例

        Args:
            format_name: 格式名称

        Returns:
            BaseOutputWriter: 写入器实例

        Raises:
            ValueError: 不支持的格式
        """
        format_name = format_name.lower().lstrip('.')

        if format_name not in cls._writers:
            raise ValueError(f"不支持的输出格式: {format_name}")

        return cls._writers[format_name]()

    @classmethod
    def get_supported_formats(cls):
        """获取支持的格式列表"""
        return list(cls._writers.keys())
