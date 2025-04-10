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

# 复制mock_funutil.py到当前目录
echo "Copying mock_funutil.py to current directory..."
cp /app/mock_funutil.py /app/
echo "Copy complete"

# 启动服务
echo "Starting service..."
gunicorn --bind 0.0.0.0:7860 --timeout 120 --workers 1 baidu_drive_api:app
