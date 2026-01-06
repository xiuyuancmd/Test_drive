# LLM Excel Processor 系统设计文档

## 1. 系统概述

LLM Excel Processor 是一个基于大语言模型的文档处理工具，能够读取多种格式的表格文档，利用大语言模型逐行处理数据，并输出处理结果。

### 1.1 核心功能
- 支持多种文档格式解析（xlsx, xls, csv, txt, pdf）
- 灵活的LLM集成（支持多种LLM提供商）
- 逐行/批量数据处理
- 可配置的处理规则和提示词模板
- 结果输出和导出
- 处理进度跟踪和错误处理

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                      前端层 (Frontend)                    │
│  - Web界面 / CLI工具 / API接口                            │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   应用层 (Application)                    │
│  - 任务管理器 (Task Manager)                              │
│  - 配置管理器 (Config Manager)                            │
│  - 进度跟踪器 (Progress Tracker)                          │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   核心处理层 (Core)                       │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 文档解析器    │  │ LLM处理器     │  │ 结果处理器    │  │
│  │ Parser       │  │ LLM Processor │  │ Output       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   基础设施层 (Infrastructure)             │
│  - 文件存储 (File Storage)                                │
│  - 缓存系统 (Cache)                                       │
│  - 日志系统 (Logging)                                     │
│  - 数据库 (Database - Optional)                           │
└───────────────────────────────────────────────────────────┘
```

---

## 3. 核心模块设计

### 3.1 文档解析模块 (Parser Module)

#### 3.1.1 文件解析器接口
```python
class BaseParser:
    """文档解析器基类"""
    def parse(self, file_path: str) -> DataFrame
    def validate(self, file_path: str) -> bool
    def get_metadata(self, file_path: str) -> dict
```

#### 3.1.2 具体解析器实现

**Excel解析器 (xlsx/xls)**
- 库：`openpyxl` (xlsx), `xlrd` (xls)
- 功能：
  - 多sheet支持
  - 单元格格式识别
  - 公式值提取
  - 合并单元格处理

**CSV解析器**
- 库：`pandas`, `csv`
- 功能：
  - 自动编码检测（UTF-8, GBK等）
  - 分隔符自动识别
  - 引号处理

**TXT解析器**
- 库：`pandas`
- 功能：
  - 固定宽度格式支持
  - 分隔符配置
  - 正则表达式解析

**PDF解析器**
- 库：`pdfplumber`, `tabula-py`
- 功能：
  - 表格区域识别
  - 多页表格合并
  - OCR支持（可选）

#### 3.1.3 统一数据结构
```python
@dataclass
class ParsedDocument:
    data: pd.DataFrame          # 解析后的数据
    metadata: dict              # 文件元信息
    sheet_name: str            # 工作表名称
    total_rows: int            # 总行数
    column_names: List[str]    # 列名
    file_format: str           # 文件格式
```

---

### 3.2 LLM处理模块 (LLM Processor Module)

#### 3.2.1 LLM提供商抽象
```python
class BaseLLMProvider:
    """LLM提供商基类"""
    def generate(self, prompt: str, **kwargs) -> str
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]
    def get_token_count(self, text: str) -> int
```

#### 3.2.2 支持的LLM提供商
- OpenAI (GPT-3.5, GPT-4)
- Anthropic Claude
- 阿里云通义千问
- 百度文心一言
- 本地部署模型（Ollama, vLLM）
- Azure OpenAI

#### 3.2.3 处理模式

**单行处理模式**
```python
def process_row(row: pd.Series, prompt_template: str) -> dict:
    """
    逐行处理，每行数据单独调用LLM
    适用场景：复杂推理、需要详细分析每行
    """
    pass
```

**批量处理模式**
```python
def process_batch(rows: pd.DataFrame, prompt_template: str, batch_size: int) -> List[dict]:
    """
    批量处理，多行数据一次调用LLM
    适用场景：简单分类、格式转换、降低成本
    """
    pass
```

**流式处理模式**
```python
def process_stream(rows: pd.DataFrame, prompt_template: str) -> Generator:
    """
    流式处理，边处理边返回结果
    适用场景：大文件处理、实时反馈
    """
    pass
```

#### 3.2.4 提示词模板系统
```python
class PromptTemplate:
    """提示词模板管理"""
    template: str
    variables: List[str]
    system_prompt: str
    few_shot_examples: List[dict]

    def render(self, row_data: dict) -> str:
        """渲染提示词"""
        pass
```

---

### 3.3 任务管理模块 (Task Manager)

#### 3.3.1 任务配置
```python
@dataclass
class ProcessingTask:
    task_id: str
    input_file: str
    output_file: str
    file_format: str

    # 处理配置
    processing_mode: str  # 'row', 'batch', 'stream'
    batch_size: int

    # LLM配置
    llm_provider: str
    model_name: str
    prompt_template: PromptTemplate
    temperature: float
    max_tokens: int

    # 高级配置
    column_mapping: dict  # 列名映射
    filter_conditions: dict  # 数据过滤条件
    output_columns: List[str]  # 输出列
    retry_strategy: dict  # 重试策略

    # 进度追踪
    status: str  # 'pending', 'processing', 'completed', 'failed'
    progress: float
    created_at: datetime
    updated_at: datetime
