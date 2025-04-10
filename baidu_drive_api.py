"""
百度网盘API服务
提供登录、列出文件和目录、上传、下载和删除文件的API接口
"""

import os
import json
import tempfile
import sys
import logging
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger('baidu_drive_api')

# 创建必要的目录，避免fundrive依赖问题
try:
    # 尝试创建多个可能的目录路径
    for path in [
        '/app/logs', '/app/.fundrive',
        '/tmp/logs', '/tmp/.fundrive',
        './logs', './.fundrive'
    ]:
        os.makedirs(path, exist_ok=True)
        print(f"成功创建目录: {path}")
    logger.info("所有必要目录创建完成")
except Exception as e:
    print(f"创建目录失败: {e}")
    logger.warning(f"创建目录失败: {e}")

# 设置HOME环境变量（如果不存在）
if 'HOME' not in os.environ:
    os.environ['HOME'] = os.environ.get('USERPROFILE', '/tmp')
    print(f"已设置HOME环境变量为: {os.environ['HOME']}")

# 导入百度网盘API
try:
    # 先检查所有依赖包
    import sys
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"Python 路径: {sys.path}")

    # 检查fundrive相关包
    import pkg_resources
    for package in ['numpy', 'pandas', 'funutil', 'funsecret', 'funfile', 'fundrive']:
        try:
            version = pkg_resources.get_distribution(package).version
            logger.info(f"已安装 {package} 版本: {version}")
        except pkg_resources.DistributionNotFound:
            logger.warning(f"未安装 {package}")

    # 尝试导入BaiDuDrive
    from fundrive.drives.baidu.drive import BaiDuDrive
    logger.info("成功导入BaiDuDrive")
except Exception as e:
    logger.error(f"导入BaiDuDrive失败: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise

app = Flask(__name__)

# 全局变量存储客户端实例
client_instances = {}

@app.route('/', methods=['GET'])
def index():
    """API首页"""
    return jsonify({
        "name": "百度网盘API服务",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API信息"},
            {"path": "/health", "method": "GET", "description": "健康检查"},
            {"path": "/login", "method": "POST", "description": "登录百度网盘"},
            {"path": "/list", "method": "GET", "description": "列出文件和目录"},
            {"path": "/upload", "method": "POST", "description": "上传文件"},
            {"path": "/download", "method": "GET", "description": "下载文件"},
            {"path": "/download_link", "method": "GET", "description": "获取文件下载链接"},
            {"path": "/delete", "method": "DELETE", "description": "删除文件"},
            {"path": "/logout", "method": "POST", "description": "登出"}
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "ok", "message": "服务正常运行"})

@app.route('/login', methods=['POST'])
def login():
    """登录接口"""
    data = request.json
    if not data or 'bduss' not in data:
        return jsonify({"status": "error", "message": "缺少bduss参数"}), 400

    bduss = data['bduss']
    session_id = data.get('session_id', bduss[:10])  # 使用bduss前10位作为会话ID

    try:
        # 初始化客户端
        client = BaiDuDrive()
        login_result = client.login(bduss=bduss)

        if login_result:
            # 存储客户端实例
            client_instances[session_id] = client
            return jsonify({
                "status": "success",
                "message": "登录成功",
                "session_id": session_id
            })
        else:
            return jsonify({"status": "error", "message": "登录失败，请检查bduss是否有效"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"登录异常: {str(e)}"}), 500

@app.route('/list', methods=['GET'])
def list_files():
    """列出文件和目录"""
    session_id = request.headers.get('X-Session-ID')
    path = request.args.get('path', '/')

    if not session_id or session_id not in client_instances:
        return jsonify({"status": "error", "message": "未登录或会话已过期"}), 401

    client = client_instances[session_id]

    try:
        # 获取文件和目录列表
        file_list = client.get_file_list(path)
        dir_list = client.get_dir_list(path)

        # 合并并格式化结果
        result = []

        for item in file_list:
            result.append({
                "name": item.name if hasattr(item, 'name') else "未知",
                "type": "file",
                "size": item.size if hasattr(item, 'size') else 0,
                "size_formatted": f"{item.size / (1024 * 1024):.2f} MB" if hasattr(item, 'size') else "0 MB",
                "path": f"{path.rstrip('/')}/{item.name}" if hasattr(item, 'name') else path
            })

        for item in dir_list:
            result.append({
                "name": item.name if hasattr(item, 'name') else "未知",
                "type": "directory",
                "path": f"{path.rstrip('/')}/{item.name}" if hasattr(item, 'name') else path
            })

        return jsonify({
            "status": "success",
            "path": path,
            "items": result,
            "total": len(result)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"获取文件列表异常: {str(e)}"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    session_id = request.headers.get('X-Session-ID')
    remote_path = request.form.get('path', '/')

    if not session_id or session_id not in client_instances:
        return jsonify({"status": "error", "message": "未登录或会话已过期"}), 401

    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "没有文件被上传"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "未选择文件"}), 400

    client = client_instances[session_id]

    try:
        # 保存上传的文件到临时目录
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, filename)
        file.save(temp_file_path)

        # 上传到百度网盘
        remote_file_path = f"{remote_path.rstrip('/')}/{filename}"
        upload_result = client.upload_file(temp_file_path, remote_file_path)

        # 清理临时文件
        os.remove(temp_file_path)
        os.rmdir(temp_dir)

        return jsonify({
            "status": "success",
            "message": "文件上传成功",
            "remote_path": remote_file_path,
            "result": upload_result
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"上传文件异常: {str(e)}"}), 500

