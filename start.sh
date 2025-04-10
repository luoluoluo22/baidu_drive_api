#!/bin/bash

# 设置环境变量
export FUNUTIL_LOG_DISABLE=1
export FUNUTIL_LOG_TO_FILE=0
export PORT=7860

# 创建一个空的logs目录，防止fundrive库尝试创建它时失败
mkdir -p logs
touch logs/.gitignore

# 启动服务
gunicorn --bind 0.0.0.0:7860 --timeout 120 --workers 1 baidu_drive_api:app
