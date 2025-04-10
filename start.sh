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

# 检查模拟模块文件是否存在
echo "Checking mock module files..."
ls -la /app/mock_*.py

# 确保模拟模块文件可访问
echo "Ensuring mock module files are accessible..."
chmod 644 /app/mock_*.py 2>/dev/null || echo "No mock files to chmod"

# 显示文件内容
echo "Displaying mock module files content..."
cat /app/mock_*.py 2>/dev/null || echo "No mock files to display"

# 启动服务
echo "Starting service..."
gunicorn --bind 0.0.0.0:7860 --timeout 120 --workers 1 baidu_drive_api:app