@app.route('/download', methods=['GET'])
def download_file():
    """下载文件"""
    session_id = request.headers.get('X-Session-ID')
    file_path = request.args.get('path')

    if not session_id or session_id not in client_instances:
        return jsonify({"status": "error", "message": "未登录或会话已过期"}), 401

    if not file_path:
        return jsonify({"status": "error", "message": "缺少文件路径参数"}), 400

    client = client_instances[session_id]

    try:
        # 创建临时目录用于下载
        temp_dir = tempfile.mkdtemp()
        filename = os.path.basename(file_path)
        temp_file_path = os.path.join(temp_dir, filename)

        # 下载文件
        download_result = client.download_file(file_path, filepath=temp_file_path)

        if os.path.exists(temp_file_path):
            # 发送文件给客户端
            return send_file(
                temp_file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/octet-stream'
            )
        else:
            return jsonify({"status": "error", "message": "文件下载失败"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"下载文件异常: {str(e)}"}), 500

@app.route('/download_link', methods=['GET'])
def get_download_link():
    """获取文件下载链接"""
    session_id = request.headers.get('X-Session-ID')
    file_path = request.args.get('path')

    if not session_id or session_id not in client_instances:
        return jsonify({"status": "error", "message": "未登录或会话已过期"}), 401

    if not file_path:
        return jsonify({"status": "error", "message": "缺少文件路径参数"}), 400

    client = client_instances[session_id]

    try:
        # 获取下载链接
        download_link = client.drive.download_link(file_path)

        return jsonify({
            "status": "success",
            "file_path": file_path,
            "download_link": download_link,
            "note": "下载链接需要带上相应的Cookie才能访问"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"获取下载链接异常: {str(e)}"}), 500

@app.route('/delete', methods=['DELETE'])
def delete_file():
    """删除文件"""
    session_id = request.headers.get('X-Session-ID')
    file_path = request.args.get('path')

    if not session_id or session_id not in client_instances:
        return jsonify({"status": "error", "message": "未登录或会话已过期"}), 401

    if not file_path:
        return jsonify({"status": "error", "message": "缺少文件路径参数"}), 400

    client = client_instances[session_id]

    try:
        # 删除文件
        delete_result = client.delete(file_path)

        return jsonify({
            "status": "success",
            "message": "文件删除成功",
            "file_path": file_path,
            "result": delete_result
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"删除文件异常: {str(e)}"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """登出接口"""
    session_id = request.headers.get('X-Session-ID')

    if session_id and session_id in client_instances:
        # 删除客户端实例
        del client_instances[session_id]
        return jsonify({"status": "success", "message": "登出成功"})

    return jsonify({"status": "warning", "message": "会话不存在或已过期"})

# 如果直接运行此文件
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
