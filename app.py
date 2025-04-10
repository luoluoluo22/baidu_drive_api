#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百度网盘API服务 - Render启动脚本
"""

# 导入应用程序
from baidu_drive_api import app

# 这个文件会被Render自动识别并运行
if __name__ == "__main__":
    # 使用环境变量中的端口（Render会自动设置PORT环境变量）
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
