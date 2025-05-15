FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 使用阿里云镜像源，升级pip并安装setuptools
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip setuptools wheel

# 设置pip全局配置
RUN pip config set global.timeout 600 && \
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

# 只安装Web服务必须的核心依赖
RUN pip install --no-cache-dir --retries 5 \
    fastapi==0.115.12 \
    uvicorn==0.30.0 \
    python-multipart==0.0.19 \
    aiosqlite==0.21.0 \
    python-dotenv==1.0.1 \
    pyyaml>=6.0.1 \
    websockets==11.0.3 \
    httpx==0.28.1

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8089

# 启动应用
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8089"]
