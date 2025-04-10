FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 创建必要的目录
RUN mkdir -p /app/logs /app/.fundrive /tmp/logs /tmp/.fundrive

# 设置环境变量
ENV HOME=/app \
    FUNUTIL_LOG_DISABLE=1 \
    FUNUTIL_LOG_TO_FILE=0 \
    PYTHONUNBUFFERED=1

# 复制安装脚本和依赖文件
COPY requirements.txt install_dependencies.sh ./
RUN chmod +x install_dependencies.sh

# 安装依赖
RUN ./install_dependencies.sh

# 复制应用代码
COPY . .

# 创建启动脚本
RUN echo '#!/bin/bash\n\
echo "Creating necessary directories..."\n\
mkdir -p /app/logs /app/.fundrive /tmp/logs /tmp/.fundrive\n\
echo "Starting API service..."\n\
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120' > start.sh \
    && chmod +x start.sh

# 暴露端口
EXPOSE 10000

# 启动服务
CMD ["/bin/bash", "start.sh"]
