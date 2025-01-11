# I-AM 产品开发规划

## 项目结构
```python
i-am-project/
├── backend/
│   ├── agents/                    # LangGraph 对话代理
│   ├── workflows/                 # 对话流程
│   ├── api/                      # FastAPI接口
│   ├── models/                   # 数据模型
│   │   ├── base.py              # 数据库配置
│   │   └── models.py            # 数据表模型
│   ├── utils/                   # 工具函数
│   │   └── llm.py              # LLM模型接口
│   ├── tests/                   # 测试文件
│   │   ├── conftest.py         # 测试配置
│   │   ├── test_api.py         # API测试
│   │   ├── test_llm.py         # LLM测试
│   │   └── test_database.py    # 数据库测试
│   └── main.py                  # 主程序入口
├── frontend/                     # Flutter前端
└── .env                         # 环境变量配置
```

## 开发进度

### ✅ Day 1: 基础架构搭建 (已完成)
1. FastAPI项目结构
   - [x] 创建基本目录结构
   - [x] 设置环境变量配置
   - [x] 实现基础API端点

2. 数据库设计
   - [x] 创建基础数据模型（User, ChatSession, Message）
   - [x] 设置SQLite数据库连接
   - [x] 实现数据库会话管理

3. LLM模型集成
   - [x] 实现本地GLM模型接口
   - [x] 实现DeepSeek API接口
   - [x] 创建统一的模型接口类

4. 测试框架
   - [x] 设置pytest测试环境
   - [x] 编写API测试
   - [x] 编写LLM接口测试
   - [x] 编写数据库测试

### 🔄 Day 2: LangGraph对话系统 (进行中)
1. 设计对话状态图
   - [ ] 需求分析状态
   - [ ] 计划制定状态
   - [ ] 日常指导状态
   - [ ] 进度追踪状态

2. 实现各状态节点功能
3. 配置状态转换规则
4. 添加错误处理机制

### ⏳ Day 3-5: 待开发功能
- 日记系统
- 冥想引导系统
- 系统集成与优化

## 已完成功能
1. 基础对话API
   - 支持发送消息并获取AI回复
   - 支持多模型切换（GLM和DeepSeek）

2. 数据存储
   - 用户信息存储
   - 对话会话管理
   - 消息历史记录

3. 测试覆盖
   - API端点测试
   - 模型接口测试
   - 数据库操作测试

## 下一步计划
1. 实现用户认证系统
2. 开发LangGraph对话管理
3. 完善错误处理
4. 添加日志系统
5. 开始日记系统开发

## 技术栈
- FastAPI
- SQLite
- GLM-4-9B-Chat (本地模型)
- DeepSeek API
- pytest

## 注意事项
1. 确保代码模块化和可维护性
2. 持续补充单元测试
3. 定期进行代码审查
4. 注意数据安全和隐私保护