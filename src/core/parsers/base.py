"""
文档解析器基类
定义所有解析器的统一接口
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import pandas as pd


@dataclass
class ParsedDocument:
    """解析后的文档数据结构"""
    data: pd.DataFrame              # 解析后的数据
    metadata: Dict[str, Any]        # 文件元信息
    sheet_name: Optional[str]       # 工作表名称（Excel专用）
    total_rows: int                 # 总行数
    column_names: List[str]         # 列名
    file_format: str                # 文件格式
    encoding: Optional[str] = None  # 文件编码


class BaseParser(ABC):
    """文档解析器基类"""

    def __init__(self):
        self.supported_formats: List[str] = []

    @abstractmethod
    def parse(self, file_path: str, **kwargs) -> ParsedDocument:
        """
        解析文档文件

        Args:
            file_path: 文件路径
            **kwargs: 额外参数（如sheet_name, encoding等）

        Returns:
            ParsedDocument: 解析后的文档对象
        """
        pass

    @abstractmethod
    def validate(self, file_path: str) -> bool:
        """
        验证文件是否有效

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否有效
        """
        pass

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件元信息

        Args:
            file_path: 文件路径

        Returns:
            dict: 文件元信息
        """
        import os
        from datetime import datetime

        stat = os.stat(file_path)
        return {
            'file_name': os.path.basename(file_path),
            'file_size': stat.st_size,
            'file_path': os.path.abspath(file_path),
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    def is_supported_format(self, file_path: str) -> bool:
        """
        检查文件格式是否被支持

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否支持该格式
        """
        import os
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_formats


class ParserFactory:
    """解析器工厂类"""

    _parsers: Dict[str, type] = {}

    @classmethod
    def register(cls, file_format: str, parser_class: type):
        """
        注册解析器

        Args:
            file_format: 文件格式（如.xlsx）
            parser_class: 解析器类
        """
        cls._parsers[file_format.lower()] = parser_class

    @classmethod
    def create(cls, file_path: str) -> BaseParser:
        """
        根据文件格式创建对应的解析器

        Args:
            file_path: 文件路径

        Returns:
            BaseParser: 解析器实例

        Raises:
            ValueError: 不支持的文件格式
        """
        import os
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in cls._parsers:
            raise ValueError(f"不支持的文件格式: {ext}")

        return cls._parsers[ext]()

    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """获取所有支持的文件格式"""
        return list(cls._parsers.keys())
