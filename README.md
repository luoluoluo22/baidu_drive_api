# 百度网盘API服务

这是一个基于Flask的百度网盘API服务，提供了百度网盘的主要功能的RESTful API接口。

本服务支持两种模式：
1. **真实模式**：如果环境中安装了fundrive[baidu]库，将使用真实的百度网盘API
2. **模拟模式**：如果环境中没有安装fundrive[baidu]库，将使用模拟的API（仅用于演示）

## 使用方法

1. 在请求头中添加`X-Bduss`字段，值为百度网盘的BDUSS
2. 调用相应的API端点

## 获取BDUSS

BDUSS可以从浏览器Cookie中获取：
1. 登录百度网盘网页版
2. 打开浏览器开发者工具（F12）
3. 切换到"应用"或"Application"选项卡
4. 在左侧找到"Cookies"，然后选择百度网盘的域名
5. 在右侧找到名为"BDUSS"的Cookie，其值就是BDUSS

## API端点

### 1. 列出文件和目录

```
GET /api/files?path=/
```

### 2. 上传文件

```
POST /api/files
```

### 3. 获取文件的下载链接

```
GET /api/files/<file_path>
```

### 4. 删除文件

```
DELETE /api/files/<file_path>
```

### 5. 获取网盘配额信息

```
GET /api/quota
```

## 示例

使用curl获取根目录文件列表：

```bash
curl -H "X-Bduss: YOUR_BDUSS_VALUE" https://your-space-name.hf.space/api/files
```

获取文件的下载链接：

```bash
curl -H "X-Bduss: YOUR_BDUSS_VALUE" https://your-space-name.hf.space/api/files/test.txt
```

## 注意事项

1. BDUSS是敏感信息，请妥善保管，不要泄露给他人
2. 下载链接的有效期较短，请尽快使用
3. 服务默认限制上传文件大小为1GB

## 当前服务状态

本服务在Hugging Face上运行，可能会使用模拟模式。如果您需要使用真实的百度网盘API，可以将代码下载到本地运行。

您可以通过访问 `/health` 端点来检查服务是否正常运行，以及当前使用的是真实模式还是模拟模式。

## 源代码

完整源代码和详细文档可在GitHub上获取：[百度网盘API服务](https://github.com/your-username/baidu-drive-api)

## 关于模拟模式

如果服务在模拟模式下运行，将会返回模拟的数据，而不是真实的百度网盘数据。这种模式下：

1. 列出文件和目录将返回空列表
2. 上传文件将返回成功，但实际上没有上传
3. 获取下载链接将返回一个假的链接
4. 删除文件将返回成功，但实际上没有删除
5. 获取配额信息将返回固定的数据
