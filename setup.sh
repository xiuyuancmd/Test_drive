#!/bin/bash
# LLM Excel Processor 安装脚本

echo "======================================"
echo "LLM Excel Processor - 安装脚本"
echo "======================================"

# 检查Python版本
echo ""
echo "1. 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python版本: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "   ❌ 未找到Python3，请先安装Python 3.9+"
    exit 1
fi

# 安装依赖
echo ""
echo "2. 安装Python依赖..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "   ✓ 依赖安装成功"
else
    echo "   ❌ 依赖安装失败"
    exit 1
fi

# 创建必要的目录
echo ""
echo "3. 创建目录结构..."
mkdir -p test_data output logs .cache

echo "   ✓ 目录创建完成"

# 创建环境变量文件
echo ""
echo "4. 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   ✓ 已创建 .env 文件"
    echo "   ⚠️  请编辑 .env 文件，设置你的API密钥"
else
    echo "   ℹ️  .env 文件已存在"
fi

# 创建测试数据
echo ""
echo "5. 创建测试数据..."
python3 test_data/create_sample_data.py

if [ $? -eq 0 ]; then
    echo "   ✓ 测试数据创建完成"
else
    echo "   ⚠️  测试数据创建失败（这不影响使用）"
fi

# 运行基础测试
echo ""
echo "6. 运行基础测试..."
python3 test_simple.py

echo ""
echo "======================================"
echo "✅ 安装完成！"
echo "======================================"
echo ""
echo "下一步:"
echo "1. 编辑 .env 文件，设置 OPENAI_API_KEY"
echo "2. 运行测试: python3 src/cli/main.py --help"
echo "3. 查看快速开始: cat QUICKSTART.md"
echo ""
