"""
Excel文档解析器 (支持 .xlsx 和 .xls 格式)
"""
import os
from typing import Optional, List, Dict, Any
import pandas as pd
from .base import BaseParser, ParsedDocument, ParserFactory


class ExcelParser(BaseParser):
    """Excel文档解析器"""

    def __init__(self):
        super().__init__()
        self.supported_formats = ['.xlsx', '.xls']

    def parse(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        header: int = 0,
        skip_rows: Optional[List[int]] = None,
        use_cols: Optional[List[str]] = None,
        **kwargs
    ) -> ParsedDocument:
        """
        解析Excel文件

        Args:
            file_path: 文件路径
            sheet_name: 工作表名称，默认为第一个sheet
            header: 标题行索引，默认为0
            skip_rows: 要跳过的行索引列表
            use_cols: 要读取的列名列表
            **kwargs: 传递给pandas.read_excel的其他参数

        Returns:
            ParsedDocument: 解析后的文档

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持或解析失败
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not self.validate(file_path):
            raise ValueError(f"无效的Excel文件: {file_path}")

        try:
            # 如果未指定sheet_name，读取第一个sheet
            if sheet_name is None:
                sheet_name = 0

            # 读取Excel文件
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=header,
                skiprows=skip_rows,
                usecols=use_cols,
                **kwargs
            )

            # 获取实际的sheet名称
            if isinstance(sheet_name, int):
                with pd.ExcelFile(file_path) as xls:
                    actual_sheet_name = xls.sheet_names[sheet_name]
            else:
                actual_sheet_name = sheet_name

            # 获取元信息
            metadata = self.get_metadata(file_path)
            metadata.update(self._get_excel_metadata(file_path))

            # 构建ParsedDocument对象
            return ParsedDocument(
                data=df,
                metadata=metadata,
                sheet_name=actual_sheet_name,
                total_rows=len(df),
                column_names=df.columns.tolist(),
                file_format=os.path.splitext(file_path)[1].lower(),
                encoding=None  # Excel文件没有文本编码概念
            )

        except Exception as e:
            raise ValueError(f"解析Excel文件失败: {str(e)}")

    def validate(self, file_path: str) -> bool:
        """
        验证Excel文件是否有效

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否有效
        """
        if not os.path.exists(file_path):
            return False

        if not self.is_supported_format(file_path):
            return False

        try:
            # 尝试打开文件检查是否损坏
            with pd.ExcelFile(file_path) as xls:
                return len(xls.sheet_names) > 0
        except Exception:
            return False

    def _get_excel_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        获取Excel特定的元信息

        Args:
            file_path: 文件路径

        Returns:
            dict: Excel元信息
        """
        try:
            with pd.ExcelFile(file_path) as xls:
                return {
                    'sheet_names': xls.sheet_names,
                    'sheet_count': len(xls.sheet_names),
                }
        except Exception:
            return {}

    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        获取Excel文件中所有的sheet名称

        Args:
            file_path: 文件路径

        Returns:
            list: sheet名称列表
        """
        try:
            with pd.ExcelFile(file_path) as xls:
                return xls.sheet_names
        except Exception as e:
            raise ValueError(f"无法读取sheet列表: {str(e)}")

    def parse_all_sheets(self, file_path: str, **kwargs) -> Dict[str, ParsedDocument]:
        """
        解析Excel文件中的所有sheet

        Args:
            file_path: 文件路径
            **kwargs: 传递给parse方法的参数

        Returns:
            dict: {sheet_name: ParsedDocument} 字典
        """
        sheet_names = self.get_sheet_names(file_path)
        results = {}

        for sheet_name in sheet_names:
            results[sheet_name] = self.parse(file_path, sheet_name=sheet_name, **kwargs)

        return results


# 注册解析器到工厂
ParserFactory.register('.xlsx', ExcelParser)
ParserFactory.register('.xls', ExcelParser)
