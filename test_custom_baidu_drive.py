#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试自定义百度网盘驱动
"""

import os
import sys
import time

# 设置HOME环境变量（如果不存在）
if 'HOME' not in os.environ:
    os.environ['HOME'] = os.environ.get('USERPROFILE', '')
    print(f"已设置HOME环境变量为: {os.environ['HOME']}")

# 先测试导入fundrives.baidu模块
print("尝试导入fundrives.baidu模块...")
try:
    import fundrives.baidu
    print("成功导入fundrives.baidu模块")
    print(f"fundrives.baidu模块路径: {fundrives.baidu.__file__}")
except Exception as e:
    print(f"导入fundrives.baidu模块失败: {e}")
    print("请先安装fundrives.baidu模块: pip install fundrives.baidu")
    sys.exit(1)

# 尝试导入自定义的BaiDuDrive
print("尝试导入自定义的BaiDuDrive...")
try:
    from custom_baidu_drive import BaiDuDrive
    print("成功导入自定义的BaiDuDrive")
except Exception as e:
    print(f"导入自定义的BaiDuDrive失败: {e}")
    sys.exit(1)

def test_baidu_drive():
    """测试百度网盘驱动的基本功能"""
    # 从环境变量或命令行参数获取BDUSS
    bduss = os.environ.get('BDUSS') or (sys.argv[1] if len(sys.argv) > 1 else None)

    if not bduss:
        print("错误: 未提供BDUSS，请设置BDUSS环境变量或作为命令行参数传入")
        print("用法: python test_custom_baidu_drive.py YOUR_BDUSS")
        sys.exit(1)

    print(f"使用BDUSS: {bduss[:10]}...")

    # 创建客户端实例
    client = BaiDuDrive()

    # 登录
    print("尝试登录...")
    login_result = client.login(bduss=bduss)
    if not login_result:
        print("登录失败")
        sys.exit(1)
    print("登录成功")

    # 获取根目录文件列表
    print("\n获取根目录文件列表...")
    file_list = client.get_file_list("/")
    print(f"找到 {len(file_list)} 个文件")
    for i, file in enumerate(file_list[:5], 1):  # 只显示前5个文件
        print(f"{i}. {file.name} - {file.size} 字节")
    if len(file_list) > 5:
        print(f"... 还有 {len(file_list) - 5} 个文件未显示")

    # 获取根目录目录列表
    print("\n获取根目录目录列表...")
    dir_list = client.get_dir_list("/")
    print(f"找到 {len(dir_list)} 个目录")
    for i, dir in enumerate(dir_list[:5], 1):  # 只显示前5个目录
        print(f"{i}. {dir.name}")
    if len(dir_list) > 5:
        print(f"... 还有 {len(dir_list) - 5} 个目录未显示")

    # 获取配额信息
    print("\n获取配额信息...")
    quota_info = client.get_quota()
    if quota_info:
        total_space = quota_info.get('total', 0) / (1024 * 1024 * 1024)  # 转换为GB
        used_space = quota_info.get('used', 0) / (1024 * 1024 * 1024)    # 转换为GB
        free_space = total_space - used_space
        print(f"总空间: {total_space:.2f} GB")
        print(f"已使用: {used_space:.2f} GB ({used_space/total_space*100:.2f}%)")
        print(f"剩余空间: {free_space:.2f} GB")
    else:
        print("获取配额信息失败")

    print("\n测试完成")

if __name__ == "__main__":
    test_baidu_drive()
