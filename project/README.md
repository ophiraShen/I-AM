# I-AM 项目

I-AM是一个AI冥想与肯定语生成助手，提供实时对话、肯定语生成和冥想音频生成功能。

## 项目结构

```
I-AM/
├── backend/           # 后端FastAPI应用
│   ├── agents/        # AI代理逻辑
│   ├── config/        # 配置文件
│   ├── static/        # 静态资源
│   └── main.py        # 主入口文件
└── frontend/          # 前端文件
    ├── index.html     # 主HTML页面
    ├── app.js         # JavaScript逻辑
    └── styles.css     # 样式表
```

## Docker部署说明

### 前提条件

- 安装Docker和Docker Compose
- 确保80和8000端口未被占用

### 部署步骤

1. 克隆代码库到服务器

```bash
git clone <repository_url> I-AM
cd I-AM/project
```

2. 确保配置文件正确

确认`.env`文件中的配置参数已正确设置：

```bash
# 检查backend/.env文件
nano backend/.env
```

3. 使用Docker Compose构建和启动服务

```bash
docker-compose up -d --build
```

4. 检查服务状态

```bash
docker-compose ps
```

5. 访问应用

浏览器访问: `http://<服务器IP地址>/`

### 维护操作

- 查看日志：

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
```

- 重启服务：

```bash
docker-compose restart
```

- 停止服务：

```bash
docker-compose down
```

- 更新服务：

```bash
git pull
docker-compose up -d --build
```

## 监控与维护

服务启动后会自动生成以下内容：
- 后端API运行在8000端口
- 前端网页运行在80端口
- 生成的音频将存储在`backend/static/audio`目录

## 问题排查

如果遇到问题，请检查：
1. Docker容器运行状态 `docker-compose ps`
2. 服务日志 `docker-compose logs`
3. 网络连接是否正常
4. 权限和目录路径是否正确 