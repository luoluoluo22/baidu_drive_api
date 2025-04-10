#!/bin/bash

# 设置环境变量
export FUNUTIL_LOG_DISABLE=1
export FUNUTIL_LOG_TO_FILE=0
export FUNSECRET_DISABLE_LOGS=1
export PORT=7860

# 显示环境信息
echo "Python version:"
python --version
echo "Installed packages:"
pip list | grep -E "fundrive|funsecret|funutil"

# 检查自定义驱动文件是否存在
echo "Checking custom driver file..."
ls -la /app/custom_baidu_drive.py

# 确保自定义驱动文件可访问
echo "Ensuring custom driver file is accessible..."
chmod 644 /app/custom_baidu_drive.py 2>/dev/null || echo "Custom driver file not found"

# 启动服务
echo "Starting service..."
gunicorn --bind 0.0.0.0:7860 --timeout 120 --workers 1 baidu_drive_api:app
