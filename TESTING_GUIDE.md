# 测试指南

本文档提供详细的测试步骤，帮助你验证LLM Excel Processor的所有功能。

## 环境准备

### 1. 安装依赖

推荐使用虚拟环境：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

或使用自动安装脚本：

```bash
./setup.sh
```

### 2. 配置API密钥

**方式1：环境变量**

```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

**方式2：.env文件**

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 文件
nano .env
# 设置: OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 验证安装

```bash
# 测试模块导入
python test_simple.py

# 查看CLI帮助
python src/cli/main.py --help
```

## 测试流程

### 阶段1：基础功能测试（不需要API密钥）

#### 1.1 模块导入测试

```bash
python test_simple.py
```

**预期输出：**
```
✓ 解析器模块导入成功
✓ LLM模块导入成功
✓ 处理器模块导入成功
✓ 输出模块导入成功
✓ 应用层模块导入成功
✓ 配置管理器测试成功
✓ 提示词模板测试成功
✓ 工厂模式测试成功
✓ 进度追踪器测试成功
✅ 所有基础测试通过！
```

#### 1.2 CLI工具测试

```bash
# 列出支持的提供商
python src/cli/main.py list-providers

# 列出支持的格式
python src/cli/main.py list-formats

# 创建配置文件
python src/cli/main.py init-config -o test_config.yaml

# 验证配置文件
python src/cli/main.py validate-config test_config.yaml
```

### 阶段2：创建测试数据

```bash
# 创建示例Excel文件
python test_data/create_sample_data.py
```

**生成的文件：**
- `test_data/customer_feedback.xlsx` - 5行客户反馈数据
- `test_data/products.xlsx` - 5行商品数据
- `test_data/addresses.xlsx` - 5行地址数据
- `test_data/simple_test.xlsx` - 3行简单测试数据

### 阶段3：真实LLM调用测试（需要API密钥）

⚠️ **注意：以下测试会真实调用OpenAI API并产生费用**

#### 3.1 最简单的测试（预估成本：$0.001）

```bash
python src/cli/main.py process \
  -i test_data/simple_test.xlsx \
  -o output/test_result.xlsx \
  --provider openai \
  --model gpt-3.5-turbo \
  --mode row \
  --prompt "请将以下文本翻译成英文: {text}"
```

**预期输出：**
```
📄 解析输入文件...
✓ 成功加载 3 行数据

🤖 初始化LLM提供商...
✓ 使用 openai - gpt-3.5-turbo

⚙️  初始化数据处理器...
✓ 使用 row 模式

🔄 开始处理数据...
进度: |████████████████████████████████| 100.0% (3/3)
✓ 处理完成: 3 成功, 0 失败

💾 保存结果...
✓ 结果已保存到: output/test_result.xlsx

==================================================
✅ 任务执行完成
==================================================

任务ID: xxx-xxx-xxx
总行数: 3
成功: 3
失败: 0
Token使用: ~150
预估成本: $0.0007
用时: 2.5秒
输出文件: output/test_result.xlsx
```

#### 3.2 使用配置文件测试（预估成本：$0.003）

```bash
# 使用预定义的情感分析配置
python src/cli/main.py process \
  -c test_data/customer_feedback_config.yaml
```

**查看结果：**
```bash
# 可以用Excel或以下命令查看
python -c "
import pandas as pd
df = pd.read_excel('output/feedback_analysis.xlsx')
print(df[['customer_name', 'status', 'parsed_result']].to_string())
"
```

#### 3.3 批量处理模式测试（预估成本：$0.002）

```bash
python src/cli/main.py process \
  -i test_data/products.xlsx \
  -o output/products_batch.xlsx \
  --mode batch \
  --batch-size 3 \
  --prompt "为以下商品生成一句话营销文案: {product_name}"
```

**批量模式优势：**
- API调用次数：2次（而不是5次）
- 预估成本降低：60%
- 处理速度：更快

#### 3.4 不同输出格式测试

**输出为CSV：**
```bash
python src/cli/main.py process \
  -i test_data/simple_test.xlsx \
  -o output/result.csv \
  --prompt "翻译: {text}"
```

**输出为JSON：**
```bash
python src/cli/main.py process \
  -i test_data/simple_test.xlsx \
  -o output/result.json \
  --prompt "分析情感: {text}"
