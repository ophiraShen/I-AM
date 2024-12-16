# 微调数据处理

## 一、数据准备阶段 (12.10-12.11)

### 1. 数据清洗
- 数据规模：1024条多轮心理咨询对话
- 清洗步骤（已完成）：
  - 移除重复对话
  - 处理异常字符和特殊符号
  - 统一标点符号格式
  - 处理过长对话（截断或分段）
  - 检查并修正明显的标注错误
#### 1.1 合并相似的 topic，为设置新字段：group
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
- 数据量统计


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
  - 只保留对话数据
  - 可进行适当的数据增强（当前不考虑）

- 验证集（10%）：
  - 基础的对话结构标记
  - 只保留对话数据
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

### 3. 数据分割

#### 3.1 添加对话结构标记：
  - 用户角色：`<|user|>`
  - 助手角色：`<|assistant|>`
  - 对话分隔符：`<|endoftext|>`

#### 

