# 个性化肯定语生成模块设计

## 一、核心组成部分
1. **对话分析系统** ✅
2. **肯定语生成系统** ✅
3. **结果持久化系统** ✅

## 二、肯定语生成结构

### 1. 生成流程
1. 对话分析 -> 用户洞察生成
2. 洞察分析 -> 个性化肯定语生成
3. 结果保存 -> YAML格式持久化

### 2. 洞察分析结构
```json
{
    "core_needs": "用户的核心需求",
    "emotional_state": [
        "当前的情绪状态1",
        "当前的情绪状态2"
    ],
    "key_issues": [
        "关键问题点1",
        "关键问题点2"
    ],
    "suggested_affirmation_count": 5
}
```

### 3. 肯定语结构
```yaml
affirmations:
  - "个性化肯定语1"
  - "个性化肯定语2"
  - "个性化肯定语3"
```

## 三、已实现的功能

### 1. 对话分析系统
```python
def create_insight(state):
    """基于对话生成用户洞察"""
```

主要特性：
- 分析用户核心需求
- 识别情绪状态
- 提取关键问题点
- 智能推荐肯定语数量
- 错误处理机制

### 2. 肯定语生成系统
```python
def create_affirmations(state):
    """基于洞察生成个性化肯定语"""
```

主要特性：
- 基于用户洞察的个性化生成
- 结构化输出格式
- 自动数量控制
- 错误重试机制
- 质量保证系统

### 3. 持久化系统
```python
def save_affirmations(affirmations, output_path):
    """保存生成的肯定语"""
```

实现功能：
- YAML格式保存
- 时间戳命名
- 自动创建目录
- 错误处理
- UTF-8编码支持

## 四、配置文件结构

### 1. 提示词配置
```yaml
prompts:
  insight: "path/to/insight_prompt.txt"
  generator: "path/to/generator_prompt.txt"
paths:
  output_path: "path/to/output/directory"
```

## 五、使用示例

```python
# 创建肯定语处理图
affirmation_graph = AffirmationAgent(config_path).create_graph()

# 处理用户对话，生成肯定语
result = affirmation_graph.invoke(NodeResult(messages=conversation))
```

## 六、待实现功能

1. **用户反馈系统**
   - 肯定语效果评估
   - 用户偏好学习
   - 内容动态优化

2. **多样性增强**
   - 多语言支持
   - 不同风格的肯定语
   - 场景化定制

3. **智能推荐系统**
   - 基于时间的推荐
   - 基于情境的推荐
   - 个性化展示顺序

## 七、技术栈

### 已使用：
- LangChain (文本生成)
- LangGraph (工作流编排)
- Pydantic (数据验证)
- YAML (配置管理)
- DeepSeek (LLM模型)

## 八、注意事项

1. **质量控制**
   - 确保肯定语的积极性
   - 避免消极或模糊的表达
   - 保持个性化和针对性

2. **性能优化**
   - LLM调用优化
   - 结果缓存机制
   - 批量处理支持

3. **错误处理**
   - 实现完整的错误重试机制
   - 记录详细错误日志
   - 提供降级方案

4. **安全考虑**
   - 用户隐私保护
   - 敏感信息过滤
   - 输出内容审核 