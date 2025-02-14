# I-AM 产品开发规划

## 项目结构
```python
project/
├── backend/
│   ├── app/                      # FastAPI应用
│   │   ├── main.py             # 主程序入口
│   │   ├── config.py           # 配置文件
│   │   └── database.py         # 数据库配置
│   ├── api/                     # API路由
│   │   ├── v1/                 # API版本1
│   │   │   ├── chat.py        # 对话接口
│   │   │   ├── affirmation.py # 肯定语接口
│   │   │   ├── meditation.py  # 冥想接口
│   │   │   └── users.py       # 用户接口
│   │   └── deps.py            # 依赖注入
│   ├── models/                  # SQLAlchemy模型
│   │   ├── user.py            # 用户模型
│   │   ├── chat.py            # 对话模型
│   │   └── base.py            # 基础模型
│   ├── agents/                  # LangGraph 对话代理
│   │   ├── chat_agent.py       # 主对话代理
│   │   ├── affirmation_agent.py # 肯定语代理
│   │   └── meditation_agent.py  # 冥想引导代理
│   ├── schemas/                 # Pydantic模型
│   ├── crud/                    # CRUD操作
│   └── tests/                   # 测试文件
├── miniprogram/                  # 微信小程序前端
│   ├── pages/                    # 页面文件
│   │   ├── index/               # 首页
│   │   ├── chat/                # 对话页
│   │   ├── affirmation/         # 肯定语页
│   │   └── meditation/          # 冥想页
│   ├── components/              # 组件
│   ├── utils/                   # 工具函数
│   ├── services/                # API服务
│   └── app.json                 # 小程序配置
└── project.config.json          # 项目配置
```

## 开发进度

### ✅ Phase 1: 核心功能模块 (已完成)
1. 主对话系统
   - [x] 对话路由分析
   - [x] 多模块协作机制
   - [x] 状态管理系统

2. 肯定语模块
   - [x] 对话分析系统
   - [x] 肯定语生成系统
   - [x] 结果持久化系统

3. 冥想引导模块
   - [x] 引导词生成系统
   - [x] 语音合成模块
   - [x] 背景音乐系统
   - [x] 音频混合器

### 🔄 Phase 2: 后端开发 (进行中)
1. FastAPI项目搭建 (预计1-2天)
   - [ ] 项目初始化配置
   - [ ] SQLite数据库设计
   - [ ] SQLAlchemy模型定义
   - [ ] 基础中间件配置
   - [ ] 集成已有的Agent模块

2. API开发 (预计3-4天)
   - [ ] RESTful API设计与实现
   - [ ] WebSocket服务实现
   - [ ] 对话历史管理
   - [ ] 用户认证系统
   - [ ] 文件上传处理
   - [ ] API文档（自动生成）

3. 测试与部署 (预计1-2天)
   - [ ] pytest单元测试
   - [ ] API集成测试
   - [ ] 性能测试
   - [ ] 部署文档

### 🔄 Phase 3: MVP小程序开发 (待开发)
1. 基础UI设计 (预计3天)
   - [ ] 设计规范制定
   - [ ] 组件库选型
   - [ ] 首页导航设计
   - [ ] 聊天界面开发
   - [ ] 肯定语卡片展示
   - [ ] 冥想引导页面
   - [ ] 设置页面

2. 核心功能实现 (预计4天)
   - [ ] 用户认证流程
   - [ ] WebSocket聊天实现
   - [ ] 音频组件开发
   - [ ] 本地存储设计
   - [ ] API服务集成
   - [ ] 错误处理机制

3. 小程序特性适配 (预计2天)
   - [ ] 页面生命周期管理
   - [ ] 微信授权登录
   - [ ] 分享功能
   - [ ] 用户信息获取

### ⏳ Phase 4: 产品优化 (待开发)
1. 功能完善
   - [ ] 用户数据同步
   - [ ] 订阅消息通知
   - [ ] 离线数据缓存
   - [ ] 支付功能集成

2. 体验优化
   - [ ] 界面动画优化
   - [ ] 性能优化
   - [ ] 加载体验优化
   - [ ] 错误提示优化

3. 运营功能
   - [ ] 数据统计分析
   - [ ] 用户反馈系统
   - [ ] 内容分享机制
   - [ ] 新手引导

## 技术栈
- Backend:
  - FastAPI
  - SQLite
  - SQLAlchemy (ORM)
  - Pydantic
  - GLM-4-9B-Chat (本地模型)
  - DeepSeek API
  - pytest
  - LangChain & LangGraph
  - CosyVoice2TTS
- Frontend:
  - 微信小程序原生开发
  - WebSocket
  - 微信音频API

## 开发建议
1. 后端开发重点
   - SQLite数据库设计要简洁实用
   - 使用FastAPI的依赖注入系统
   - 合理使用Pydantic模型验证
   - 异步处理大型计算任务
   - 完善的错误处理
   - 使用FastAPI的内置日志系统

2. 小程序开发注意事项
   - 遵循小程序规范
   - 注意音频播放限制
   - 控制包体积大小
   - 适配不同机型
   - 良好的错误提示
   - 优雅的加载状态

3. 发布策略
   - 先内测收集反馈
   - 逐步开放功能
   - 持续优化体验
   - 关注用户反馈

## 近期开发重点
1. FastAPI后端开发
   - 搭建项目框架
   - 设计SQLite数据模型
   - 开发核心API
   - 集成WebSocket
   - 编写pytest测试用例

2. 准备小程序开发
   - UI设计规范
   - 组件库调研
   - API接口文档
   - 开发环境搭建

## 开发流程建议
1. 后端开发流程
   - FastAPI项目初始化
   - SQLite数据库设计
   - Pydantic模型定义
   - API路由开发
   - 集成已有Agent
   - WebSocket实现
   - pytest测试
   - 自动API文档确认

2. 前端开发流程
   - 界面原型设计
   - 组件开发
   - 页面开发
   - API对接
   - 功能测试
   - 性能优化

3. 测试与部署
   - 接口测试
   - 功能测试
   - 性能测试
   - 部署上线
   - 监控告警