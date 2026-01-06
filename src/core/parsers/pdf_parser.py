"""
PDF文档解析器
支持从PDF中提取表格数据
"""
import os
from typing import Optional, List
import pandas as pd
from .base import BaseParser, ParsedDocument, ParserFactory


class PDFParser(BaseParser):
    """PDF文档解析器"""

    def __init__(self):
        super().__init__()
        self.supported_formats = ['.pdf']

    def parse(
        self,
        file_path: str,
        pages: Optional[List[int]] = None,
        method: str = 'lattice',  # 'lattice' 或 'stream'
        **kwargs
    ) -> ParsedDocument:
        """
        解析PDF文件中的表格

        Args:
            file_path: 文件路径
            pages: 要解析的页码列表，默认为所有页
            method: 表格提取方法
                - 'lattice': 基于表格线的提取（适用于有边框的表格）
                - 'stream': 基于文本流的提取（适用于无边框的表格）
            **kwargs: 传递给tabula或pdfplumber的其他参数

        Returns:
            ParsedDocument: 解析后的文档
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not self.validate(file_path):
            raise ValueError(f"无效的PDF文件: {file_path}")

        try:
            # 尝试使用tabula-py提取表格
            df = self._extract_with_tabula(file_path, pages, method, **kwargs)

            # 如果tabula失败，尝试使用pdfplumber
            if df is None or df.empty:
                df = self._extract_with_pdfplumber(file_path, pages, **kwargs)

            if df is None or df.empty:
                raise ValueError("无法从PDF中提取表格数据")

            # 获取元信息
            metadata = self.get_metadata(file_path)
            metadata.update(self._get_pdf_metadata(file_path))

            return ParsedDocument(
                data=df,
                metadata=metadata,
                sheet_name=None,
                total_rows=len(df),
                column_names=df.columns.tolist(),
                file_format='.pdf',
                encoding=None
            )

        except Exception as e:
            raise ValueError(f"解析PDF文件失败: {str(e)}")

    def validate(self, file_path: str) -> bool:
        """验证PDF文件是否有效"""
        if not os.path.exists(file_path):
            return False

        if not self.is_supported_format(file_path):
            return False

        try:
            # 简单验证PDF文件头
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header == b'%PDF'
        except Exception:
            return False

    def _extract_with_tabula(
        self,
        file_path: str,
        pages: Optional[List[int]],
        method: str,
        **kwargs
    ) -> Optional[pd.DataFrame]:
        """使用tabula-py提取表格"""
        try:
            import tabula

            # 转换页码格式
            pages_str = 'all' if pages is None else ','.join(map(str, pages))

            # 提取表格
            dfs = tabula.read_pdf(
                file_path,
                pages=pages_str,
                lattice=(method == 'lattice'),
                stream=(method == 'stream'),
                **kwargs
            )

            if dfs and len(dfs) > 0:
                # 如果有多个表格，合并它们
                return pd.concat(dfs, ignore_index=True)

            return None

        except ImportError:
            # tabula未安装，返回None
            return None
        except Exception:
            return None

    def _extract_with_pdfplumber(
        self,
        file_path: str,
        pages: Optional[List[int]],
        **kwargs
    ) -> Optional[pd.DataFrame]:
        """使用pdfplumber提取表格"""
        try:
            import pdfplumber

            all_tables = []

            with pdfplumber.open(file_path) as pdf:
                target_pages = pages if pages else range(len(pdf.pages))

                for page_num in target_pages:
                    if page_num < len(pdf.pages):
                        page = pdf.pages[page_num]
                        tables = page.extract_tables()

                        for table in tables:
                            if table:
                                # 将表格转换为DataFrame
                                df = pd.DataFrame(table[1:], columns=table[0])
                                all_tables.append(df)

            if all_tables:
                return pd.concat(all_tables, ignore_index=True)

            return None

        except ImportError:
            return None
        except Exception:
            return None

    def _get_pdf_metadata(self, file_path: str) -> dict:
        """获取PDF元信息"""
        try:
            import PyPDF2

            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                return {
                    'page_count': len(pdf_reader.pages),
                    'pdf_info': pdf_reader.metadata or {}
                }
        except Exception:
            return {}


# 注册解析器
ParserFactory.register('.pdf', PDFParser)
