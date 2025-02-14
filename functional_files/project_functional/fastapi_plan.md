# I-AM FastAPI 开发规划

## 当前进度 (2024-03-xx)

### 已完成功能：

1. 用户系统
   - [x] 用户注册
   - [x] 用户登录
   - [x] JWT 认证
   - [x] 用户信息获取

2. 对话系统
   - [x] WebSocket 实时对话
   - [x] 对话会话管理（创建、获取、删除）
   - [x] 多会话支持（每个用户可以有多个对话）
   - [x] 对话历史记录
   - [x] 前端测试页面

### 待开发功能：

1. 肯定语系统
   - [ ] 生成肯定语
   - [ ] 获取历史肯定语
   - [ ] 前端集成

2. 冥想系统
   - [ ] 生成冥想引导
   - [ ] 音频处理
   - [ ] 冥想记录管理

### 技术细节：

1. 对话系统实现：
   - 使用 WebSocket 实现实时对话
   - 每个对话有唯一的 session_id
   - 支持对话历史的保存和加载
   - 前端支持多对话切换
   - 对话内容与用户强关联

2. 数据库结构：
   - User: 用户基本信息
   - Chat: 对话会话和历史
   - Affirmation: 肯定语（待实现）
   - Meditation: 冥想记录（待实现）

3. 安全性：
   - JWT token 认证
   - WebSocket 连接认证
   - 用户数据隔离

## 1. 项目结构
```
backend/
├── app/
│   ├── main.py              # FastAPI 应用主入口
│   ├── config.py            # 配置文件
│   ├── database.py          # 数据库配置
│   └── exceptions.py        # 自定义异常
├── api/
│   ├── v1/
│   │   ├── chat.py         # 对话相关路由
│   │   ├── affirmation.py  # 肯定语相关路由
│   │   ├── meditation.py   # 冥想相关路由
│   │   └── users.py        # 用户相关路由
│   └── deps.py             # 依赖注入
├── models/
│   ├── user.py             # 用户模型
│   ├── chat.py             # 对话模型
│   └── base.py             # 基础模型
└── schemas/
    ├── user.py             # 用户数据模式
    ├── chat.py             # 对话数据模式
    ├── affirmation.py      # 肯定语数据模式
    └── meditation.py       # 冥想数据模式
```

## 2. 核心功能模块

### 2.1 用户管理 (users.py)
- 用户注册
  - 路由: POST `/api/v1/users/register`
  - 功能: 创建新用户
  - 返回: 用户信息和 token

- 用户登录
  - 路由: POST `/api/v1/users/login`
  - 功能: 用户登录认证
  - 返回: 访问令牌

- 获取用户信息
  - 路由: GET `/api/v1/users/me`
  - 功能: 获取当前用户信息
  - 权限: 需要认证

### 2.2 对话系统 (chat.py)
- 创建对话
  - 路由: POST `/api/v1/chat/create`
  - 功能: 创建新的对话会话
  - 返回: 会话 ID

- WebSocket 对话连接
  - 路由: WebSocket `/api/v1/chat/ws/{session_id}`
  - 功能: 建立实时对话连接
  - 特性: 支持流式响应

- 获取历史对话
  - 路由: GET `/api/v1/chat/history`
  - 功能: 获取用户的对话历史
  - 参数: 分页、时间范围

### 2.3 肯定语系统 (affirmation.py)
- 生成肯定语
  - 路由: POST `/api/v1/affirmation/generate`
  - 功能: 基于对话生成肯定语
  - 返回: 肯定语列表

- 获取历史肯定语
  - 路由: GET `/api/v1/affirmation/history`
  - 功能: 获取用户的肯定语历史
  - 参数: 分页、时间范围

### 2.4 冥想系统 (meditation.py)
- 生成冥想引导
  - 路由: POST `/api/v1/meditation/generate`
  - 功能: 生成冥想引导内容
  - 返回: 音频文件 URL

- 获取冥想记录
  - 路由: GET `/api/v1/meditation/history`
  - 功能: 获取用户的冥想记录
  - 参数: 分页、时间范围

## 3. 数据模型设计

### 3.1 User 模型
```python
class User(Base):
    id: int
    username: str
    email: str
    hashed_password: str
    created_at: datetime
    is_active: bool
```

### 3.2 Chat 模型
```python
class Chat(Base):
    id: int
    user_id: int
    session_id: str
    messages: List[dict]
    created_at: datetime
```

### 3.3 Affirmation 模型
```python
class Affirmation(Base):
    id: int
    user_id: int
    chat_id: int
    content: List[str]
    created_at: datetime
```

### 3.4 Meditation 模型
```python
class Meditation(Base):
    id: int
    user_id: int
    chat_id: int
    audio_url: str
    script: dict
    created_at: datetime
```

## 4. 中间件与依赖项

### 4.1 认证中间件
- JWT 认证
- 用户会话管理
- 权限验证

### 4.2 异常处理
- 自定义异常响应
- 错误日志记录
- 优雅的错误提示

### 4.3 数据库会话
- SQLite 连接管理
- 会话依赖注入
- 异步支持

## 5. 开发步骤

1. 基础设置 (1天)
   - 项目结构搭建
   - 依赖安装
   - 配置文件设置

2. 数据库集成 (1天)
   - SQLite 配置
   - 模型定义
   - 迁移脚本

3. 用户系统 (1天)
   - 认证实现
   - 用户 CRUD
   - 权限管理

4. 核心功能 (2-3天)
   - 对话系统集成
   - 肯定语系统集成
   - 冥想系统集成

5. WebSocket 实现 (1天)
   - 实时对话
   - 连接管理
   - 错误处理

6. 测试与优化 (1-2天)
   - 单元测试
   - 集成测试
   - 性能优化

## 6. 注意事项

1. 安全性考虑
   - 输入验证
   - XSS 防护
   - CORS 设置
   - 速率限制

2. 性能优化
   - 异步处理
   - 缓存策略
   - 数据库索引

3. 可维护性
   - 代码注释
   - 类型提示
   - 模块化设计

4. 错误处理
   - 全局异常处理
   - 日志记录
   - 友好的错误提示 