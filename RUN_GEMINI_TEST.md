# 🚀 Gemini Flash 快速测试指南

已经为你配置好Google Gemini 1.5 Flash支持！下面是快速测试步骤。

## ⚡ 为什么用Gemini Flash？

- **速度快 2-3倍** - 比GPT-3.5 Turbo更快
- **成本低 14倍** - 处理10万行数据只需$0.35（GPT-3.5需$5+）
- **免费额度** - 每天1500次请求免费
- **质量好** - 接近GPT-3.5水平

---

## 第1步：获取API密钥（2分钟）

1. 打开浏览器访问：https://makersuite.google.com/app/apikey
2. 用Google账号登录
3. 点击 "Create API Key" 按钮
4. 复制生成的API密钥（格式：AIzaSy...）

---

## 第2步：设置环境变量

```bash
# 设置API密钥
export GEMINI_API_KEY='AIzaSy你的密钥'

# 验证设置
echo $GEMINI_API_KEY
```

或者编辑.env文件：
```bash
echo "GEMINI_API_KEY=你的密钥" >> .env
```

---

## 第3步：安装Gemini依赖

```bash
# 安装Google Generative AI库
pip install google-generativeai

# 如果失败，尝试
pip3 install google-generativeai
```

---

## 第4步：运行集成测试

```bash
python test_gemini.py
```

**预期输出：**
```
============================================================
Google Gemini 集成测试
============================================================

1. 检查API密钥...
✓ API密钥已设置: AIzaSy...

2. 测试模块导入...
✓ Gemini提供商导入成功

3. 测试基础连接...
✓ Gemini提供商初始化成功

4. 测试简单API调用...
✓ API调用成功
  响应: 你好，世界

... (更多测试)

✅ Gemini集成测试完成！
```

---

## 第5步：CLI测试（真实数据处理）

### 测试1：简单翻译（3行数据）

```bash
python src/cli/main.py process \
  -c test_data/gemini_test_config.yaml
```

**预期结果：**
- 处理3行中文文本
- 翻译成英文
- 成本：约$0.0001
- 用时：2-3秒

### 测试2：命令行参数方式

```bash
python src/cli/main.py process \
  -i test_data/simple_test.xlsx \
  -o output/gemini_result.xlsx \
  --provider gemini \
  --model gemini-1.5-flash \
  --prompt "翻译成英文: {text}"
```

### 测试3：批量处理客户反馈（5行数据）

```bash
python src/cli/main.py process \
  -c test_data/gemini_batch_config.yaml
```

**这个测试会：**
- 分析5条客户反馈的情感
- 使用batch模式（更快更便宜）
- 成本：约$0.0003
- 用时：3-4秒

---

## 实用命令速查

### 查看支持的提供商

```bash
python src/cli/main.py list-providers
```

应该看到：
```
支持的LLM提供商:
  • openai
  • gemini  ← 新增
```

### 自定义任务示例

#### 情感分析
```bash
python src/cli/main.py process \
  -i your_reviews.xlsx \
  -o sentiment_results.xlsx \
  --provider gemini \
  --model gemini-1.5-flash \
  --mode batch \
  --batch-size 20 \
  --prompt "分析情感(positive/neutral/negative): {review_text}"
```

#### 内容摘要
```bash
python src/cli/main.py process \
  -i long_articles.xlsx \
  -o summaries.xlsx \
  --provider gemini \
  --prompt "一句话总结: {article}"
```

#### 数据分类
```bash
python src/cli/main.py process \
  -i products.xlsx \
  -o categorized.xlsx \
  --provider gemini \
  --prompt "分类这个产品(电子/服装/食品/其他): {product_name}"
```

---

## 性能对比

我帮你准备了一个小测试，对比Gemini和GPT-3.5：

```bash
# 如果你也有OpenAI API密钥，可以运行对比测试

# Gemini测试
time python src/cli/main.py process \
  -i test_data/customer_feedback.xlsx \
  -o output/gemini_result.xlsx \
  --provider gemini \
  --prompt "情感分析: {feedback_text}"

# OpenAI测试（需要OPENAI_API_KEY）
time python src/cli/main.py process \
  -i test_data/customer_feedback.xlsx \
  -o output/openai_result.xlsx \
  --provider openai \
  --prompt "情感分析: {feedback_text}"
```

**预期对比（5行数据）：**
- Gemini：2-3秒，$0.0003
- GPT-3.5：4-5秒，$0.004

---

## 常见问题

### Q1: 测试失败 - "API key not valid"

**解决：**
```bash
# 检查密钥是否正确设置
echo $GEMINI_API_KEY

# 重新获取密钥
# 访问 https://makersuite.google.com/app/apikey
```

### Q2: "ModuleNotFoundError: No module named 'google.generativeai'"

**解决：**
```bash
pip install google-generativeai
```

### Q3: "Rate limit exceeded"

**解决：**
- 免费额度：15 RPM（每分钟15次请求）
- 等待1分钟后重试
- 或升级到付费计划

### Q4: Gemini返回内容不符合预期

**优化提示词：**
```yaml
# ❌ 模糊的提示词
prompt: "分析这个"

# ✅ 明确的提示词
prompt: "分析情感，只返回positive/neutral/negative之一: {text}"
```

### Q5: 想用Gemini Pro（更高质量）

**修改配置：**
```bash
python src/cli/main.py process \
  -i input.xlsx \
  -o output.xlsx \
  --provider gemini \
  --model gemini-1.5-pro \  # 改用Pro
  --prompt "..."
```

注意：Pro价格是Flash的100倍，但质量更好。

---

## 成本估算

基于Gemini 1.5 Flash定价（2024）：

| 任务类型 | 数据量 | 模式 | 预估成本 | 时间 |
|---------|-------|------|---------|------|
| 简单翻译 | 100行 | row | $0.003 | 30秒 |
| 简单翻译 | 100行 | batch(20) | $0.002 | 10秒 |
| 情感分析 | 1000行 | row | $0.03 | 5分钟 |
| 情感分析 | 1000行 | batch(20) | $0.015 | 2分钟 |
| 内容摘要 | 10000行 | batch(20) | $0.2 | 15分钟 |

**对比OpenAI成本：Gemini便宜14倍** 💰

---

## 下一步

1. ✅ 已完成基础测试
2. 🔄 处理你自己的数据
3. 📊 对比Gemini vs OpenAI的效果
4. ⚡ 优化batch_size提升速度
5. 📖 查看完整文档：[GEMINI_SETUP.md](GEMINI_SETUP.md)

---

## 需要帮助？

- **完整文档**: [GEMINI_SETUP.md](GEMINI_SETUP.md)
- **测试指南**: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **快速开始**: [QUICKSTART.md](QUICKSTART.md)

享受Gemini带来的极速体验！🚀
