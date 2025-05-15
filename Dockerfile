# 构建阶段
FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04 AS builder

WORKDIR /build

# 设置非交互式安装
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# 安装基本依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 配置pip镜像
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && pip3 config set global.trusted-host mirrors.aliyun.com

# 安装PyTorch 2.6.0
RUN pip3 install --no-cache-dir torch==2.6.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 复制requirements
COPY requirements.txt .

# 安装依赖
RUN pip3 install --no-cache-dir pynini==2.1.5 \
    && pip3 install --no-cache-dir -r requirements.txt

# 最终镜像
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# 安装Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 创建软链接使python命令可用
RUN ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip

# 从构建阶段复制Python包
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . /app/

# 设置环境变量
ENV PYTHONPATH="/app:/app/CosyVoice:/app/CosyVoice/third_party/Matcha-TTS"

# 暴露端口
EXPOSE 8089

# 启动命令
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8089"]