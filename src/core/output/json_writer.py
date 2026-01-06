"""
JSON格式输出
"""
import json
import pandas as pd
from .base import BaseOutputWriter, OutputWriterFactory


class JSONWriter(BaseOutputWriter):
    """JSON输出写入器"""

    def __init__(self):
        super().__init__()
        self.supported_formats = ['json']

    def write(
        self,
        data: pd.DataFrame,
        output_path: str,
        orient: str = 'records',
        indent: int = 2,
        ensure_ascii: bool = False,
        **kwargs
    ) -> bool:
        """
        写入JSON文件

        Args:
            data: 要写入的数据
            output_path: 输出路径
            orient: JSON格式 ('records', 'index', 'columns', 'values')
            indent: 缩进空格数
            ensure_ascii: 是否转义非ASCII字符
            **kwargs: 传递给pandas.to_json的其他参数

        Returns:
            bool: 是否写入成功
        """
        if not self.validate_data(data):
            raise ValueError("无效的数据")

        try:
            data.to_json(
                output_path,
                orient=orient,
                indent=indent,
                force_ascii=ensure_ascii,
                **kwargs
            )

            return True

        except Exception as e:
            raise RuntimeError(f"写入JSON文件失败: {str(e)}")


# 注册写入器
OutputWriterFactory.register('json', JSONWriter)
