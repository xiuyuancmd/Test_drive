#!/usr/bin/env python3
"""
Gemini提供商测试脚本
测试Google Gemini 1.5 Flash的集成
"""
import os
import sys

# 添加src到路径
sys.path.insert(0, os.path.dirname(__file__))

print("="*60)
print("Google Gemini 集成测试")
print("="*60)

# 1. 检查API密钥
print("\n1. 检查API密钥...")
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ 未设置GEMINI_API_KEY环境变量")
    print("\n请设置API密钥:")
    print("  export GEMINI_API_KEY='your-api-key-here'")
    print("\n如何获取Gemini API密钥:")
    print("  1. 访问 https://makersuite.google.com/app/apikey")
    print("  2. 创建API密钥")
    print("  3. 复制密钥并设置环境变量")
    sys.exit(1)
else:
    print(f"✓ API密钥已设置: {api_key[:20]}...")

# 2. 测试导入
print("\n2. 测试模块导入...")
try:
    from src.core.llm import GeminiProvider, PromptTemplate
    print("✓ Gemini提供商导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    print("\n请安装依赖:")
    print("  pip install google-generativeai")
    sys.exit(1)

# 3. 测试基础连接
print("\n3. 测试基础连接...")
try:
    gemini = GeminiProvider(
        api_key=api_key,
        model="gemini-1.5-flash",
        temperature=0.7
    )
    print("✓ Gemini提供商初始化成功")
    print(f"  模型: {gemini.model}")
    print(f"  温度: {gemini.temperature}")
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    sys.exit(1)

# 4. 测试简单调用
print("\n4. 测试简单API调用...")
try:
    response = gemini.generate("请说'你好，世界'")
    print("✓ API调用成功")
    print(f"  响应: {response.content}")
    print(f"  模型: {response.model}")
    print(f"  Token: {response.tokens_used}")
except Exception as e:
    print(f"❌ API调用失败: {e}")
    print("\n可能的原因:")
    print("  1. API密钥无效")
    print("  2. 网络连接问题")
    print("  3. Gemini服务不可用")
    sys.exit(1)

# 5. 测试中文翻译
print("\n5. 测试中文翻译...")
try:
    template = PromptTemplate(
        template="请将以下中文翻译成英文: {text}",
        system_prompt="你是一个专业的翻译助手"
    )

    test_text = "今天天气真好"
    prompt = template.render({"text": test_text})
    response = gemini.generate(prompt, system_prompt=template.system_prompt)

    print("✓ 翻译测试成功")
    print(f"  原文: {test_text}")
    print(f"  译文: {response.content}")
    print(f"  Token使用: {response.tokens_used}")
except Exception as e:
    print(f"❌ 翻译测试失败: {e}")

# 6. 测试流式生成
print("\n6. 测试流式生成...")
try:
    print("  生成内容: ", end='', flush=True)
    full_text = ""
    for chunk in gemini.generate_stream("用一句话介绍人工智能"):
        print(chunk, end='', flush=True)
        full_text += chunk
    print("\n✓ 流式生成成功")
except Exception as e:
    print(f"\n❌ 流式生成失败: {e}")

# 7. 测试JSON输出
print("\n7. 测试JSON格式输出...")
try:
    prompt = """
    请分析以下文本的情感，用JSON格式返回：

    文本: "这个产品非常好用，我很满意！"

    返回格式:
    {
      "sentiment": "positive/neutral/negative",
      "confidence": 0.0-1.0
    }
    """

    response = gemini.generate(prompt)
    print("✓ JSON输出测试成功")
    print(f"  响应: {response.content}")
except Exception as e:
    print(f"❌ JSON输出测试失败: {e}")

# 8. 测试工厂模式
print("\n8. 测试工厂模式...")
try:
    from src.core.llm import LLMProviderFactory

    gemini_from_factory = LLMProviderFactory.create(
        provider_name="gemini",
        api_key=api_key,
        model="gemini-1.5-flash"
    )

    response = gemini_from_factory.generate("测试工厂模式")
    print("✓ 工厂模式测试成功")
    print(f"  响应: {response.content[:50]}...")
except Exception as e:
    print(f"❌ 工厂模式测试失败: {e}")

# 9. 测试完整处理流程
print("\n9. 测试完整处理流程...")
try:
    import pandas as pd
    from src.core.processors import RowProcessor

    # 创建测试数据
    df = pd.DataFrame({
        'text': ['你好', '再见', '谢谢']
    })

    # 创建处理器
    template = PromptTemplate(
        template="翻译成英文: {text}",
        system_prompt="你是翻译专家"
    )

    processor = RowProcessor(gemini, template)

    # 处理数据
    results = processor.process_dataframe(df)

    print("✓ 完整处理流程测试成功")
    print(f"  处理行数: {len(results)}")
    print(f"  成功数: {len(results[results['status'] == 'success'])}")
    print(f"  总Token: {results['tokens_used'].sum()}")

    print("\n  处理结果:")
    for idx, row in results.iterrows():
        print(f"    {row['original_data']['text']} -> {row['parsed_result']}")

except Exception as e:
    print(f"❌ 完整流程测试失败: {e}")
    import traceback
    traceback.print_exc()

# 总结
print("\n" + "="*60)
print("✅ Gemini集成测试完成！")
print("="*60)
print("\n下一步:")
print("1. 使用CLI测试:")
print("   python src/cli/main.py process -c test_data/gemini_test_config.yaml")
print("\n2. 批量处理测试:")
print("   python src/cli/main.py process -c test_data/gemini_batch_config.yaml")
print("\n3. 命令行参数测试:")
print("   python src/cli/main.py process \\")
print("     -i test_data/simple_test.xlsx \\")
print("     -o output/gemini_result.xlsx \\")
print("     --provider gemini \\")
print("     --model gemini-1.5-flash \\")
print("     --prompt '翻译: {text}'")
print("\nGemini 1.5 Flash特点:")
print("  - 速度快（比GPT-3.5 Turbo更快）")
print("  - 成本低（比GPT系列便宜很多）")
print("  - 支持100万token上下文")
print("  - 多模态支持（文本、图像、视频）")
print("  - 免费额度：15 RPM (requests per minute)")
