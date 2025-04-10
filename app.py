#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百度网盘API服务 - Hugging Face启动脚本
"""

# 导入应用程序
from baidu_drive_api import app

# 这个文件会被Hugging Face自动识别并运行
if __name__ == "__main__":
    # 使用环境变量中的端口（如果有），否则使用7860（Hugging Face的默认端口）
    import os
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
