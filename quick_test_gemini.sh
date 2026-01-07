#!/bin/bash
# 一键测试脚本 - 用于快速验证Gemini集成

echo "=========================================="
echo "LLM Excel Processor - Gemini 快速测试"
echo "=========================================="

# 1. 检查Python版本
echo ""
echo "1. 检查Python版本..."
python --version || python3 --version

# 2. 安装依赖
echo ""
echo "2. 安装依赖包（这可能需要几分钟）..."
pip install pandas openpyxl google-generativeai pyyaml click || {
    echo "❌ 依赖安装失败，尝试使用pip3..."
    pip3 install pandas openpyxl google-generativeai pyyaml click
}

# 3. 创建测试数据
echo ""
echo "3. 创建测试数据..."
python test_data/create_sample_data.py || python3 test_data/create_sample_data.py

# 4. 检查API密钥
echo ""
echo "4. 检查Gemini API密钥..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ 未设置GEMINI_API_KEY环境变量"
    echo ""
    echo "请按以下步骤操作："
    echo "  1. 访问 https://makersuite.google.com/app/apikey"
    echo "  2. 用Google账号登录"
    echo "  3. 点击 'Create API Key'"
    echo "  4. 复制密钥"
    echo "  5. 运行: export GEMINI_API_KEY='你的密钥'"
    echo ""
    echo "然后重新运行此脚本: ./quick_test_gemini.sh"
    exit 1
else
    echo "✓ API密钥已设置: ${GEMINI_API_KEY:0:20}..."
fi

# 5. 运行Gemini基础测试
echo ""
echo "5. 运行Gemini基础测试..."
python test_gemini.py || python3 test_gemini.py

# 6. 运行CLI测试
echo ""
echo "=========================================="
echo "6. 运行CLI实际数据处理测试"
echo "=========================================="
echo ""
echo "测试命令："
echo "python src/cli/main.py process \\"
echo "  -i test_data/simple_test.xlsx \\"
echo "  -o output/gemini_quick_test.xlsx \\"
echo "  --provider gemini \\"
echo "  --model gemini-1.5-flash \\"
echo "  --prompt '翻译成英文: {text}'"
echo ""

python src/cli/main.py process \
  -i test_data/simple_test.xlsx \
  -o output/gemini_quick_test.xlsx \
  --provider gemini \
  --model gemini-1.5-flash \
  --prompt "翻译成英文: {text}" || python3 src/cli/main.py process \
  -i test_data/simple_test.xlsx \
  -o output/gemini_quick_test.xlsx \
  --provider gemini \
  --model gemini-1.5-flash \
  --prompt "翻译成英文: {text}"

# 7. 检查结果
echo ""
echo "=========================================="
echo "7. 查看处理结果"
echo "=========================================="

if [ -f "output/gemini_quick_test.xlsx" ]; then
    echo "✅ 测试成功！"
    echo ""
    echo "结果文件: output/gemini_quick_test.xlsx"
    echo "文件大小: $(ls -lh output/gemini_quick_test.xlsx | awk '{print $5}')"
    echo ""
    echo "下一步："
    echo "  1. 用Excel打开结果文件查看"
    echo "  2. 尝试处理自己的数据"
    echo "  3. 查看文档: cat RUN_GEMINI_TEST.md"
else
    echo "❌ 未找到结果文件"
    echo "请检查上面的错误信息"
fi

echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
