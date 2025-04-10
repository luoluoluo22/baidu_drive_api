#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百度网盘API服务健康检查脚本
用于Hugging Face检查服务是否正常运行
"""

import os
import sys
import time
import requests

def check_health():
    """检查服务是否正常运行"""
    port = os.environ.get('PORT', 7860)
    url = f"http://localhost:{port}/health"
    
    # 尝试连接服务
    max_retries = 10
    retry_interval = 3  # 秒
    
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    print(f"服务正常运行: {data}")
                    return True
            print(f"服务返回异常状态码: {response.status_code}")
        except Exception as e:
            print(f"尝试 {i+1}/{max_retries} 连接服务失败: {e}")
        
        if i < max_retries - 1:
            print(f"等待 {retry_interval} 秒后重试...")
            time.sleep(retry_interval)
    
    print("健康检查失败，服务可能未正常运行")
    return False

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)
