# 快速开始指南

## Phase 1 完成功能

✅ 已完成的核心功能：
- 批量处理器 (BatchProcessor)
- 流式处理器 (StreamProcessor)
- 任务管理器 (TaskManager)
- 配置管理器 (ConfigManager)
- 进度追踪器 (ProgressTracker)
- CLI工具
- 多种输出格式支持 (Excel, CSV, JSON)

## 安装和配置

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（参考 `.env.example`）：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置你的API密钥
# OPENAI_API_KEY=your-api-key-here
```

或者直接导出环境变量：

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 运行测试

### 测试1：基础架构测试（不需要API密钥）

```bash
# 测试所有模块是否正确导入和工作
python test_simple.py
```

这个测试会验证：
- ✓ 所有模块导入
- ✓ 配置管理器
- ✓ 提示词模板
- ✓ 工厂模式
- ✓ 进度追踪器

### 测试2：创建示例数据

```bash
# 创建测试用的Excel文件
python test_data/create_sample_data.py
```

这会创建以下测试文件：
- `test_data/customer_feedback.xlsx` - 客户反馈数据
- `test_data/products.xlsx` - 商品数据
- `test_data/addresses.xlsx` - 地址数据
- `test_data/simple_test.xlsx` - 简单测试数据

### 测试3：CLI工具测试

#### 查看帮助信息

```bash
python src/cli/main.py --help
```

#### 列出支持的功能

```bash
# 列出支持的LLM提供商
python src/cli/main.py list-providers

# 列出支持的文件格式
python src/cli/main.py list-formats
```

#### 创建配置文件

```bash
# 生成默认配置文件
python src/cli/main.py init-config -o my_config.yaml

# 验证配置文件
python src/cli/main.py validate-config test_data/customer_feedback_config.yaml
```

### 测试4：实际处理文件（需要API密钥）

#### 方式1：使用配置文件

```bash
# 使用预定义的配置文件
python src/cli/main.py process -c test_data/customer_feedback_config.yaml
```

#### 方式2：使用命令行参数

```bash
# 简单文本翻译示例
python src/cli/main.py process \
  -i test_data/simple_test.xlsx \
  -o output/result.xlsx \
  --provider openai \
  --model gpt-3.5-turbo \
  --prompt "请将以下文本翻译成英文: {text}"

# 批量处理模式
python src/cli/main.py process \
  -i test_data/products.xlsx \
  -o output/products_summary.xlsx \
  --mode batch \
  --batch-size 5 \
  --prompt "为以下商品生成简短的营销文案: {product_name} - {description}"
```

## 使用示例

### 示例1：客户反馈情感分析

```bash
python src/cli/main.py process \
  -i test_data/customer_feedback.xlsx \
  -o output/feedback_analysis.xlsx \
  --prompt "分析客户反馈的情感(positive/neutral/negative): {feedback_text}"
```

### 示例2：商品描述优化

```bash
python src/cli/main.py process \
  -i test_data/products.xlsx \
  -o output/products_optimized.xlsx \
  --mode batch \
  --batch-size 3 \
  --prompt "为商品生成SEO友好的描述: {product_name}"
```

### 示例3：地址结构化提取

```bash
python src/cli/main.py process \
  -i test_data/addresses.xlsx \
  -o output/addresses_structured.json \
  --prompt "从地址中提取省市区信息(JSON格式): {address}"
```

## Python API使用

### 示例：完整的处理流程

```python
from src.app import ConfigManager, TaskManager

# 1. 加载配置
config_manager = ConfigManager()
config_manager.load_from_file('test_data/customer_feedback_config.yaml')

# 2. 创建任务管理器
task_manager = TaskManager(config_manager)

# 3. 执行任务（带进度回调）
def progress_callback(progress):
    print(f"进度: {progress.progress_percentage:.1f}%")

result = task_manager.execute(progress_callback=progress_callback)

# 4. 查看结果
print(f"成功: {result['success_count']}")
print(f"失败: {result['failed_count']}")
print(f"Token使用: {result['total_tokens']}")
print(f"预估成本: ${result['estimated_cost']:.4f}")
```

### 示例：直接使用处理器

```python
import pandas as pd
from src.core.llm import OpenAIProvider, PromptTemplate
from src.core.processors import RowProcessor

# 创建数据
df = pd.DataFrame({
    'text': ['你好', '再见', '谢谢']
})

# 创建LLM提供商
llm = OpenAIProvider(
    api_key='your-key',
    model='gpt-3.5-turbo'
)

# 创建提示词模板
template = PromptTemplate(
    template="翻译成英文: {text}",
    system_prompt="你是一个翻译专家"
)

# 创建处理器
processor = RowProcessor(llm, template)

# 处理数据
results = processor.process_dataframe(df)
print(results)
```

## 处理模式说明

### Row模式（逐行处理）

- **适用场景**: 每行需要独立分析
- **优点**: 准确度高，错误隔离
- **缺点**: API调用次数多，成本高

```bash
--mode row
```

### Batch模式（批量处理）

- **适用场景**: 多行数据可以一起处理
- **优点**: API调用次数少，成本低
- **缺点**: 单次失败影响整批

```bash
--mode batch --batch-size 10
```

### Stream模式（流式处理）

- **适用场景**: 大文件，需要实时反馈
- **优点**: 内存效率高，实时输出
- **缺点**: 无法批量优化

```bash
--mode stream
```

## 常见问题

### Q1: ModuleNotFoundError

```bash
# 确保安装了所有依赖
pip install -r requirements.txt
```

### Q2: API密钥错误

```bash
# 检查环境变量是否设置
echo $OPENAI_API_KEY

# 或者在命令行中直接指定
python src/cli/main.py process ... --api-key 'your-key'
```

### Q3: 文件路径问题

```bash
# 使用绝对路径
python src/cli/main.py process -i /absolute/path/to/input.xlsx -o /absolute/path/to/output.xlsx ...

# 或者从项目根目录运行
cd /home/user/Test_drive
python src/cli/main.py process ...
```

### Q4: 编码问题

对于CSV文件，系统会自动检测编码。如果仍有问题：

```yaml
input:
  file: "data.csv"
  encoding: "gbk"  # 或 utf-8, utf-8-sig等
```

## 输出文件说明

处理后的输出文件包含以下列：

- `row_index`: 原始行索引
- `original_data`: 原始数据（可配置）
- `llm_response`: LLM原始响应（可配置）
- `parsed_result`: 解析后的结果
- `status`: 处理状态 (success/failed)
- `error`: 错误信息（如果失败）
- `tokens_used`: Token使用量（可配置）
- `model`: 使用的模型（可配置）

## 性能优化建议

1. **使用批量模式**: 如果数据允许，使用batch模式可以减少70-80%的成本
2. **选择合适的模型**: gpt-3.5-turbo 速度快价格低，gpt-4更准确但更贵
3. **优化提示词**: 简洁的提示词可以减少token使用
4. **设置合理的max_tokens**: 避免浪费token配额

## 下一步

查看以下文档了解更多：

- [完整设计文档](DESIGN.md) - 系统架构详解
- [README](README.md) - 项目概述
- [配置示例](configs/config.example.yaml) - 详细配置说明
- [示例代码](examples/) - 更多使用示例

## 支持

如有问题，请查看：
- [GitHub Issues](https://github.com/yourusername/llm-excel-processor/issues)
- [设计文档](DESIGN.md)
