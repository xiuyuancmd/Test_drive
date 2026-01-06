"""
结果输出模块
支持多种输出格式
"""
from .base import BaseOutputWriter, OutputWriterFactory
from .excel_writer import ExcelWriter
from .csv_writer import CSVWriter
from .json_writer import JSONWriter

__all__ = [
    'BaseOutputWriter',
    'OutputWriterFactory',
    'ExcelWriter',
    'CSVWriter',
    'JSONWriter',
]
