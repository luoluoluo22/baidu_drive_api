# 自定义百度网盘驱动

这个项目提供了一个自定义的百度网盘驱动实现，解决了在Hugging Face等只读环境中使用fundrive[baidu]库时遇到的问题。

## 问题背景

原始的百度网盘驱动（fundrive.drives.baidu.drive.BaiDuDrive）依赖于以下几个库：

- fundrives.baidu - 提供百度网盘API的核心功能
- funget - 用于下载文件
- funsecret - 用于读取密钥
- funutil - 用于日志记录

问题主要出在funsecret和funutil这两个库上，它们尝试创建日志目录和缓存目录，而这在Hugging Face的只读环境中是不允许的。

## 解决方案

我们创建了一个自定义的百度网盘驱动（custom_baidu_drive.py），它：

1. 不依赖于funsecret和funutil库
2. 直接使用传入的凭据，而不是尝试从文件中读取
3. 使用简单的print语句代替日志记录
4. 保持与原始BaiDuDrive类相同的接口，以确保兼容性

## 使用方法

### 1. 安装依赖

```bash
pip install fundrives.baidu
```

### 2. 使用自定义驱动

```python
from custom_baidu_drive import BaiDuDrive

# 创建客户端实例
client = BaiDuDrive()

# 登录（必须提供bduss）
client.login(bduss="YOUR_BDUSS_HERE")

# 使用客户端
file_list = client.get_file_list("/")
for file in file_list:
    print(file.name, file.size)
```

### 3. 在API服务中使用

我们的`baidu_drive_api.py`文件已经配置为优先使用自定义驱动，按照以下顺序尝试导入：

1. 首先尝试导入自定义的BaiDuDrive（custom_baidu_drive.py）
2. 如果失败，尝试导入模拟的BaiDuDrive（mock_baidu_drive.py）
3. 如果仍然失败，尝试导入真实的BaiDuDrive（fundrive.drives.baidu.drive.BaiDuDrive）
4. 如果所有导入都失败，使用内置的模拟类

## 获取BDUSS

BDUSS是百度网盘的用户身份标识，可以从浏览器Cookie中获取：

1. 登录百度网盘网页版
2. 打开浏览器开发者工具（F12）
3. 切换到"应用"或"Application"选项卡
4. 在左侧找到"Cookies"，然后选择百度网盘的域名
5. 在右侧找到名为"BDUSS"的Cookie，其值就是BDUSS

## 注意事项

- 自定义驱动仍然依赖于fundrives.baidu库，但不依赖于funsecret和funutil
- 在使用自定义驱动时，必须显式提供bduss参数，因为它不会尝试从文件中读取
- 自定义驱动的日志记录功能有限，主要用于调试目的