```

#### 3.3.2 任务执行器
```python
class TaskExecutor:
    """任务执行器"""
    def execute(self, task: ProcessingTask) -> TaskResult
    def pause(self, task_id: str)
    def resume(self, task_id: str)
    def cancel(self, task_id: str)
```

---

### 3.4 结果输出模块 (Output Module)

#### 3.4.1 输出格式
- Excel (xlsx)
- CSV
- JSON
- 数据库（PostgreSQL, MySQL等）
- API推送

#### 3.4.2 结果结构
```python
@dataclass
class ProcessingResult:
    original_data: dict         # 原始数据
    llm_response: str          # LLM原始响应
    parsed_result: dict        # 解析后的结果
    confidence: float          # 置信度（可选）
    processing_time: float     # 处理耗时
    error: Optional[str]       # 错误信息
    metadata: dict             # 额外元数据
```

---

## 4. 技术栈选型

### 4.1 后端技术栈
- **语言**: Python 3.9+
- **Web框架**: FastAPI（API服务）/ Flask（轻量级）
- **文档解析**:
  - Excel: `openpyxl`, `xlrd`, `pandas`
  - CSV: `pandas`, `chardet`
  - PDF: `pdfplumber`, `tabula-py`, `PyPDF2`
- **LLM集成**:
  - `openai`
  - `anthropic`
  - `langchain` (可选，用于复杂场景)
- **数据处理**: `pandas`, `numpy`
- **任务队列**: `Celery` + `Redis`（可选，用于异步处理）
- **数据库**: `SQLite`（轻量）/ `PostgreSQL`（生产）
- **配置管理**: `pydantic`, `python-dotenv`

### 4.2 前端技术栈（可选）
- **框架**: React / Vue.js
- **UI组件**: Ant Design / Element Plus
- **状态管理**: Redux / Pinia
- **文件上传**: react-dropzone / vue-upload-component

---

## 5. 关键流程设计

### 5.1 文档处理流程

```
上传文件
   ↓
文件验证（格式、大小、完整性）
   ↓
选择解析器（基于文件格式）
   ↓
解析文档 → 生成DataFrame
   ↓
配置处理任务（提示词、LLM参数）
   ↓
数据预处理（过滤、转换、验证）
   ↓
分批/逐行调用LLM处理
   ↓
结果解析和验证
   ↓
结果聚合和后处理
   ↓
导出结果文件
   ↓
清理临时文件
```

### 5.2 错误处理和重试机制

**错误类型**:
1. 文件解析错误
2. LLM API错误（限流、超时、配额）
3. 数据验证错误
4. 网络错误

**重试策略**:
- 指数退避重试
- 限流感知（429错误）
- 断点续传（大文件处理中断后继续）

---

## 6. 非功能需求

### 6.1 性能要求
- 支持处理10万行以内的文档
- 单行处理延迟 < LLM响应时间 + 100ms
- 并发处理能力：10个任务同时执行

### 6.2 安全性
- 文件上传大小限制（默认100MB）
- 文件类型白名单验证
- API密钥安全存储（环境变量/密钥管理服务）
- 临时文件自动清理

### 6.3 可扩展性
- 插件化解析器设计
- 多LLM提供商支持
- 自定义后处理函数
- Webhook通知支持

### 6.4 可观测性
- 详细日志记录（结构化日志）
- 处理进度实时追踪
- 成本统计（Token使用量）
- 性能监控（处理速度、成功率）

---

## 7. 配置文件示例

### 7.1 任务配置示例 (config.yaml)
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
  filter:
    column: "status"
    value: "pending"

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.3
  max_tokens: 500

  prompt_template: |
    分析以下客户反馈的情感倾向（积极/中性/消极），并提取关键问题：

    客户姓名: {customer_name}
    反馈内容: {feedback_text}

    请以JSON格式返回结果：
    {
      "sentiment": "积极/中性/消极",
      "key_issues": ["问题1", "问题2"],
      "urgency": "高/中/低"
    }

output:
  file: "feedback_analysis_result.xlsx"
  format: "xlsx"
  columns:
    - "customer_name"
    - "feedback_text"
    - "sentiment"
    - "key_issues"
    - "urgency"

retry:
  max_attempts: 3
  backoff_factor: 2
  timeout: 30
```

---

## 8. 项目目录结构

