"""
Excel格式输出
"""
import pandas as pd
from .base import BaseOutputWriter, OutputWriterFactory


class ExcelWriter(BaseOutputWriter):
    """Excel输出写入器"""

    def __init__(self):
        super().__init__()
        self.supported_formats = ['xlsx', 'xls']

    def write(
        self,
        data: pd.DataFrame,
        output_path: str,
        sheet_name: str = 'Results',
        include_index: bool = False,
        **kwargs
    ) -> bool:
        """
        写入Excel文件

        Args:
            data: 要写入的数据
            output_path: 输出路径
            sheet_name: 工作表名称
            include_index: 是否包含索引
            **kwargs: 传递给pandas.to_excel的其他参数

        Returns:
            bool: 是否写入成功
        """
        if not self.validate_data(data):
            raise ValueError("无效的数据")

        try:
            # 写入Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                data.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=include_index,
                    **kwargs
                )

            return True

        except Exception as e:
            raise RuntimeError(f"写入Excel文件失败: {str(e)}")

    def write_multiple_sheets(
        self,
        data_dict: dict,
        output_path: str,
        include_index: bool = False,
        **kwargs
    ) -> bool:
        """
        写入多个工作表

        Args:
            data_dict: {sheet_name: DataFrame} 字典
            output_path: 输出路径
            include_index: 是否包含索引
            **kwargs: 传递给pandas.to_excel的其他参数

        Returns:
            bool: 是否写入成功
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in data_dict.items():
                    if self.validate_data(df):
                        df.to_excel(
                            writer,
                            sheet_name=sheet_name,
                            index=include_index,
                            **kwargs
                        )

            return True

        except Exception as e:
            raise RuntimeError(f"写入多工作表Excel文件失败: {str(e)}")


# 注册写入器
OutputWriterFactory.register('xlsx', ExcelWriter)
OutputWriterFactory.register('xls', ExcelWriter)
