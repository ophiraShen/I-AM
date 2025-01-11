# 数据库架构规划

## 一、整体架构

### 1. 核心数据存储

- 初期：SQLite
- 后期：PostgreSQL
- 用途：存储结构化数据（用户信息、对话记录、日记、冥想音频等）

### 2. 向量数据存储

- 选型：Chroma
- 用途：存储AI对话向量、语义检索

## 二、分阶段实施计划

**第一阶段（开发期）**

1. **使用 SQLite**
    - 零配置，快速开发
    - 存储所有结构化数据
    - 使用内置全文搜索功能
2. **集成 Chroma**
    - 嵌入式部署
    - 存储对话向量
    - 实现语义搜索

**第二阶段（优化期）**

1. **迁移到 PostgreSQL**
    - 时机：用户量增长或并发需求提升
    - 迁移内容：所有 SQLite 中的数据
    - 优势：更好的并发处理和查询性能
2. **优化 Chroma**
    - 配置持久化存储
    - 优化向量索引
    - 提升检索性能

**第三阶段（扩展期）**

1. **数据库扩展**
    - 评估 PostgreSQL 集群需求
    - 考虑读写分离
    - 实现数据分片
2. **向量数据库升级**
    - 评估迁移到 Qdrant 的需求
    - 或根据需求考虑 Milvus
    - 实现分布式部署

## 三、数据表设计

### 1. 核心数据表

```sql
-- 用户表
users (
    user_id,
    username,
    email,
    password_hash,
    profile,
    created_at
)

-- 对话会话表
chat_sessions (
    session_id,
    user_id,
    title,
    created_at,
    last_message_at,
    metadata
)

-- 消息表
messages (
    message_id,
    session_id,
    role,
    content,
    created_at,
    vector_id,
    metadata
)

-- 日记表
journals (
    journal_id,
    user_id,
    content,
    mood,
    created_at,
    metadata
)

-- 冥想记录表
meditations (
    meditation_id,
    user_id,
    type,
    duration,
    completed_at,
    metadata
)
```

### 2. 向量数据（Chroma）

- 存储内容：
  - 对话向量嵌入
  - 语义索引
  - 相似度检索数据

## 四、数据同步策略

### 1. 实时同步

- 新消息同时写入 PostgreSQL 和 Chroma
- 保持向量ID与消息ID的对应关系

### 2. 异步同步

- 定期同步检查
- 数据一致性验证
- 错误数据修复

## 五、性能监控指标

### 1. 数据库监控

- 查询响应时间
- 连接池使用情况
- 磁盘使用情况
- 缓存命中率

### 2. 向量检索监控

- 检索延迟
- 准确率
- 资源使用情况

## 六、扩展时机判断标准

### 1. SQLite 转 PostgreSQL

- 并发用户数 > 100
- 数据量 > 10GB
- 查询延迟明显提升
- 需要复杂的事务处理

### 2. Chroma 转 Qdrant/Milvus

- 向量数据量 > 100万
- 检索延迟 > 1秒
- 需要分布式部署
- 需要更复杂的向量操作

## 七、数据备份策略

### 1. 开发阶段

- 定期备份 SQLite 文件
- 备份 Chroma 持久化数据

### 2. 生产阶段

- PostgreSQL 定时全量备份
- 实时事务日志备份
- 向量数据定期备份

## 八、注意事项

### 1. 数据安全

- 实现数据加密
- 定期安全审计
- 用户数据脱敏

### 2. 性能优化

- 合理使用索引
- 优化查询语句
- 实现缓存策略

### 3. 容错处理

- 实现重试机制
- 数据一致性检查
- 错误日志记录

这个规划涵盖了数据库架构的主要方面，可以根据项目发展情况进行调整和优化。建议在实施每个阶段前，都进行详细的技术评估和测试。
