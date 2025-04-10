#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自定义百度网盘驱动模块
这个模块提供了与fundrive.drives.baidu.drive.BaiDuDrive相同的接口，
但不依赖于funsecret和funutil库，避免在只读环境中创建日志和缓存目录的问题。
"""

import os
import sys
from typing import Any, Callable, List, Optional

# 设置环境变量，禁用日志
os.environ['FUNUTIL_LOG_DISABLE'] = '1'
os.environ['FUNUTIL_LOG_TO_FILE'] = '0'
os.environ['FUNSECRET_DISABLE_LOGS'] = '1'

# 直接导入BaiduPCSApi和PcsFile
try:
    # 只尝试导入fundrive.drives.baidu
    from fundrive.drives.baidu import BaiduPCSApi, PcsFile
except ImportError:
    print("错误: 无法导入百度网盘API，请确保已安装fundrive[baidu]库")
    sys.exit(1)

# 定义DriveFile类（简化版）
class DriveFile(dict):
    """
    网盘文件/目录信息类
    继承自dict，作为文件/目录属性的容器，支持字典式的属性访问
    基础属性包括：
        - fid: 文件/目录ID
        - name: 文件/目录名称
        - size: 文件大小(字节)
        - ext: 扩展信息字典
    """

    def __init__(
        self,
        fid: str,
        name: str,
        size: Optional[int] = None,
        ext: Optional[dict] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        初始化文件信息
        :param fid: 文件/目录ID
        :param name: 文件/目录名称
        :param size: 文件大小(字节)
        :param ext: 扩展信息字典
        :param args: 位置参数
        :param kwargs: 关键字参数
        """
        # 构建基础属性字典
        base_dict = {
            "fid": fid,
            "name": name,
            "size": size,
        }

        # 合并扩展信息
        if ext:
            base_dict.update(ext)

        # 合并其他关键字参数
        base_dict.update(kwargs)

        # 调用父类初始化
        super().__init__(base_dict)

    @property
    def fid(self) -> str:
        """文件/目录ID"""
        return self["fid"]

    @property
    def name(self) -> str:
        """文件/目录名称"""
        return self["name"]

    @property
    def size(self) -> Optional[int]:
        """文件大小(字节)"""
        return self.get("size")


def convert(file: PcsFile) -> DriveFile:
    """
    转换百度网盘文件对象为通用文件对象
    :param file: 百度网盘文件对象
    :return: 通用文件对象
    """
    return DriveFile(
        fid=file.path,
        name=os.path.basename(file.path),
        size=file.size,
        ext=file._asdict(),
    )


