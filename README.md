# LLM Excel Processor

基于大语言模型的Excel文档智能处理工具，支持多种文档格式和LLM提供商。

## 功能特性

- 📄 **多格式支持**: xlsx, xls, csv, txt, pdf
- 🤖 **多LLM集成**: OpenAI GPT, Claude, 通义千问等
- ⚡ **灵活处理**: 单行、批量、流式处理模式
- 🎯 **提示词模板**: 支持变量替换和few-shot示例
- 📊 **结果导出**: 多种格式输出（Excel, CSV, JSON）
- 🔄 **错误重试**: 智能重试和断点续传
- 📈 **进度追踪**: 实时处理进度和成本统计

## 系统架构

```
┌─────────────────────────────────────────┐
│           前端层 (Frontend)              │
│    Web界面 / CLI工具 / API接口          │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         应用层 (Application)             │
│  任务管理 / 配置管理 / 进度跟踪          │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          核心处理层 (Core)               │
│  文档解析 / LLM处理 / 结果输出          │
└─────────────────────────────────────────┘
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

```python
from llm_excel_processor import ExcelProcessor, OpenAIProvider, PromptTemplate

# 1. 初始化LLM提供商
llm_provider = OpenAIProvider(
    api_key="your-api-key",
    model="gpt-4",
    temperature=0.3
)

# 2. 定义提示词模板
template = PromptTemplate(
    template="分析以下客户反馈: {feedback}，返回情感分类（正面/中性/负面）",
    output_format="json",
    system_prompt="你是一个专业的情感分析专家"
)

# 3. 创建处理器
processor = ExcelProcessor(
    llm_provider=llm_provider,
    mode="row"  # 单行处理模式
)

# 4. 处理文件
result = processor.process_file(
    input_file="customer_feedback.xlsx",
    output_file="analysis_result.xlsx",
    prompt_template=template,
    columns=["feedback"]  # 要处理的列
)

print(f"处理完成: {result.total_rows} 行")
print(f"成功: {result.success_count} 行")
print(f"失败: {result.failed_count} 行")
print(f"Token使用: {result.total_tokens}")
```

### CLI使用

```bash
# 基础命令
llm-excel-processor process \
  --input data.xlsx \
  --output result.xlsx \
  --config config.yaml

# 指定LLM提供商
llm-excel-processor process \
  --input data.xlsx \
  --provider openai \
  --model gpt-4 \
  --prompt "分析: {text}"

# 批量处理模式
llm-excel-processor process \
  --input large_file.xlsx \
  --mode batch \
  --batch-size 10
```

## 配置文件

### 任务配置示例 (config.yaml)

```yaml
task:
  name: "客户反馈情感分析"
  description: "分析客户反馈的情感倾向"

input:
  file: "customer_feedback.xlsx"
  sheet: "Sheet1"
  encoding: "utf-8"

processing:
  mode: "row"  # row, batch, stream
  batch_size: 10
  columns:
    - "feedback_text"
    - "customer_name"

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.3
  max_tokens: 500

  prompt_template: |
    分析以下客户反馈的情感倾向：

    客户姓名: {customer_name}
    反馈内容: {feedback_text}

    请返回JSON格式结果：
    {
      "sentiment": "积极/中性/消极",
      "key_issues": ["问题1", "问题2"],
      "urgency": "高/中/低"
    }

output:
  file: "feedback_analysis.xlsx"
  format: "xlsx"
```

## 核心模块

### 1. 文档解析模块

支持多种文件格式的解析：

```python
from llm_excel_processor.parsers import ParserFactory

# 自动选择合适的解析器
parser = ParserFactory.create("data.xlsx")
document = parser.parse("data.xlsx")

print(f"总行数: {document.total_rows}")
print(f"列名: {document.column_names}")
```

### 2. LLM集成模块

支持多种LLM提供商：

```python
from llm_excel_processor.llm import LLMProviderFactory

# OpenAI
openai_provider = LLMProviderFactory.create(
    provider_name="openai",
    api_key="your-key",
    model="gpt-4"
)

# 生成文本
response = openai_provider.generate("你好，请介绍一下自己")
print(response.content)
```

### 3. 提示词模板

创建可复用的提示词模板：

```python
from llm_excel_processor.llm import PromptTemplate