```

### 阶段4：高级功能测试

#### 4.1 错误处理测试

创建一个会导致部分失败的测试：

```bash
# 创建包含空值的测试数据
python -c "
import pandas as pd
df = pd.DataFrame({'text': ['正常文本', None, '另一个文本']})
df.to_excel('test_data/with_null.xlsx', index=False)
"

# 处理包含空值的数据
python src/cli/main.py process \
  -i test_data/with_null.xlsx \
  -o output/null_test.xlsx \
  --prompt "分析: {text}"
```

**验证结果：**
- 应该有1-2行失败
- 失败的行会有错误信息
- 成功的行正常处理

#### 4.2 大文件处理测试

```bash
# 创建较大的测试文件（100行）
python -c "
import pandas as pd
df = pd.DataFrame({
    'id': range(100),
    'text': [f'这是第{i}条测试文本' for i in range(100)]
})
df.to_excel('test_data/large_test.xlsx', index=False)
"

# 使用batch模式处理
python src/cli/main.py process \
  -i test_data/large_test.xlsx \
  -o output/large_result.xlsx \
  --mode batch \
  --batch-size 20 \
  --prompt "计算文本长度: {text}"
```

**监控指标：**
- 处理速度
- Token使用量
- 成本估算
- 进度显示

#### 4.3 复杂提示词测试

```bash
python src/cli/main.py process \
  -i test_data/customer_feedback.xlsx \
  -o output/complex_analysis.json \
  --prompt "请详细分析客户反馈并返回JSON格式结果：
客户：{customer_name}
反馈：{feedback_text}
日期：{feedback_date}

返回格式：
{
  \"sentiment\": \"positive/neutral/negative\",
  \"score\": 0.0-1.0,
  \"keywords\": [\"关键词1\", \"关键词2\"],
  \"summary\": \"简短总结\"
}"
```

## Python API测试

### 测试1：基础API使用

创建文件 `test_api.py`：

```python
import os
import pandas as pd
from src.core.llm import OpenAIProvider, PromptTemplate
from src.core.processors import RowProcessor

# 设置API密钥
os.environ['OPENAI_API_KEY'] = 'your-key-here'

# 创建测试数据
df = pd.DataFrame({
    'text': ['你好', '再见', '谢谢']
})

# 创建LLM提供商
llm = OpenAIProvider(
    api_key=os.getenv('OPENAI_API_KEY'),
    model='gpt-3.5-turbo',
    temperature=0.3
)

# 创建提示词模板
template = PromptTemplate(
    template="翻译成英文: {text}",
    system_prompt="你是一个翻译专家"
)

# 创建处理器
processor = RowProcessor(llm, template)

# 处理数据
print("开始处理...")
results = processor.process_dataframe(df)

# 显示结果
print("\n处理结果:")
for idx, row in results.iterrows():
    print(f"原文: {row['original_data']['text']}")
    print(f"翻译: {row['parsed_result']}")
    print(f"状态: {row['status']}\n")
```

运行测试：
```bash
python test_api.py
```

### 测试2：完整流程API

创建文件 `test_full_api.py`：

```python
from src.app import ConfigManager, TaskManager

# 加载配置
config = ConfigManager()
config.load_from_file('test_data/customer_feedback_config.yaml')

# 创建任务管理器
manager = TaskManager(config)

# 执行任务（带进度回调）
def progress_callback(progress):
    print(f"进度: {progress.progress_percentage:.1f}% - "
          f"成功: {progress.success_count}, "
          f"失败: {progress.failed_count}")

result = manager.execute(progress_callback=progress_callback)

# 打印摘要
print("\n" + "="*50)
print("任务完成摘要")
print("="*50)
print(f"任务ID: {result['task_id']}")
print(f"总行数: {result['total_rows']}")
print(f"成功: {result['success_count']}")
print(f"失败: {result['failed_count']}")
print(f"Token使用: {result['total_tokens']}")
print(f"预估成本: ${result['estimated_cost']:.4f}")
print(f"用时: {result['elapsed_time']:.1f}秒")
print(f"输出: {result['output_file']}")
```

运行测试：
```bash
python test_full_api.py
```

## 性能基准测试

### 对比不同处理模式

创建 `benchmark.py`：

```python
import time
import pandas as pd
from src.core.llm import OpenAIProvider, PromptTemplate
from src.core.processors import RowProcessor, BatchProcessor