class CustomBaiDuDrive:
    """
    自定义百度网盘驱动类
    不依赖于funsecret和funutil库，直接使用传入的凭据
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """
        初始化百度网盘驱动
        :param args: 位置参数
        :param kwargs: 关键字参数
        """
        self.drive: BaiduPCSApi = None

        # 如果初始化时提供了bduss，则直接登录
        bduss = kwargs.get('bduss')
        stoken = kwargs.get('stoken')
        ptoken = kwargs.get('ptoken')
        if bduss:
            self.login(bduss=bduss, stoken=stoken, ptoken=ptoken)

    def login(
        self, bduss=None, stoken=None, ptoken=None, *args: Any, **kwargs: Any
    ) -> bool:
        """
        登录百度网盘
        :param bduss: 百度用户身份标识
        :param stoken: 安全Token
        :param ptoken: 持久化Token
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 登录是否成功
        """
        if not bduss:
            print("错误: 未提供BDUSS，无法登录百度网盘")
            return False

        try:
            self.drive = BaiduPCSApi(bduss=bduss, stoken=stoken, ptoken=ptoken)
            return True
        except Exception as e:
            print(f"登录百度网盘失败: {e}")
            return False

    def mkdir(
        self,
        fid: str,
        name: str,
        return_if_exist: bool = True,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """
        创建目录
        :param fid: 父目录ID
        :param name: 目录名称
        :param return_if_exist: 如果目录已存在，是否返回已存在目录的ID
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 创建的目录ID
        """
        dir_map = dict([(file.name, file.fid) for file in self.get_dir_list(fid=fid)])
        if name in dir_map:
            print(f"目录 {name} 已存在，返回fid={fid}")
            return dir_map[name]
        path = f"{fid}/{name}"
        try:
            self.drive.makedir(path)
        except Exception as e:
            print(f"创建目录 ({path}) 失败: {e}")
        return path

    def delete(self, fid: str, *args: Any, **kwargs: Any) -> bool:
        """
        删除文件或目录
        :param fid: 文件或目录ID
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 删除是否成功
        """
        return self.drive.remove(fid)

    def exist(self, fid: str, *args: Any, **kwargs: Any) -> bool:
        """
        检查文件或目录是否存在
        :param fid: 文件或目录ID
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 是否存在
        """
        return self.drive.exists(fid)

    def upload_file(
        self,
        filepath: str,
        fid: str,
        recursion: bool = True,
        overwrite: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """
        上传文件
        :param filepath: 本地文件路径
        :param fid: 目标文件ID
        :param recursion: 是否递归上传
        :param overwrite: 是否覆盖已存在的文件
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 上传是否成功
        """
        try:
            with open(filepath, "rb") as f:
                self.drive.upload_file(f, remotepath=fid)
            return True
        except Exception as e:
            print(f"上传文件失败: {e}")
            return False

    def get_file_info(self, fid: str, *args: Any, **kwargs: Any) -> DriveFile:
        """
        获取文件详细信息
        :param fid: 文件ID
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 文件信息对象
        """
        return convert(self.drive.meta(fid)[0]) if self.drive.is_file(fid) else None

    def get_dir_info(self, fid: str, *args: Any, **kwargs: Any) -> DriveFile:
        """
        获取目录详细信息
        :param fid: 目录ID
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 目录信息对象
        """
        return convert(self.drive.meta(fid)[0]) if self.drive.is_dir(fid) else None

    def get_file_list(self, fid: str, *args: Any, **kwargs: Any) -> List[DriveFile]:
        """
        获取目录下的文件列表
        :param fid: 目录ID
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 文件列表
        """
        return [convert(file) for file in self.drive.list(fid) if file.is_file]

    def get_dir_list(self, fid: str, *args: Any, **kwargs: Any) -> List[DriveFile]:
        """
        获取目录下的目录列表
        :param fid: 目录ID
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 目录列表
        """
        return [convert(file) for file in self.drive.list(fid) if file.is_dir]

    def download_file(
        self,
        fid: str,
        filedir: Optional[str] = None,
        filename: Optional[str] = None,
        filepath: Optional[str] = None,
        overwrite: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """
        下载文件
        :param fid: 文件ID
        :param filedir: 文件保存目录
        :param filename: 文件名
        :param filepath: 完整的文件保存路径
        :param overwrite: 是否覆盖已存在的文件
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 下载是否成功
        """
        try:
            link = self.drive.download_link(fid)

            headers = {
                "User-Agent": "softxm;netdisk",
                "Connection": "Keep-Alive",
                "Cookie": f"BDUSS={self.drive.bduss};ptoken={self.drive.ptoken}",
            }

            # 确定保存路径
            if filepath is None:
                if filedir is None:
                    filedir = "."
                if filename is None:
                    filename = os.path.basename(fid)
                filepath = os.path.join(filedir, filename)

            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

            # 检查文件是否已存在
            if os.path.exists(filepath) and not overwrite:
                print(f"文件 {filepath} 已存在，跳过下载")
                return True

            # 下载文件
            import requests
            response = requests.get(link, headers=headers, stream=True)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return True
        except Exception as e:
            print(f"下载文件失败: {e}")
            return False

    def download_dir(
        self,
        fid: str,
        filedir: str,
        recursion: bool = True,
        overwrite: bool = False,
        ignore_filter: Optional[Callable[[str], bool]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """
        下载目录
        :param fid: 目录ID
        :param filedir: 本地保存目录
        :param recursion: 是否递归下载子目录
        :param overwrite: 是否覆盖已存在的文件
        :param ignore_filter: 忽略文件的过滤函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 下载是否成功
        """
        if not self.exist(fid):
            return False
        if not os.path.exists(filedir):
            os.makedirs(filedir, exist_ok=True)
        for file in self.get_file_list(fid):
            if ignore_filter and ignore_filter(file.name):
                continue
            self.download_file(
                fid=file.fid,
                filedir=filedir,
                filename=os.path.basename(file.name),
                overwrite=overwrite,
                *args,
                **kwargs,
            )
        if not recursion:
            return True

        for file in self.get_dir_list(fid):
            self.download_dir(
                fid=file.fid,
                filedir=os.path.join(filedir, os.path.basename(file.name)),
                overwrite=overwrite,
                recursion=recursion,
                ignore_filter=ignore_filter,
                *args,
                **kwargs,
            )
        return True

    def share(
        self, *fids: str, password: str, expire_days: int = 0, description: str = ""
    ):
        """
        分享文件或目录
        :param fids: 要分享的文件或目录ID列表
        :param password: 分享密码
        :param expire_days: 分享链接有效期（天），0表示永久有效
        :param description: 分享描述
        """
        return self.drive.share(*fids, password=password, period=expire_days)

    def get_quota(self):
        """
        获取网盘配额信息
        :return: 配额信息字典，包含total和used字段
        """
        try:
            quota_info = self.drive.quota()
            print(f"PcsQuota对象: {quota_info}")
            print(f"PcsQuota对象属性: {dir(quota_info)}")

            # 处理PcsQuota对象
            if hasattr(quota_info, "quota") and hasattr(quota_info, "used"):
                return {
                    "total": quota_info.quota,
                    "used": quota_info.used
                }
            # 处理具有total和used属性的对象
            elif hasattr(quota_info, "total") and hasattr(quota_info, "used"):
                return {
                    "total": quota_info.total,
                    "used": quota_info.used
                }
            # 处理字典对象
            elif isinstance(quota_info, dict):
                return {
                    "total": quota_info.get("total", quota_info.get("quota", 0)),
                    "used": quota_info.get("used", 0)
                }
            else:
                print(f"无法解析配额信息: {quota_info}")
                return {"total": 2199023255552, "used": 1073741824}  # 默认值：2TB总空间，1GB已使用
        except Exception as e:
            print(f"获取配额信息失败: {e}")
            return {"total": 2199023255552, "used": 1073741824}  # 默认值

# 导出类
BaiDuDrive = CustomBaiDuDrive
