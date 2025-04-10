#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百度网盘HTTP API服务
提供百度网盘功能的RESTful API接口
"""

# 在导入任何库之前设置环境变量
import os
import sys

# 设置HOME环境变量（如果不存在）
if 'HOME' not in os.environ:
    os.environ['HOME'] = os.environ.get('USERPROFILE', '')
    print(f"已设置HOME环境变量为: {os.environ['HOME']}")

# 禁用日志文件写入
os.environ['FUNUTIL_LOG_DISABLE'] = '1'
os.environ['FUNUTIL_LOG_TO_FILE'] = '0'
os.environ['FUNSECRET_DISABLE_LOGS'] = '1'

# 设置日志记录器
import logging

# 配置日志 - 只输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入其他库
import time
import json
import tempfile
import traceback
from flask import Flask, request, jsonify, send_file, Response, send_from_directory
from werkzeug.utils import secure_filename
from functools import wraps

# 导入百度网盘API
# 优先使用自定义的BaiDuDrive
print("尝试导入自定义的BaiDuDrive...")
try:
    from custom_baidu_drive import BaiDuDrive
    print("成功导入自定义的BaiDuDrive")
    USE_REAL_API = True
except Exception as e:
    print(f"导入自定义的BaiDuDrive失败: {e}")
    print("尝试导入真实的BaiDuDrive...")
    try:
        from fundrive.drives.baidu.drive import BaiDuDrive
        print("成功导入真实的BaiDuDrive")
        USE_REAL_API = True
    except Exception as e:
        print(f"导入真实的BaiDuDrive失败: {e}")
        print("错误: 无法导入百度网盘API，请确保已安装fundrive[baidu]库")
        sys.exit(1)

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 限制上传文件大小为1GB
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()  # 使用临时目录存储上传的文件

# 存储BDUSS和客户端实例的字典
clients = {}

# 身份验证装饰器
def require_bduss(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        bduss = request.headers.get('X-Bduss')
        if not bduss:
            return jsonify({"error": "未提供BDUSS，请在请求头中添加X-Bduss"}), 401

        # 检查是否已有客户端实例
        if bduss not in clients:
            try:
                client = BaiDuDrive()
                login_result = client.login(bduss=bduss)
                if not login_result:
                    return jsonify({"error": "BDUSS无效或已过期"}), 401
                clients[bduss] = client
                logger.info(f"创建新的客户端实例，BDUSS: {bduss[:10]}...")
            except Exception as e:
                logger.error(f"创建客户端实例失败: {str(e)}")
                return jsonify({"error": f"创建客户端实例失败: {str(e)}"}), 500

        # 将客户端实例传递给视图函数
        return f(clients[bduss], *args, **kwargs)
    return decorated

@app.route('/')
def index():
    """API首页，显示简单的使用说明"""
    # 如果存在static/index.html，则返回它
    if os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return send_from_directory(app.static_folder, 'index.html')

    # 否则返回JSON数据
    return jsonify({
        "name": "百度网盘API服务",
        "version": "1.0.0",
        "description": "提供百度网盘功能的RESTful API接口",
        "endpoints": [
            {"path": "/api/files", "method": "GET", "description": "列出文件和目录"},
            {"path": "/api/files", "method": "POST", "description": "上传文件"},
            {"path": "/api/files/<path:file_path>", "method": "GET", "description": "获取文件的下载链接"},
            {"path": "/api/files/<path:file_path>", "method": "DELETE", "description": "删除文件"},
            {"path": "/api/quota", "method": "GET", "description": "获取网盘配额信息"}
        ],
        "authentication": "在请求头中添加X-Bduss字段，值为百度网盘的BDUSS"
    })

@app.route('/api/files')
@require_bduss
def list_files(client):
    """列出文件和目录"""
    path = request.args.get('path', '/')

    try:
        # 获取文件列表
        file_list = client.get_file_list(path)
        # 获取目录列表
        dir_list = client.get_dir_list(path)

        # 合并文件和目录列表
        all_items = []

        # 处理目录
        for item in dir_list:
            item_data = {
                "name": item.name if hasattr(item, 'name') else "未知",
                "path": item.path if hasattr(item, 'path') else path + "/" + item.name,
                "type": "directory",
                "size": item.size if hasattr(item, 'size') else 0,
                "size_formatted": f"{item.size / (1024 * 1024):.2f} MB" if hasattr(item, 'size') else "0.00 MB"
            }
            all_items.append(item_data)

        # 处理文件
        for item in file_list:
            item_data = {
                "name": item.name if hasattr(item, 'name') else "未知",
                "path": item.path if hasattr(item, 'path') else path + "/" + item.name,
                "type": "file",
                "size": item.size if hasattr(item, 'size') else 0,
                "size_formatted": f"{item.size / (1024 * 1024):.2f} MB" if hasattr(item, 'size') else "0.00 MB"
            }
            all_items.append(item_data)

        return jsonify({
            "path": path,
            "items": all_items,
            "total": len(all_items)
        })
    except Exception as e:
        logger.error(f"列出文件时出错: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"列出文件时出错: {str(e)}"}), 500

@app.route('/api/files', methods=['POST'])
@require_bduss
def upload_file(client):
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({"error": "未提供文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    remote_path = request.form.get('path', '/')
    if not remote_path.endswith('/'):
        remote_path += '/'

    try:
        # 保存上传的文件到临时目录
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)

        # 上传文件到百度网盘
        remote_file_path = f"{remote_path}{filename}"
        upload_result = client.upload_file(temp_path, remote_file_path)

        # 删除临时文件
        os.remove(temp_path)

        if upload_result:
            return jsonify({
                "success": True,
                "message": f"文件 {filename} 上传成功",
                "path": remote_file_path
            })
        else:
            return jsonify({
                "success": False,
                "error": f"文件 {filename} 上传失败"
            }), 500
    except Exception as e:
        logger.error(f"上传文件时出错: {str(e)}\n{traceback.format_exc()}")
        # 确保临时文件被删除
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": f"上传文件时出错: {str(e)}"}), 500

@app.route('/api/files/<path:file_path>')
@require_bduss
def get_download_link(client, file_path):
    """获取文件的下载链接"""
    try:
        # 确保文件路径以/开头
        if not file_path.startswith('/'):
            file_path = '/' + file_path

        # 获取文件名
        filename = os.path.basename(file_path)

        # 使用底层API获取下载链接
        try:
            download_link = client.drive.download_link(file_path)

            # 生成完整的下载信息
            headers = {
                "User-Agent": "softxm;netdisk",
                "Connection": "Keep-Alive",
                "Cookie": f"BDUSS={client.drive.bduss};ptoken={client.drive.ptoken}",
            }

            return jsonify({
                "success": True,
                "filename": filename,
                "download_link": download_link,
                "headers": headers,
                "message": "下载链接获取成功",
                "note": "注意：下载链接有效期较短，请尽快使用"
            })
        except Exception as e:
            return jsonify({"error": f"获取下载链接失败: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"获取下载链接时出错: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"获取下载链接时出错: {str(e)}"}), 500

@app.route('/api/files/<path:file_path>', methods=['DELETE'])
@require_bduss
def delete_file(client, file_path):
    """删除文件"""
    try:
        # 确保文件路径以/开头
        if not file_path.startswith('/'):
            file_path = '/' + file_path

        # 删除文件
        delete_result = client.delete(file_path)

        if delete_result is None or delete_result:
            return jsonify({
                "success": True,
                "message": f"文件 {file_path} 删除成功"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"文件 {file_path} 删除失败"
            }), 500
    except Exception as e:
        logger.error(f"删除文件时出错: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"删除文件时出错: {str(e)}"}), 500

@app.route('/api/quota')
@require_bduss
def get_quota(client):
    """获取网盘配额信息"""
    try:
        # 获取配额信息
        quota_info = client.get_quota()

        if quota_info:
            total_space = quota_info.get('total', 0) / (1024 * 1024 * 1024)  # 转换为GB
            used_space = quota_info.get('used', 0) / (1024 * 1024 * 1024)    # 转换为GB

            return jsonify({
                "total": quota_info.get('total', 0),
                "used": quota_info.get('used', 0),
                "free": quota_info.get('total', 0) - quota_info.get('used', 0),
                "total_formatted": f"{total_space:.2f} GB",
                "used_formatted": f"{used_space:.2f} GB",
                "free_formatted": f"{total_space - used_space:.2f} GB"
            })
        else:
            return jsonify({"error": "获取配额信息失败"}), 500
    except Exception as e:
        logger.error(f"获取配额信息时出错: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"获取配额信息时出错: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "资源不存在"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "服务器内部错误"}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "上传的文件太大"}), 413

# 添加健康检查端点
@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Service is running",
        "mode": "real",
        "description": "使用真实百度网盘API"
    })

if __name__ == '__main__':
    # 使用环境变量中的端口（如果有），否则使用7860（Hugging Face的默认端口）
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=True)
