# 🚀 立即测试 Gemini - Windows版本

## 问题已修复！✅

刚才的bug已经修复了。现在按照以下步骤测试：

---

## 步骤1：安装必要的Python包

```bash
pip install pandas openpyxl google-generativeai pyyaml click
```

如果提示`pip`不是命令，尝试：
```bash
python -m pip install pandas openpyxl google-generativeai pyyaml click
```

---

## 步骤2：获取Gemini API密钥

1. 访问：https://makersuite.google.com/app/apikey
2. 用Google账号登录
3. 点击 "Create API Key"
4. 复制生成的密钥（格式：`AIzaSy...`）

---

## 步骤3：设置API密钥（Windows）

```bash
# 方式1：临时设置（推荐测试用）
set GEMINI_API_KEY=你的密钥

# 方式2：创建.env文件（持久化）
echo GEMINI_API_KEY=你的密钥 > .env
```

验证设置：
```bash
echo %GEMINI_API_KEY%
```

---

## 步骤4：创建测试数据

```bash
python test_data/create_sample_data.py
```

**预期输出：**
```
✓ 创建客户反馈数据: test_data/customer_feedback.xlsx
✓ 创建商品数据: test_data/products.xlsx
✓ 创建地址数据: test_data/addresses.xlsx
✓ 创建简单测试数据: test_data/simple_test.xlsx
```

---

## 步骤5：运行基础测试（可选）

```bash
python test_gemini.py
```

这会测试9个方面，确保Gemini集成正常工作。

---

## 步骤6：运行实际数据处理测试 ⭐

```bash
python src/cli/main.py process ^
  -i test_data/simple_test.xlsx ^
  -o output/gemini_result.xlsx ^
  --provider gemini ^
  --model gemini-1.5-flash ^
  --prompt "翻译成英文: {text}"
```

**注意：** Windows命令行用 `^` 续行，如果在一行输入，去掉 `^`：

```bash
python src/cli/main.py process -i test_data/simple_test.xlsx -o output/gemini_result.xlsx --provider gemini --model gemini-1.5-flash --prompt "翻译成英文: {text}"
```

---

## 预期输出

```
📋 使用命令行参数创建配置

==================================================
🚀 开始执行任务
==================================================

📄 解析输入文件...
✓ 成功加载 3 行数据

🤖 初始化LLM提供商...
✓ 使用 gemini - gemini-1.5-flash

⚙️  初始化数据处理器...
✓ 使用 row 模式

🔄 开始处理数据...
进度: |████████████████████████████| 100.0% (3/3)
✓ 处理完成: 3 成功, 0 失败

💾 保存结果...
✓ 结果已保存到: output/gemini_result.xlsx

==================================================
✅ 任务执行完成
==================================================

任务ID: xxx-xxx-xxx
总行数: 3
成功: 3
失败: 0
Token使用: ~150
预估成本: $0.0002
用时: 2-3秒
输出文件: output/gemini_result.xlsx
```

---

## 步骤7：查看结果

### 方式1：用Excel打开
```bash
start output/gemini_result.xlsx
```

### 方式2：用Python查看
```bash
python -c "import pandas as pd; df = pd.read_excel('output/gemini_result.xlsx'); print(df[['original_data', 'parsed_result', 'status']])"
```

---

## 其他测试示例

### 测试1：使用配置文件
```bash
python src/cli/main.py process -c test_data/gemini_test_config.yaml
```

### 测试2：批量处理（更快更便宜）
```bash
python src/cli/main.py process ^
  -i test_data/customer_feedback.xlsx ^
  -o output/feedback_analysis.xlsx ^
  --provider gemini ^
  --mode batch ^
  --batch-size 3 ^
  --prompt "分析情感(positive/neutral/negative): {feedback_text}"
```

### 测试3：处理CSV文件
```bash
python src/cli/main.py process ^
  -i test_data/simple_test.csv ^
  -o output/csv_result.xlsx ^
  --provider gemini ^
  --prompt "翻译: {text}"
```

---

## 常见问题

### Q1: "ModuleNotFoundError: No module named 'pandas'"
**解决：** 重新安装依赖
```bash
pip install pandas openpyxl google-generativeai pyyaml click
```

### Q2: "GEMINI_API_KEY environment variable not set"
**解决：** 设置环境变量
```bash
set GEMINI_API_KEY=你的密钥
echo %GEMINI_API_KEY%
```

### Q3: "FileNotFoundError: test_data/simple_test.xlsx"
**解决：** 创建测试数据
```bash
python test_data/create_sample_data.py
```

### Q4: "API key not valid"
**解决：**
1. 检查密钥是否正确复制
2. 确认密钥没有过期
3. 重新生成密钥：https://makersuite.google.com/app/apikey

### Q5: 速度慢或超时
**解决：**
1. 检查网络连接
2. 尝试使用代理
3. 减少batch_size

---

## 快速测试脚本（Git Bash）

如果你使用Git Bash，可以运行：
```bash
./quick_test_gemini.sh
```

这会自动完成所有测试步骤。

---

## 成功标志

当你看到以下输出时，表示测试成功：

✅ **任务执行完成**
✅ **成功: 3, 失败: 0**
✅ **结果文件已创建: output/gemini_result.xlsx**

---

## 下一步

1. ✅ 测试成功后，可以处理自己的数据
2. 📊 对比Gemini和OpenAI的效果和成本
3. ⚡ 使用batch模式提升处理速度
4. 📖 查看完整文档：
   - [RUN_GEMINI_TEST.md](RUN_GEMINI_TEST.md)
   - [GEMINI_SETUP.md](GEMINI_SETUP.md)

---

## 需要帮助？

- 查看错误日志
- 检查API密钥设置
- 确认网络连接
- 查看文档中的故障排查部分

祝测试顺利！🚀
