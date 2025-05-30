FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 复制 requirements.txt 到容器
COPY requirements.txt /app/requirements.txt

# 使用清华镜像源，升级pip并安装setuptools
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ --upgrade pip setuptools wheel

# 设置pip全局配置
RUN pip config set global.timeout 600 && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# **修改**：先安装 CPU 版的 torch 和 torchaudio
# 使用 PyTorch 官方 CPU 源确保安装 CPU 版本
RUN pip install --no-cache-dir torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu

# **修改**：然后安装 requirements.txt 中的所有依赖
# 因为 torch 和 torchaudio 已经安装，pip 不会再从清华源下载它们
RUN pip install --no-cache-dir -r /app/requirements.txt

# 设置环境变量
ENV PYTHONPATH=/app:/app/backend

# 暴露端口
EXPOSE 8089

# 启动应用
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8089"]