```
llm-excel-processor/
├── src/
│   ├── core/
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # 基础解析器接口
│   │   │   ├── excel_parser.py   # Excel解析器
│   │   │   ├── csv_parser.py     # CSV解析器
│   │   │   ├── txt_parser.py     # TXT解析器
│   │   │   └── pdf_parser.py     # PDF解析器
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # LLM基类
│   │   │   ├── openai_provider.py
│   │   │   ├── claude_provider.py
│   │   │   └── local_provider.py
│   │   ├── processors/
│   │   │   ├── __init__.py
│   │   │   ├── row_processor.py   # 单行处理器
│   │   │   ├── batch_processor.py # 批量处理器
│   │   │   └── stream_processor.py # 流式处理器
│   │   └── output/
│   │       ├── __init__.py
│   │       ├── excel_writer.py
│   │       ├── csv_writer.py
│   │       └── json_writer.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── task_manager.py       # 任务管理
│   │   ├── config_manager.py     # 配置管理
│   │   └── progress_tracker.py   # 进度追踪
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI主入口
│   │   ├── routes/
│   │   │   ├── tasks.py          # 任务相关API
│   │   │   ├── files.py          # 文件上传API
│   │   │   └── health.py         # 健康检查
│   │   └── schemas/
│   │       └── models.py         # Pydantic模型
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py               # 命令行工具
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # 日志工具
│       ├── validators.py         # 验证工具
│       └── helpers.py            # 辅助函数
├── tests/
│   ├── test_parsers.py
│   ├── test_llm.py
│   ├── test_processors.py
│   └── fixtures/                 # 测试数据
├── configs/
│   ├── config.yaml               # 默认配置
│   └── prompts/                  # 提示词模板库
│       ├── sentiment_analysis.yaml
│       ├── data_extraction.yaml
│       └── classification.yaml
├── examples/
│   ├── basic_usage.py
│   ├── batch_processing.py
│   └── custom_prompt.py
├── docs/
│   ├── API.md                    # API文档
│   ├── USER_GUIDE.md            # 用户指南
│   └── DEVELOPMENT.md           # 开发文档
├── scripts/
│   ├── setup.sh                  # 环境设置脚本
│   └── run_tests.sh             # 测试脚本
├── .env.example                  # 环境变量模板
├── requirements.txt              # 依赖列表
├── setup.py                      # 安装配置
├── README.md                     # 项目说明
└── DESIGN.md                     # 本设计文档
```

---

## 9. 开发路线图

### Phase 1: 核心功能（2-3周）
- [ ] 文档解析模块（Excel, CSV）
- [ ] LLM集成（OpenAI）
- [ ] 单行处理器
- [ ] 基础CLI工具

### Phase 2: 增强功能（2-3周）
- [ ] 批量处理模式
- [ ] 更多文件格式（TXT, PDF）
- [ ] 更多LLM提供商
- [ ] 任务管理系统

### Phase 3: 生产就绪（2-3周）
- [ ] Web API服务
- [ ] 错误处理和重试
- [ ] 进度追踪
- [ ] 性能优化

### Phase 4: 高级特性（2-3周）
- [ ] Web前端界面
- [ ] 异步任务队列
- [ ] 数据库持久化
- [ ] 监控和日志系统

---

## 10. 使用示例

### 10.1 Python API使用
```python
from llm_excel_processor import ExcelProcessor, OpenAIProvider, PromptTemplate

# 初始化处理器
processor = ExcelProcessor(
    llm_provider=OpenAIProvider(api_key="your-api-key"),
    mode="row"
)

# 定义提示词模板
template = PromptTemplate(
    template="分析以下数据：{text}，返回情感分类（正面/负面/中性）",
    output_format="json"
)

# 处理文件
result = processor.process_file(
    input_file="data.xlsx",
    output_file="result.xlsx",
    prompt_template=template,
    columns=["text"]
)

print(f"处理完成: {result.total_rows} 行")
```

### 10.2 CLI使用
```bash
# 基础使用
llm-excel-processor process \
  --input data.xlsx \
  --output result.xlsx \
  --config config.yaml

# 指定LLM提供商
llm-excel-processor process \
  --input data.xlsx \
  --provider openai \
  --model gpt-4 \
  --prompt "分析这行数据: {column1}"
```

### 10.3 API使用
```bash
# 上传文件并创建任务
curl -X POST "http://localhost:8000/api/tasks" \
  -F "file=@data.xlsx" \
  -F "config=@config.yaml"

# 查询任务进度
curl "http://localhost:8000/api/tasks/{task_id}"

# 下载结果
curl "http://localhost:8000/api/tasks/{task_id}/download"
```

---

## 11. 总结

本设计文档提供了LLM Excel Processor的完整架构设计，包括：
- 模块化的系统架构，便于扩展和维护
- 支持多种文件格式的解析能力
- 灵活的LLM集成方案
- 多种处理模式（单行、批量、流式）
- 完善的错误处理和重试机制
- 清晰的项目结构和开发路线图

该设计确保了系统的可扩展性、可维护性和生产就绪性。
