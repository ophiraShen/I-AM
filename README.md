# I-AM - 基于吸引力法则的个性化冥想助手

## 项目介绍

I-AM 是一款基于吸引力法则理论的智能对话机器人，能够根据用户的情绪状态和需求自动生成个性化冥想音频。作为您的心灵伴侣，I-AM 旨在帮助您缓解压力、提升内心平静，并通过吸引力法则的正向引导，助您实现内心愿望。

### 核心功能

- **智能对话**：与用户自然交流，倾听用户的压力源、生活困扰和内心渴望
- **吸引力法则引导**：基于吸引力法则理论提供正向反馈和引导
- **个性化冥想音频**：根据对话内容动态生成与用户当前情境相关的冥想引导音频
- **肯定语生成**：提供积极的肯定语，帮助用户建立正向思维模式

## 技术架构

I-AM 采用了先进的人工智能技术，主要包括：

- 基于 LangChain 和 LLM 的对话系统
- 基于 LangGraph 的多代理协作框架
- CosyVoice 语音合成技术
- 智能路由系统，自动判断用户需求

## 项目结构

```
I-AM/
├── project/
│   ├── backend/
│   │   ├── agents/           # AI代理逻辑
│   │   ├── config/           # 配置文件
│   │   ├── static/           # 静态资源
│   │   ├── output/           # 生成的音频文件
│   │   └── main.py           # 主入口文件
│   ├── frontend/             # 前端文件
│   │   ├── index.html        # 主HTML页面
│   │   ├── app.js            # JavaScript逻辑
│   │   └── styles.css        # 样式表
│   ├── requirements.txt      # 依赖包
│   └── Dockerfile            # Docker配置文件
├── models/                   # 预训练模型
└── CosyVoice/                # 语音合成引擎
```

## 使用方法

前后端已经完成开发，您可以通过以下方式体验 I-AM：

### 1. 本地运行

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/I-AM.git
cd I-AM

# 安装依赖
pip install -r project/requirements.txt

# 启动应用
cd project/backend
python main.py
```

访问 `http://localhost:8000` 开始使用I-AM

### 2. Docker部署

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/I-AM.git
cd I-AM/project

# 使用Docker Compose构建和启动
docker-compose up -d
```

访问 `http://<服务器IP地址>/` 开始使用

## 已生成的示例冥想音频

您可以在 `project/backend/output/meditation/tts` 目录中找到一些已生成的冥想音频示例：

- 20250117101407.wav
- 20250117173323.wav
- 20250119173232.wav
- 20250420232157.wav

## 技术原理

I-AM 的工作流程如下：

1. **对话理解**：分析用户输入，提取情绪状态、需求和目标
2. **路由判断**：智能判断是提供普通对话、肯定语还是生成冥想音频
3. **冥想生成流程**：
   - 生成冥想大纲（用户情境分析、脚本结构）
   - 创建详细冥想脚本（开场、主体引导、结束）
   - 语音合成（使用CosyVoice2技术）
   - 添加舒缓背景音乐

## 未来计划

- 增加更多类型的冥想主题
- 提供Web界面和移动应用
- 支持更多语言和音色选择
- 个性化数据分析和冥想效果跟踪

## 贡献指南

我们欢迎各种形式的贡献！如果您想参与项目开发，请：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 联系方式

如有任何问题或建议，请联系：ophira.shenyige@outlook.com

## 许可证

本项目采用 [MIT 许可证](LICENSE)

---

*I-AM - 引导你探索内心世界，创造你想要的生活*
