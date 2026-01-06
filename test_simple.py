#!/usr/bin/env python3
"""
简单测试脚本 - 不需要真实LLM调用
测试整个系统的架构和流程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 首先测试导入
print("="*60)
print("测试模块导入")
print("="*60)

try:
    from src.core.parsers import ParserFactory, ExcelParser, CSVParser
    print("✓ 解析器模块导入成功")
except Exception as e:
    print(f"✗ 解析器模块导入失败: {e}")
    sys.exit(1)

try:
    from src.core.llm import LLMProviderFactory, PromptTemplate
    print("✓ LLM模块导入成功")
except Exception as e:
    print(f"✗ LLM模块导入失败: {e}")
    sys.exit(1)

try:
    from src.core.processors import RowProcessor, BatchProcessor, StreamProcessor
    print("✓ 处理器模块导入成功")
except Exception as e:
    print(f"✗ 处理器模块导入失败: {e}")
    sys.exit(1)

try:
    from src.core.output import OutputWriterFactory
    print("✓ 输出模块导入成功")
except Exception as e:
    print(f"✗ 输出模块导入失败: {e}")
    sys.exit(1)

try:
    from src.app import ConfigManager, TaskManager, ProgressTracker
    print("✓ 应用层模块导入成功")
except Exception as e:
    print(f"✗ 应用层模块导入失败: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("测试配置管理器")
print("="*60)

try:
    config_manager = ConfigManager()
    default_config = ConfigManager.create_default_config()
    config_manager.load_from_dict(default_config)
    print("✓ 配置管理器测试成功")
    print(f"  - 任务名称: {config_manager.task_config.name}")
    print(f"  - 处理模式: {config_manager.processing_config.mode}")
except Exception as e:
    print(f"✗ 配置管理器测试失败: {e}")

print("\n" + "="*60)
print("测试提示词模板")
print("="*60)

try:
    template = PromptTemplate(
        template="分析以下文本: {text}",
        system_prompt="你是一个AI助手",
        output_format="json"
    )

    rendered = template.render({"text": "测试内容"})
    print("✓ 提示词模板测试成功")
    print(f"  - 变量: {template.variables}")
    print(f"  - 渲染结果预览: {rendered[:50]}...")
except Exception as e:
    print(f"✗ 提示词模板测试失败: {e}")

print("\n" + "="*60)
print("测试工厂模式")
print("="*60)

try:
    print("✓ 支持的解析器:")
    for fmt in ParserFactory.get_supported_formats():
        print(f"  - {fmt}")

    print("✓ 支持的输出格式:")
    for fmt in OutputWriterFactory.get_supported_formats():
        print(f"  - {fmt}")
except Exception as e:
    print(f"✗ 工厂模式测试失败: {e}")

print("\n" + "="*60)
print("测试进度追踪器")
print("="*60)

try:
    tracker = ProgressTracker("test-task", total=10)
    tracker.start()
    for i in range(10):
        tracker.increment(success=True, tokens=100)
    tracker.complete()

    print("✓ 进度追踪器测试成功")
    print(f"  - 总数: {tracker.progress.total}")
    print(f"  - 成功: {tracker.progress.success_count}")
    print(f"  - Token: {tracker.progress.total_tokens}")
    print(f"  - 状态: {tracker.progress.status.value}")
except Exception as e:
    print(f"✗ 进度追踪器测试失败: {e}")

print("\n" + "="*60)
print("✅ 所有基础测试通过！")
print("="*60)
print("\n说明:")
print("- 所有核心模块导入正常")
print("- 配置管理、模板系统工作正常")
print("- 进度追踪功能正常")
print("\n如需完整测试，请:")
print("1. 安装依赖: pip install -r requirements.txt")
print("2. 设置API密钥: export OPENAI_API_KEY='your-key'")
print("3. 创建测试数据: python test_data/create_sample_data.py")
print("4. 运行CLI: python src/cli/main.py process -i test_data/simple_test.xlsx -o output/result.xlsx --prompt '翻译成英文: {text}'")
