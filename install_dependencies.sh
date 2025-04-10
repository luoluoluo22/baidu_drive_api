#!/bin/bash

# 设置错误时退出
set -e

echo "开始安装依赖..."

# 安装基础依赖
echo "安装基础依赖..."
pip install --no-cache-dir flask==2.0.1 requests==2.26.0 werkzeug==2.0.1 gunicorn==20.1.0

# 安装数据处理依赖
echo "安装数据处理依赖..."
pip install --no-cache-dir numpy==1.24.3 pandas==1.5.3

# 安装其他可能需要的依赖
echo "安装其他依赖..."
pip install --no-cache-dir python-dateutil>=2.8.2 pytz>=2021.3 six>=1.16.0

# 安装fundrive依赖链
echo "安装fundrive依赖链..."
pip install --no-cache-dir git+https://github.com/farfarfun/funbuild.git
pip install --no-cache-dir git+https://github.com/farfarfun/funfile.git
pip install --no-cache-dir git+https://github.com/farfarfun/funutil.git
pip install --no-cache-dir git+https://github.com/farfarfun/funsecret.git
pip install --no-cache-dir git+https://github.com/farfarfun/fundrive.git

echo "所有依赖安装完成!"
