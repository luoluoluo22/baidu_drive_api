#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模拟funutil模块，用于替换原始模块
这个模块提供了与原始funutil模块相同的接口，但不会尝试创建logs目录或写入日志文件
"""

import sys
import logging

# 创建一个空的日志记录器
class DummyLogger:
    def __init__(self, name=None):
        self.name = name or "dummy"
    
    def debug(self, msg, *args, **kwargs):
        pass
    
    def info(self, msg, *args, **kwargs):
        pass
    
    def warning(self, msg, *args, **kwargs):
        pass
    
    def error(self, msg, *args, **kwargs):
        pass
    
    def critical(self, msg, *args, **kwargs):
        pass
    
    def exception(self, msg, *args, **kwargs):
        pass
    
    def log(self, level, msg, *args, **kwargs):
        pass

# 模拟funutil.util.log模块
class LogModule:
    def get_logger(self, name=None):
        return DummyLogger(name)
    
    def getLogger(self, name=None):
        return DummyLogger(name)

# 模拟funutil.util模块
class UtilModule:
    def __init__(self):
        self.log = LogModule()
        
    def deep_get(self, obj, path, default=None):
        return default
    
    def get_logger(self, name=None):
        return self.log.get_logger(name)
    
    def getLogger(self, name=None):
        return self.log.getLogger(name)
    
    def get_package_version(self, package_name):
        return "0.0.0"
    
    def find_get(self, obj, keys, default=None):
        return default

# 创建模拟的funutil模块
class FunUtilModule:
    def __init__(self):
        self.util = UtilModule()
    
    def deep_get(self, obj, path, default=None):
        return self.util.deep_get(obj, path, default)
    
    def get_logger(self, name=None):
        return self.util.get_logger(name)
    
    def getLogger(self, name=None):
        return self.util.getLogger(name)
    
    def get_package_version(self, package_name):
        return self.util.get_package_version(package_name)
    
    def find_get(self, obj, keys, default=None):
        return self.util.find_get(obj, keys, default)

# 创建模拟模块实例
mock_funutil = FunUtilModule()

# 导出模块中的函数和类
deep_get = mock_funutil.deep_get
get_logger = mock_funutil.get_logger
getLogger = mock_funutil.getLogger
get_package_version = mock_funutil.get_package_version
find_get = mock_funutil.find_get

# 注入模拟模块到sys.modules
sys.modules['funutil'] = mock_funutil
sys.modules['funutil.util'] = mock_funutil.util
sys.modules['funutil.util.log'] = mock_funutil.util.log

print("已成功注入模拟的funutil模块")
