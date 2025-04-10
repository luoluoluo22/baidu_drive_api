#!/bin/bash

# 设置环境变量
export FUNUTIL_LOG_DISABLE=1
export FUNUTIL_LOG_TO_FILE=0
export FUNSECRET_DISABLE_LOGS=1
export PORT=7860

# 创建一个空的logs目录，防止fundrive库尝试创建它时失败
echo "Creating logs directory..."
mkdir -p logs
chmod 777 logs
echo "Creating .gitignore file in logs directory..."
touch logs/.gitignore
chmod 666 logs/.gitignore
echo "Logs directory setup complete"

# 显示环境信息
echo "Python version:"
python --version
echo "Installed packages:"
pip list | grep -E "fundrive|funsecret|funutil"

# 启动服务
echo "Starting service..."
gunicorn --bind 0.0.0.0:7860 --timeout 120 --workers 1 baidu_drive_api:app