# 创建测试数据
df = pd.DataFrame({
    'text': [f'测试文本{i}' for i in range(20)]
})

llm = OpenAIProvider(api_key='your-key', model='gpt-3.5-turbo')
template = PromptTemplate(template="翻译: {text}")

# 测试Row模式
print("测试Row模式...")
start = time.time()
row_processor = RowProcessor(llm, template)
row_results = row_processor.process_dataframe(df)
row_time = time.time() - start
row_cost = row_results['tokens_used'].sum() * 0.000002

# 测试Batch模式
print("测试Batch模式...")
start = time.time()
batch_processor = BatchProcessor(llm, template, batch_size=5)
batch_results = batch_processor.process_dataframe(df)
batch_time = time.time() - start
batch_cost = batch_results['tokens_used'].sum() * 0.000002

# 对比结果
print("\n" + "="*50)
print("性能对比")
print("="*50)
print(f"Row模式:   用时 {row_time:.1f}s, 成本 ${row_cost:.4f}")
print(f"Batch模式: 用时 {batch_time:.1f}s, 成本 ${batch_cost:.4f}")
print(f"速度提升: {(row_time/batch_time-1)*100:.1f}%")
print(f"成本降低: {(1-batch_cost/row_cost)*100:.1f}%")
```

## 故障排查

### 问题1：模块导入错误

**错误：** `ModuleNotFoundError: No module named 'xxx'`

**解决：**
```bash
pip install -r requirements.txt
```

### 问题2：API密钥错误

**错误：** `AuthenticationError` 或 API密钥无效

**解决：**
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 重新设置
export OPENAI_API_KEY='sk-your-actual-key'

# 或在命令中直接指定
python src/cli/main.py process ... --api-key 'sk-your-key'
```

### 问题3：文件路径错误

**错误：** `FileNotFoundError`

**解决：**
```bash
# 使用绝对路径
python src/cli/main.py process \
  -i $(pwd)/test_data/simple_test.xlsx \
  -o $(pwd)/output/result.xlsx \
  ...

# 或确保从项目根目录运行
cd /home/user/Test_drive
python src/cli/main.py process ...
```

### 问题4：编码问题

**错误：** `UnicodeDecodeError`

**解决：**
在配置文件中指定编码：
```yaml
input:
  file: "data.csv"
  encoding: "gbk"  # 或 utf-8, utf-8-sig
```

### 问题5：Token限制

**错误：** `maximum context length exceeded`

**解决：**
1. 减少批次大小：`--batch-size 5`
2. 减少max_tokens设置
3. 简化提示词模板
4. 使用支持更大上下文的模型

## 成本估算

基于OpenAI GPT-3.5-turbo定价（2024年）：

| 任务类型 | 行数 | 模式 | 预估Token | 预估成本 |
|---------|------|------|----------|---------|
| 简单翻译 | 10 | row | 500 | $0.001 |
| 简单翻译 | 10 | batch | 300 | $0.0006 |
| 情感分析 | 50 | row | 3000 | $0.006 |
| 情感分析 | 50 | batch(10) | 2000 | $0.004 |
| 复杂分析 | 100 | row | 10000 | $0.02 |
| 复杂分析 | 100 | batch(20) | 6000 | $0.012 |

**成本优化建议：**
- 使用batch模式可节省40-60%
- 使用gpt-3.5-turbo比gpt-4便宜15倍
- 简化提示词可减少token使用

## 测试清单

在发布前，确保完成以下测试：

- [ ] 基础模块导入测试
- [ ] CLI工具所有命令测试
- [ ] 配置文件加载和验证
- [ ] 三种处理模式（row/batch/stream）
- [ ] 三种输出格式（xlsx/csv/json）
- [ ] 错误处理和恢复
- [ ] 进度追踪和显示
- [ ] Token统计和成本估算
- [ ] 大文件处理（100+行）
- [ ] Python API调用

## 下一步

测试通过后，可以：

1. 处理真实数据
2. 集成到现有系统
3. 开发Phase 2功能（更多LLM提供商、Web API等）
4. 部署到生产环境

## 获取帮助

- 查看 [QUICKSTART.md](QUICKSTART.md)
- 查看 [DESIGN.md](DESIGN.md)
- 运行 `python src/cli/main.py --help`
