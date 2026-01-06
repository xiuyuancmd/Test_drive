"""
基础使用示例
演示如何使用LLM Excel Processor进行简单的数据处理
"""
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.parsers import ParserFactory, ExcelParser
from src.core.llm import OpenAIProvider, PromptTemplate
from src.core.processors.row_processor import RowProcessor


def example_1_parse_excel():
    """示例1: 解析Excel文件"""
    print("=== 示例1: 解析Excel文件 ===\n")

    # 创建解析器
    parser = ExcelParser()

    # 假设我们有一个测试文件
    file_path = "sample_data.xlsx"

    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        print("请先创建一个示例Excel文件")
        return

    # 解析文件
    document = parser.parse(file_path)

    print(f"文件名: {document.metadata['file_name']}")
    print(f"总行数: {document.total_rows}")
    print(f"列名: {document.column_names}")
    print(f"\n前5行数据:")
    print(document.data.head())


def example_2_sentiment_analysis():
    """示例2: 情感分析"""
    print("\n=== 示例2: 客户反馈情感分析 ===\n")

    # 1. 设置OpenAI API Key (从环境变量读取)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置环境变量 OPENAI_API_KEY")
        return

    # 2. 创建LLM提供商
    llm_provider = OpenAIProvider(
        api_key=api_key,
        model="gpt-3.5-turbo",  # 使用更便宜的模型做演示
        temperature=0.3,
        max_tokens=200
    )

    # 3. 创建提示词模板
    template = PromptTemplate(
        template="""
分析以下客户反馈的情感倾向：

反馈内容: {feedback}

请返回JSON格式结果：
{{
  "sentiment": "positive/neutral/negative",
  "confidence": 0.95,
  "summary": "简短总结"
}}
""",
        system_prompt="你是一个专业的情感分析专家，擅长分析客户反馈。",
        output_format="json"
    )

    # 4. 创建处理器
    processor = RowProcessor(
        llm_provider=llm_provider,
        prompt_template=template
    )

    # 5. 创建示例数据
    import pandas as pd

    sample_data = pd.DataFrame({
        'feedback': [
            '产品质量很好，非常满意！',
            '物流太慢了，等了一个星期',
            '还可以，没什么特别的'
        ]
    })

    # 6. 处理数据
    print("开始处理数据...\n")

    def progress_callback(current, total):
        print(f"进度: {current}/{total} ({current/total*100:.1f}%)")

    results = processor.process_dataframe(
        sample_data,
        progress_callback=progress_callback
    )

    # 7. 显示结果
    print("\n处理结果:")
    for idx, result in results.iterrows():
        print(f"\n--- 数据 {idx + 1} ---")
        print(f"原始反馈: {result['original_data']['feedback']}")
        print(f"LLM分析: {result['parsed_result']}")
        print(f"状态: {result['status']}")
        if result['error']:
            print(f"错误: {result['error']}")


def example_3_data_extraction():
    """示例3: 数据提取和标准化"""
    print("\n=== 示例3: 地址信息提取 ===\n")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置环境变量 OPENAI_API_KEY")
        return

    # 创建LLM提供商
    llm_provider = OpenAIProvider(
        api_key=api_key,
        model="gpt-3.5-turbo",
        temperature=0.1  # 降低温度以获得更确定的结果
    )

    # 创建提示词模板
    template = PromptTemplate(
        template="""
从以下地址中提取结构化信息：

地址: {address}

请返回JSON格式：
{{
  "province": "省份",
  "city": "城市",
  "district": "区县",
  "street": "街道",
  "postal_code": "邮编"
}}
""",
        system_prompt="你是一个地址解析专家，擅长从非结构化地址中提取结构化信息。"
    )

    # 添加few-shot示例
    template.add_example(
        input_data={"address": "北京市朝阳区建国路88号"},
        output='{"province": "北京市", "city": "北京市", "district": "朝阳区", "street": "建国路88号", "postal_code": ""}'
    )

    # 创建处理器
    processor = RowProcessor(llm_provider, template)

    # 示例数据
    import pandas as pd

    sample_data = pd.DataFrame({
        'address': [
            '上海市浦东新区世纪大道1000号',
            '广东省深圳市南山区科技园',
            '浙江省杭州市西湖区文三路100号'
        ]
    })

    # 处理
    print("开始提取地址信息...\n")
    results = processor.process_dataframe(sample_data)

    # 显示结果
    print("\n提取结果:")
    for idx, result in results.iterrows():
        print(f"\n--- 地址 {idx + 1} ---")
        print(f"原始: {result['original_data']['address']}")
        print(f"提取: {result['parsed_result']}")


def example_4_using_factory():
    """示例4: 使用工厂模式"""
    print("\n=== 示例4: 使用工厂模式自动选择解析器 ===\n")

    # 自动选择合适的解析器
    test_files = [
        "data.xlsx",
        "data.csv",
        "data.pdf"
    ]

    for file_path in test_files:
        try:
            # 工厂会根据文件扩展名自动选择解析器
            parser = ParserFactory.create(file_path)
            print(f"文件 {file_path} 使用解析器: {parser.__class__.__name__}")
        except ValueError as e:
            print(f"文件 {file_path}: {e}")

    print("\n支持的格式:")
    print(ParserFactory.get_supported_formats())


def main():
    """运行所有示例"""
    print("LLM Excel Processor - 使用示例\n")
    print("=" * 50)

    # 示例1: 解析Excel
    try:
        example_1_parse_excel()
    except Exception as e:
        print(f"示例1出错: {e}")

    # 示例2: 情感分析
    try:
        example_2_sentiment_analysis()
    except Exception as e:
        print(f"示例2出错: {e}")

    # 示例3: 数据提取
    try:
        example_3_data_extraction()
    except Exception as e:
        print(f"示例3出错: {e}")

    # 示例4: 工厂模式
    try:
        example_4_using_factory()
    except Exception as e:
        print(f"示例4出错: {e}")


if __name__ == "__main__":
    main()
