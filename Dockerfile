FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有文件
COPY . .

# 设置环境变量
ENV FUNUTIL_LOG_DISABLE=1
ENV FUNUTIL_LOG_TO_FILE=0
ENV PORT=7860

# 暴露端口
EXPOSE 7860

# 设置启动脚本权限
RUN chmod +x start.sh

# 启动服务
CMD ["/bin/bash", "start.sh"]