template = PromptTemplate(
    template="翻译以下文本到{target_language}: {text}",
    system_prompt="你是一个专业的翻译专家",
    variables=["target_language", "text"]
)

# 添加示例
template.add_example(
    input_data={"target_language": "英语", "text": "你好"},
    output="Hello"
)

# 渲染提示词
prompt = template.render({
    "target_language": "法语",
    "text": "早上好"
})
```

## 处理模式

### 单行处理模式

逐行处理，适合复杂分析：

```python
processor = RowProcessor(llm_provider, prompt_template)
results = processor.process_dataframe(df)
```

### 批量处理模式

多行一次性处理，降低成本：

```python
processor = BatchProcessor(llm_provider, prompt_template, batch_size=10)
results = processor.process_dataframe(df)
```

### 流式处理模式

边处理边输出，适合大文件：

```python
processor = StreamProcessor(llm_provider, prompt_template)
for result in processor.process_stream(df):
    print(result)
```

## 目录结构

```
llm-excel-processor/
├── src/
│   ├── core/              # 核心模块
│   │   ├── parsers/       # 文档解析器
│   │   ├── llm/           # LLM集成
│   │   ├── processors/    # 数据处理器
│   │   └── output/        # 结果输出
│   ├── app/               # 应用层
│   ├── api/               # API服务
│   └── cli/               # 命令行工具
├── tests/                 # 测试
├── configs/               # 配置文件
├── examples/              # 使用示例
└── docs/                  # 文档
```

## 环境变量

创建 `.env` 文件：

```env
# OpenAI
OPENAI_API_KEY=your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1

# Claude
ANTHROPIC_API_KEY=your-claude-key

# 通义千问
QWEN_API_KEY=your-qwen-key

# 文件配置
MAX_FILE_SIZE=100  # MB
TEMP_DIR=/tmp/llm-excel-processor
```

## 高级功能

### 错误处理和重试

```python
from llm_excel_processor.utils import RetryStrategy

retry_strategy = RetryStrategy(
    max_attempts=3,
    backoff_factor=2,
    timeout=30
)

processor.set_retry_strategy(retry_strategy)
```

### 进度追踪

```python
def progress_callback(current, total):
    percentage = (current / total) * 100
    print(f"进度: {percentage:.2f}% ({current}/{total})")

processor.process_file(
    input_file="data.xlsx",
    output_file="result.xlsx",
    progress_callback=progress_callback
)
```

### 结果过滤

```python
# 只处理满足条件的行
processor.process_file(
    input_file="data.xlsx",
    filter_condition=lambda row: row['status'] == 'pending'
)
```

## API服务

启动API服务器：

```bash
python -m llm_excel_processor.api
```

API端点：

```bash
# 创建任务
POST /api/tasks
Content-Type: multipart/form-data

# 查询进度
GET /api/tasks/{task_id}

# 下载结果
GET /api/tasks/{task_id}/download

# 取消任务
DELETE /api/tasks/{task_id}
```

## 性能优化

- 批量处理可减少API调用次数
- 使用缓存避免重复处理
- 异步处理提高并发能力
- 合理设置batch_size和并发数

## 成本控制

```python
# 统计token使用
result = processor.process_file(...)
print(f"Token使用: {result.total_tokens}")
print(f"预估成本: ${result.estimated_cost}")

# 设置token限制
processor.set_token_limit(max_tokens=100000)
```

## 常见问题

### Q: 如何处理中文编码问题？

A: CSV解析器会自动检测编码，也可以手动指定：

```python
parser.parse("data.csv", encoding="gbk")
```

### Q: 如何处理大文件？

A: 使用流式处理模式或分批处理：

```python
processor = StreamProcessor(llm_provider, prompt_template)
```

### Q: 如何自定义结果解析？

A: 提供自定义解析函数：

```python
def custom_parser(response: str) -> dict:
    # 自定义解析逻辑
    return {"result": response.strip()}

processor = RowProcessor(
    llm_provider,
    prompt_template,
    result_parser=custom_parser
)
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- 项目主页: https://github.com/yourusername/llm-excel-processor
- 问题反馈: https://github.com/yourusername/llm-excel-processor/issues

## 相关文档

- [完整设计文档](DESIGN.md)
- [API文档](docs/API.md)
- [开发指南](docs/DEVELOPMENT.md)
- [用户手册](docs/USER_GUIDE.md)
