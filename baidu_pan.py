
"""
百度网盘操作示例脚本
功能：登录、列出文件和目录、上传、下载和删除文件
使用方法：python test_fundrive_complete.py
"""

import os
import sys
import time
import shutil

# 设置HOME环境变量（如果不存在）
if 'HOME' not in os.environ:
    os.environ['HOME'] = os.environ.get('USERPROFILE', '')
    print(f"已设置HOME环境变量为: {os.environ['HOME']}")

# 导入百度网盘API
from fundrive.drives.baidu.drive import BaiDuDrive

def main():
    # 使用bduss参数初始化百度网盘客户端
    # 请替换为您自己的bduss值
    bduss = "YOUR_BDUSS_HERE"

    try:
        print("=== 1. 初始化和登录 ===")
        client = BaiDuDrive()
        login_result = client.login(bduss=bduss)
        if login_result:
            print("登录成功!")
        else:
            print("登录失败!")
            return
    except Exception as e:
        print(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 创建测试目录
    test_dir = "baidu_test"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)

    try:
        print("\n=== 2. 列出根目录内容 ===")
        # 获取文件列表
        file_list = client.get_file_list("/")
        # 获取目录列表
        dir_list = client.get_dir_list("/")

        # 合并文件和目录列表
        all_items = file_list + dir_list

        if all_items:
            print(f"找到 {len(all_items)} 个文件/文件夹:")
            for i, item in enumerate(all_items, 1):
                item_type = "文件夹" if hasattr(item, 'is_dir') and item.is_dir else "文件"
                item_name = item.name if hasattr(item, 'name') else "未知"
                item_size = item.size / (1024 * 1024) if hasattr(item, 'size') else 0  # 转换为MB
                print(f"  {i}. {item_name} ({item_type}, {item_size:.2f} MB)")
        else:
            print("根目录为空")
    except Exception as e:
        print(f"列出文件时出错: {e}")
        import traceback
        traceback.print_exc()

    # 创建一个测试文件
    test_content = f"这是一个测试文件，创建于 {time.strftime('%Y-%m-%d %H:%M:%S')}"
    test_filename = "test_file.txt"
    local_test_file = os.path.join(test_dir, test_filename)

    try:
        print(f"\n=== 3. 上传文件 ===")
        # 创建本地测试文件
        with open(local_test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"本地测试文件创建成功: {local_test_file}")

        # 上传测试文件
        upload_result = client.upload_file(local_test_file, f"/{test_filename}")
        print(f"上传结果: {upload_result}")

        # 列出根目录文件，确认文件已上传
        file_list = client.get_file_list("/")
        if file_list:
            print(f"上传后根目录文件列表:")
            for i, file_info in enumerate(file_list, 1):
                file_name = file_info.name if hasattr(file_info, 'name') else "未知"
                file_size = file_info.size / (1024 * 1024) if hasattr(file_info, 'size') else 0  # 转换为MB
                print(f"  {i}. {file_name} ({file_size:.2f} MB)")
        else:
            print("未找到上传的文件")
    except Exception as e:
        print(f"上传文件时出错: {e}")
        import traceback
        traceback.print_exc()

    try:
        print(f"\n=== 4. 下载文件 ===")
        # 创建下载目录
        download_dir = os.path.join(test_dir, "downloads")
        os.makedirs(download_dir, exist_ok=True)

        # 方式1：使用filedir和filename参数
        download_path1 = os.path.join(download_dir, "method1")
        os.makedirs(download_path1, exist_ok=True)
        download_result1 = client.download_file(
            f"/{test_filename}",
            filedir=download_path1,
            filename=f"downloaded_{test_filename}"
        )
        print(f"下载方式1结果: {download_result1}")

        # 方式2：使用filepath参数
        download_path2 = os.path.join(download_dir, "method2", f"downloaded_{test_filename}")
        os.makedirs(os.path.dirname(download_path2), exist_ok=True)
        download_result2 = client.download_file(
            f"/{test_filename}",
            filepath=download_path2
        )
        print(f"下载方式2结果: {download_result2}")

        # 方式3：使用底层API
        download_path3 = os.path.join(download_dir, "method3", f"downloaded_{test_filename}")
        os.makedirs(os.path.dirname(download_path3), exist_ok=True)
        try:
            download_link = client.drive.download_link(f"/{test_filename}")

            # 使用requests库直接下载文件
            import requests
            headers = {
                "User-Agent": "softxm;netdisk",
                "Connection": "Keep-Alive",
                "Cookie": f"BDUSS={client.drive.bduss};ptoken={client.drive.ptoken}",
            }
            response = requests.get(download_link, headers=headers, stream=True)
            if response.status_code == 200:
                with open(download_path3, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"下载方式3结果: 成功")
            else:
                print(f"下载方式3结果: 失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"下载方式3结果: 失败，错误: {e}")

        # 检查下载的文件
        print("\n下载的文件内容验证:")
        for method, path in [
            ("方式1", os.path.join(download_path1, f"downloaded_{test_filename}")),
            ("方式2", download_path2),
            ("方式3", download_path3)
        ]:
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"  {method} - 文件内容: {content}")

                    # 验证文件内容是否一致
                    if content == test_content:
                        print(f"  {method} - 文件内容验证成功")
                    else:
                        print(f"  {method} - 文件内容验证失败")
                else:
                    print(f"  {method} - 文件不存在: {path}")
            except Exception as e:
                print(f"  {method} - 读取文件内容时出错: {e}")
    except Exception as e:
        print(f"下载文件时出错: {e}")
        import traceback
        traceback.print_exc()

    try:
        print(f"\n=== 5. 删除文件 ===")
        # 删除测试文件
        delete_result = client.delete(f"/{test_filename}")
        print(f"删除结果: {delete_result}")

        # 列出根目录文件，确认文件已删除
        file_list = client.get_file_list("/")
        if file_list:
            print(f"删除后根目录文件列表:")
            for i, file_info in enumerate(file_list, 1):
                file_name = file_info.name if hasattr(file_info, 'name') else "未知"
                file_size = file_info.size / (1024 * 1024) if hasattr(file_info, 'size') else 0  # 转换为MB
                print(f"  {i}. {file_name} ({file_size:.2f} MB)")
        else:
            print("根目录下没有文件，删除成功")
    except Exception as e:
        print(f"删除文件时出错: {e}")
        import traceback
        traceback.print_exc()

    # 清理本地测试文件
    try:
        print(f"\n=== 6. 清理本地文件 ===")
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        print("本地测试文件清理完成")
    except Exception as e:
        print(f"清理本地文件时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始执行百度网盘操作示例脚本...")
    main()
    print("脚本执行完成!")
