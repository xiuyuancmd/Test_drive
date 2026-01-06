"""
CSV格式输出
"""
import pandas as pd
from .base import BaseOutputWriter, OutputWriterFactory


class CSVWriter(BaseOutputWriter):
    """CSV输出写入器"""

    def __init__(self):
        super().__init__()
        self.supported_formats = ['csv']

    def write(
        self,
        data: pd.DataFrame,
        output_path: str,
        encoding: str = 'utf-8',
        include_index: bool = False,
        **kwargs
    ) -> bool:
        """
        写入CSV文件

        Args:
            data: 要写入的数据
            output_path: 输出路径
            encoding: 文件编码
            include_index: 是否包含索引
            **kwargs: 传递给pandas.to_csv的其他参数

        Returns:
            bool: 是否写入成功
        """
        if not self.validate_data(data):
            raise ValueError("无效的数据")

        try:
            data.to_csv(
                output_path,
                encoding=encoding,
                index=include_index,
                **kwargs
            )

            return True

        except Exception as e:
            raise RuntimeError(f"写入CSV文件失败: {str(e)}")


# 注册写入器
OutputWriterFactory.register('csv', CSVWriter)
