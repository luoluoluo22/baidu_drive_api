#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模拟百度网盘API模块
这个模块提供了与真实百度网盘API相同的接口，但不依赖于fundrive库
"""

import os
import sys
import json
import time
import random
import string
from typing import List, Dict, Any, Optional, Union

# 模拟文件和目录类
class FileItem:
    def __init__(self, name, path, size=1024, is_dir=False):
        self.name = name
        self.path = path
        self.size = size
        self.is_dir = is_dir
        self.server_filename = name
        self.server_mtime = int(time.time())
        self.local_mtime = int(time.time())
        self.md5 = ''.join(random.choices(string.hexdigits, k=32)).lower()
        self.fs_id = random.randint(10000000000000, 99999999999999)

# 模拟百度网盘API
class BaiDuDrive:
    def __init__(self):
        self.drive = self
        self.bduss = None
        self.ptoken = None
        self.stoken = None
        self.files = {}  # 存储模拟的文件系统
        self.quota = {"total": 2199023255552, "used": 1073741824}  # 2TB总空间，1GB已使用
        print("创建了模拟的BaiDuDrive实例")
        
        # 初始化一些示例文件和目录
        self._init_sample_files()
    
    def _init_sample_files(self):
        # 创建一些示例文件和目录
        self.files["/"] = []
        
        # 添加一些目录
        for dirname in ["文档", "图片", "视频", "音乐", "下载"]:
            dir_item = FileItem(dirname, f"/{dirname}", 0, True)
            self.files["/"].append(dir_item)
            self.files[f"/{dirname}"] = []
        
        # 在文档目录中添加一些文件
        for filename in ["工作计划.docx", "学习笔记.txt", "重要文档.pdf"]:
            file_item = FileItem(filename, f"/文档/{filename}", random.randint(10240, 1024000))
            self.files["/文档"].append(file_item)
        
        # 在图片目录中添加一些文件
        for filename in ["照片1.jpg", "照片2.png", "截图.gif"]:
            file_item = FileItem(filename, f"/图片/{filename}", random.randint(102400, 5120000))
            self.files["/图片"].append(file_item)
    
    def login(self, bduss=None):
        """登录百度网盘"""
        self.bduss = bduss
        self.ptoken = "fake_ptoken_" + ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        self.stoken = "fake_stoken_" + ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        print(f"模拟登录成功，bduss: {bduss[:10] if bduss else None}...")
        return True
    
    def get_file_list(self, path="/"):
        """获取文件列表"""
        print(f"模拟获取文件列表，路径: {path}")
        if path in self.files:
            return [item for item in self.files[path] if not item.is_dir]
        return []
    
    def get_dir_list(self, path="/"):
        """获取目录列表"""
        print(f"模拟获取目录列表，路径: {path}")
        if path in self.files:
            return [item for item in self.files[path] if item.is_dir]
        return []
    
    def upload_file(self, local_path, remote_path):
        """上传文件"""
        print(f"模拟上传文件，本地路径: {local_path}，远程路径: {remote_path}")
        
        # 获取文件名和目录
        filename = os.path.basename(remote_path)
        dirname = os.path.dirname(remote_path)
        
        # 确保目录存在
        if dirname not in self.files:
            self.files[dirname] = []
        
        # 获取文件大小
        try:
            size = os.path.getsize(local_path)
        except:
            size = random.randint(1024, 1024000)
        
        # 创建文件项
        file_item = FileItem(filename, remote_path, size)
        
        # 添加到文件系统
        self.files[dirname].append(file_item)
        
        # 更新已使用空间
        self.quota["used"] += size
        
        return True
    
    def delete(self, path):
        """删除文件或目录"""
        print(f"模拟删除文件，路径: {path}")
        
        # 获取文件名和目录
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)
        
        # 确保目录存在
        if dirname not in self.files:
            return False
        
        # 查找文件
        for i, item in enumerate(self.files[dirname]):
            if item.name == filename:
                # 删除文件
                del self.files[dirname][i]
                
                # 更新已使用空间
                self.quota["used"] -= item.size
                
                return True
        
        return False
    
    def get_quota(self):
        """获取网盘配额信息"""
        print("模拟获取配额信息")
        return self.quota
    
    def download_link(self, path):
        """获取下载链接"""
        print(f"模拟获取下载链接，路径: {path}")
        
        # 生成一个随机的下载链接
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        return f"https://d.pcs.baidu.com/file/{random_id}?filename={os.path.basename(path)}"

# 导出模块
sys.modules['fundrive'] = type('MockModule', (), {})
sys.modules['fundrive.drives'] = type('MockModule', (), {})
sys.modules['fundrive.drives.baidu'] = type('MockModule', (), {})
sys.modules['fundrive.drives.baidu.drive'] = type('MockModule', (), {'BaiDuDrive': BaiDuDrive})

# 导出类
__all__ = ['BaiDuDrive']
