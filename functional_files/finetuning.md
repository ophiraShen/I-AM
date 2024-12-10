# AI模型微调计划

## 一、数据准备阶段 (12.10-12.11)

### 1. 数据清洗
- 数据规模：1024条多轮心理咨询对话
- 清洗步骤（已完成）：
  - 移除重复对话
  - 处理异常字符和特殊符号
  - 统一标点符号格式
  - 处理过长对话（截断或分段）
  - 检查并修正明显的标注错误
#### 1.1 合并相似的 topic，设置新字段：group
```python
TOPIC_MAPPING = {
    'mental_health': ['mental_health', 'anxiety', 'emotional_management', 'emotional_awareness', 'stress'],
    'health': ['health'],
    'career': ['career', 'work_life_balance'],
    'study': ['study'],
    'personal_growth': ['self_growth', 'confidence', 'life_purpose', 'behavior_change'],
    'finance': ['finance'],
    'relationship': ['relationship', 'social', 'family', 'friendship'],
}
```
#### 1.2 按照对话轮次长度，设置新字段：length_group
```python
if length <= 5:
    length_group = 'short'
elif length <= 8:
    length_group = 'medium'
else:
    length_group = 'long'
```

#### 1.3 按照 'group_length_group' 字段，划分数据集，并统计各类数据量
```
mental_health_medium 58
personal_growth_medium 159
finance_long 6
mental_health_long 5
personal_growth_long 29
relationship_short 18
career_short 26
health_short 4
relationship_medium 189
mental_health_short 14
career_medium 167
finance_medium 133
study_long 6
career_long 16
relationship_long 21
health_long 7
personal_growth_short 25
study_medium 78
finance_short 6
study_short 7
health_medium 50
```

### 2. 数据集划分与处理
- 训练集（80%）：
  - 完整的标注和特殊标记处理
  - 保留所有对话结构和语义信息
  - 可进行适当的数据增强（当前不考虑）

- 验证集（10%）：
  - 基础的对话结构标记
  - 保留必要的标注信息
  - 不进行数据增强
  - 用于监控训练过程

- 测试集（10%）：
  - 最小化处理
  - 仅保留用户输入部分
  - 移除助手回复的标注
  - 用于最终效果评估

#### 2.1 按照数据量划分比例
1. 数据量 >= 50 的 group，划分比例为 80:10:10
2. 数据量 20-49 的 group，划分比例为 70:15:15
3. 数据量 < 20 的 group，保证验证集和测试集至少各有一个样本

### 3. 数据标注处理
- 特殊标记设计
  - 对话结构标记：`<|begin|>`, `<|end|>`, `<|user|>`, `<|assistant|>`
  - 主题标记：`<|topic_*|>`（整体对话级别）
  - 用户标记：
    - 意图标记：`<|intent_*|>`
    - 情感标记：`<|emotion_*|>`
  - 助手标记：
    - 意图标记：`<|intent_*|>`
    - 语气标记：`<|tone_*|>`
    - 技巧标记：`<|technique_*|>`, `<|purpose_*|>`
    - 对话阶段：`<|phase_*|>`, `<|progress_*|>`

- 标注统计分析
  - 统计各类标注的分布情况
  - 验证标注的完整性和一致性
  - 生成标注覆盖率报告
  - 识别并补充缺失标注



## 二、模型准备阶段 (12.12)

### 1. 基座模型选择
- 主选方案: ChatGLM4
- 备选方案: Qwen2.5
- 评估标准:
  - 中文理解能力
  - 情感表达能力
  - 推理能力
  - 资源占用情况

### 2. 微调方法选择
- 采用LoRA技术进行微调
- 关键参数设置:
  - Rank: 8
  - Alpha: 32
  - Dropout: 0.1
  - Learning rate: 3e-4

### 3. Prompt模板设计
```python
PROMPT_TEMPLATE = """
基于以下用户背景信息：
主题: {topic}
意图: {intent}
情感: {emotion}
用户问题: {user_question}
请提供一个富有同理心和实用性的回答，包含:
- 情感共鸣
- 实用建议
- 行动指导
- 思维引导
"""
```


## 三、训练阶段 (12.13)

### 1. 初步实验
- 使用10%数据进行试验性训练
- 验证训练流程
- 调整超参数
- 评估初步效果

### 2. 全量训练
- 使用完整训练集进行训练
- 训练轮次: 3-5 epochs
- 批次大小: 4
- 梯度累积: 4
- 训练时长预估: 4-6小时

### 3. 训练监控
- Loss曲线监控
- 验证集性能监控
- 资源使用监控
- 生成样本质量抽检

## 四、评估阶段 (12.14)

### 1. 评估指标
- 回复相关性 (Relevance)
- 情感共鸣度 (Empathy)
- 建议可执行性 (Actionability)
- 回复连贯性 (Coherence)

### 2. 人工评估
- 随机抽取50条测试集对话
- 邀请3位专业心理咨询师评分
- 评分维度:
  - 专业性 (1-5分)
  - 同理心 (1-5分)
  - 建议质量 (1-5分)
  - 表达方式 (1-5分)

### 3. 自动评估
```python
def evaluate_metrics(model, test_data):
    metrics = {
        "relevance": [],
        "empathy": [],
        "actionability": [],
        "coherence": []
    }
```

### 实现评估逻辑
```python
return metrics
```


## 五、优化阶段 (12.14)

### 1. 错误分析
- 收集并分析表现欠佳的案例
- 总结常见问题类型
- 制定优化策略

### 2. 模型优化
- 根据错误分析调整训练策略
- 考虑是否需要增补训练数据
- 微调模型参数

### 3. 部署准备
- 模型压缩与量化
- 推理性能优化
- 部署文档准备

## 六、风险控制

### 1. 技术风险
- 定期保存检查点
- 监控训练过程
- 准备备用方案

### 2. 质量风险
- 设置输出内容过滤
- 建立安全审核机制
- 准备人工干预方案

### 3. 伦理风险
- 确保建议的合理性
- 避免过度承诺
- 保护用户隐私

## 七、成功标准

1. 模型性能指标
- 相关性得分 > 0.8
- 情感共鸣度 > 0.75
- 建议可执行性 > 0.7
- 人工评分均值 > 4.0

2. 技术指标
- 推理延迟 < 1s
- 显存占用 < 8GB
- 稳定性 > 99.9%

---
注：本计划将根据实际训练情况进行动态调整。