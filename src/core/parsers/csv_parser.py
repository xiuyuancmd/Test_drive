"""
CSV文档解析器
"""
import os
from typing import Optional, List
import pandas as pd
import chardet
from .base import BaseParser, ParsedDocument, ParserFactory


class CSVParser(BaseParser):
    """CSV文档解析器"""

    def __init__(self):
        super().__init__()
        self.supported_formats = ['.csv']

    def parse(
        self,
        file_path: str,
        encoding: Optional[str] = None,
        delimiter: str = ',',
        header: int = 0,
        skip_rows: Optional[List[int]] = None,
        **kwargs
    ) -> ParsedDocument:
        """
        解析CSV文件

        Args:
            file_path: 文件路径
            encoding: 文件编码，如果为None则自动检测
            delimiter: 分隔符，默认为逗号
            header: 标题行索引，默认为0
            skip_rows: 要跳过的行索引列表
            **kwargs: 传递给pandas.read_csv的其他参数

        Returns:
            ParsedDocument: 解析后的文档
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not self.validate(file_path):
            raise ValueError(f"无效的CSV文件: {file_path}")

        # 自动检测编码
        if encoding is None:
            encoding = self._detect_encoding(file_path)

        try:
            # 读取CSV文件
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                sep=delimiter,
                header=header,
                skiprows=skip_rows,
                **kwargs
            )

            # 获取元信息
            metadata = self.get_metadata(file_path)
            metadata['encoding'] = encoding
            metadata['delimiter'] = delimiter

            return ParsedDocument(
                data=df,
                metadata=metadata,
                sheet_name=None,
                total_rows=len(df),
                column_names=df.columns.tolist(),
                file_format='.csv',
                encoding=encoding
            )

        except Exception as e:
            raise ValueError(f"解析CSV文件失败: {str(e)}")

    def validate(self, file_path: str) -> bool:
        """验证CSV文件是否有效"""
        if not os.path.exists(file_path):
            return False

        if not self.is_supported_format(file_path):
            return False

        try:
            # 尝试读取前几行检查格式
            encoding = self._detect_encoding(file_path)
            pd.read_csv(file_path, encoding=encoding, nrows=5)
            return True
        except Exception:
            return False

    def _detect_encoding(self, file_path: str) -> str:
        """
        自动检测文件编码

        Args:
            file_path: 文件路径

        Returns:
            str: 检测到的编码
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB用于检测
                result = chardet.detect(raw_data)
                encoding = result['encoding']

                # 处理常见的编码别名
                if encoding.lower() in ['gb2312', 'gbk']:
                    encoding = 'gbk'
                elif encoding.lower() in ['utf-8-sig']:
                    encoding = 'utf-8-sig'
                elif encoding is None:
                    encoding = 'utf-8'  # 默认使用UTF-8

                return encoding
        except Exception:
            return 'utf-8'  # 检测失败时使用默认编码


# 注册解析器
ParserFactory.register('.csv', CSVParser)
