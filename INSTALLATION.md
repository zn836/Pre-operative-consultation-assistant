# 安装和部署指南

本文档提供详细的安装和部署步骤,帮助您快速搭建术前谈话助手系统。

## 系统要求

### 硬件要求
- **CPU**: 双核及以上
- **内存**: 4GB RAM (推荐 8GB)
- **存储**: 至少 500MB 可用空间(不含视频文件)
- **网络**: 稳定的互联网连接(用于API调用)

### 软件要求
- **操作系统**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 或更高版本
- **浏览器**: Chrome 90+, Edge 90+, Firefox 88+ (推荐Chrome)

---

## 安装步骤

### 方法一: 标准安装 (推荐)

#### 1. 安装 Python

**Windows**:
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载 Python 3.8+ 安装包
3. 运行安装程序,**勾选 "Add Python to PATH"**
4. 验证安装:
```bash
python --version
```

**macOS**:
```bash
# 使用 Homebrew 安装
brew install python3

# 验证安装
python3 --version
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install python3 python3-pip

# 验证安装
python3 --version
```

#### 2. 下载项目

**选项A: 直接下载**
- 将项目文件夹复制到本地
- 例如: `C:\Users\YourName\video_qa_assistant`

**选项B: 使用Git (如果项目在代码仓库)**
```bash
git clone <项目地址>
cd video_qa_assistant
```

#### 3. 安装依赖包

打开命令行,进入项目文件夹:

**Windows**:
```bash
cd "C:\Users\YourName\video_qa_assistant"
pip install streamlit requests python-dotenv
```

**macOS/Linux**:
```bash
cd /path/to/video_qa_assistant
pip3 install streamlit requests python-dotenv
```

**或者使用 requirements.txt** (如果有):
```bash
pip install -r requirements.txt
```

#### 4. 准备视频和字幕文件

1. 确认项目根目录下有 `video` 文件夹
   ```bash
   # Windows
   mkdir video

   # macOS/Linux
   mkdir -p video
   ```

2. 将视频文件放入 `video` 文件夹:
   - 支持格式: `.mp4`, `.avi`, `.mov`
   - 建议命名: `1.mp4`, `2.mp4` 等

3. 准备对应的字幕文件:
   - 与视频同名,扩展名为 `.txt`
   - 例如: `1.mp4` 对应 `1.txt`

**字幕文件格式示例** (`video/1.txt`):
```
[00:00:00.620 - 00:00:12.300] 各位患者和家属大家好,我是心内科的XXX医生
[00:00:12.300 - 00:00:25.500] 今天我们来讲一下术前需要做哪些准备
[00:00:25.500 - 00:00:40.200] 首先第一点,术前需要完善相关检查
```

#### 5. 配置API (可选)

**当前配置已内置在代码中**,如需修改:

编辑 `app.py` 文件的第13-15行:
```python
API_BASE_URL = "http://58.34.97.143:4000/v1/chat/completions"
API_KEY = "sk-9jWCuocCFjkCRWVvdtwG"
MODEL_NAME = "openai/gpt-oss-120b"
```

**或者使用环境变量** (需要修改代码读取方式):

创建 `.env` 文件:
```env
API_BASE_URL=http://58.34.97.143:4000/v1/chat/completions
API_KEY=sk-9jWCuocCFjkCRWVvdtwG
MODEL_NAME=openai/gpt-oss-120b
```

#### 6. 启动应用

**Windows**:
```bash
streamlit run app.py
```

**macOS/Linux**:
```bash
streamlit run app.py
```

#### 7. 访问应用

浏览器会自动打开 `http://localhost:8501`

如果没有自动打开,手动访问该地址。

---

### 方法二: 虚拟环境安装 (推荐用于开发)

使用虚拟环境可以避免依赖冲突。

#### Windows

```bash
# 1. 进入项目目录
cd "C:\Users\YourName\video_qa_assistant"

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
venv\Scripts\activate

# 4. 安装依赖
pip install streamlit requests python-dotenv

# 5. 启动应用
streamlit run app.py

# 6. 退出虚拟环境(使用完毕后)
deactivate
```

#### macOS/Linux

```bash
# 1. 进入项目目录
cd /path/to/video_qa_assistant

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 安装依赖
pip install streamlit requests python-dotenv

# 5. 启动应用
streamlit run app.py

# 6. 退出虚拟环境(使用完毕后)
deactivate
```

---

## 完整项目结构

安装完成后,项目结构应该如下:

```
video_qa_assistant/
├── app.py                      # 主应用程序
├── prompts.py                  # AI提示词配置
├── README.md                   # 项目介绍文档
├── USER_GUIDE.md              # 用户使用指南
├── INSTALLATION.md            # 本安装文档
├── .env                       # 环境变量配置(可选)
├── requirements.txt           # Python依赖列表(可选)
├── video/                     # 视频资源文件夹
│   ├── 1.mp4                 # 视频文件
│   └── 1.txt                 # 对应字幕文件
└── venv/                      # 虚拟环境(如使用)
```

---

## 依赖包说明

### 核心依赖

| 包名 | 版本要求 | 用途 |
|------|---------|------|
| streamlit | >= 1.28.0 | Web应用框架 |
| requests | >= 2.31.0 | HTTP请求,调用API |
| python-dotenv | >= 1.0.0 | 环境变量管理 |

### 创建 requirements.txt

如果需要创建 `requirements.txt` 文件:

```bash
# 激活虚拟环境后
pip freeze > requirements.txt
```

或手动创建 `requirements.txt`:
```
streamlit>=1.28.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## 配置说明

### API 配置

#### 当前内置配置
系统默认使用以下API配置(在 `app.py` 中):
```python
API_BASE_URL = "http://58.34.97.143:4000/v1/chat/completions"
API_KEY = "sk-9jWCuocCFjkCRWVvdtwG"
MODEL_NAME = "openai/gpt-oss-120b"
```

#### 更换为其他API

如需使用OpenAI官方API或其他兼容API:

1. 修改 `app.py` 第13-15行:
```python
API_BASE_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "your-api-key-here"
MODEL_NAME = "gpt-4" # 或 gpt-3.5-turbo
```

2. 或创建 `.env` 文件并修改代码读取方式:
```python
# 在 app.py 中修改为:
import os
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
```

### Streamlit 配置 (可选)

创建 `.streamlit/config.toml` 文件进行高级配置:

```toml
[server]
port = 8501
headless = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

## 验证安装

### 1. 检查 Python 和包

```bash
# 检查 Python 版本
python --version  # 或 python3 --version

# 检查已安装的包
pip list | grep streamlit
pip list | grep requests
```

### 2. 测试启动

```bash
streamlit run app.py
```

**预期输出**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 3. 验证功能

1. ✅ 视频是否正常加载和播放
2. ✅ 输入问题是否有响应
3. ✅ 推荐问题是否显示
4. ✅ 视频跳转是否正常
5. ✅ 专家解答是否可以获取

---

## 常见安装问题

### Q1: 提示 "streamlit command not found"

**原因**: Python包安装路径不在系统PATH中

**解决方法**:

**Windows**:
```bash
# 使用完整路径运行
python -m streamlit run app.py
```

**macOS/Linux**:
```bash
# 方法1: 使用完整路径
python3 -m streamlit run app.py

# 方法2: 添加到PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Q2: pip 安装失败

**解决方法**:

```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple streamlit requests python-dotenv

# 或升级 pip
python -m pip install --upgrade pip
```

### Q3: 端口 8501 被占用

**解决方法**:

```bash
# 指定其他端口
streamlit run app.py --server.port 8502
```

### Q4: 视频无法播放

**可能原因**:
1. 视频格式不支持
2. 视频文件路径错误
3. 浏览器不支持

**解决方法**:
1. 确保视频格式为 mp4/avi/mov
2. 检查 `video` 文件夹位置
3. 使用 Chrome 浏览器
4. 转换视频格式:
```bash
# 使用 ffmpeg 转换
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4
```

### Q5: API 调用失败

**检查步骤**:
1. 确认网络连接
2. 检查 API_KEY 是否正确
3. 检查 API_BASE_URL 是否可访问
4. 查看错误提示信息

**测试 API 连接**:
```bash
curl -X POST "http://58.34.97.143:4000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-9jWCuocCFjkCRWVvdtwG" \
  -d '{"model":"openai/gpt-oss-120b","messages":[{"role":"user","content":"测试"}]}'
```

### Q6: 字幕文件无法识别

**检查清单**:
1. ✅ 文件名是否与视频一致(仅扩展名不同)
2. ✅ 文件编码是否为 UTF-8
3. ✅ 时间戳格式是否正确
4. ✅ 是否在 `video` 文件夹中

**验证字幕格式**:
```python
# 测试脚本
import re
line = "[00:00:00.620 - 00:00:12.300] 测试文本"
match = re.match(r'\[([\d:\.]+)\s*-\s*([\d:\.]+)\]\s*(.+)', line)
if match:
    print("格式正确")
    print(f"开始: {match.group(1)}, 结束: {match.group(2)}, 文本: {match.group(3)}")
else:
    print("格式错误")
```

---

## 升级和更新

### 升级依赖包

```bash
pip install --upgrade streamlit requests python-dotenv
```

### 更新项目代码

如果使用 Git:
```bash
git pull origin main
```

如果是手动下载:
- 备份现有 `video` 文件夹
- 下载新版本代码
- 恢复 `video` 文件夹

---

## 卸载

### 删除虚拟环境

```bash
# Windows
rmdir /s venv

# macOS/Linux
rm -rf venv
```

### 卸载全局安装的包

```bash
pip uninstall streamlit requests python-dotenv
```

### 删除项目

直接删除项目文件夹即可。

---

## 生产环境部署 (高级)

### 使用 Docker 部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

构建和运行:
```bash
docker build -t video-qa-assistant .
docker run -p 8501:8501 -v $(pwd)/video:/app/video video-qa-assistant
```

### 使用 Systemd 服务 (Linux)

创建 `/etc/systemd/system/video-qa.service`:
```ini
[Unit]
Description=Video QA Assistant
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/video_qa_assistant
ExecStart=/usr/bin/python3 -m streamlit run app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl enable video-qa
sudo systemctl start video-qa
```

### 使用 Nginx 反向代理

Nginx 配置:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 性能优化建议

### 1. 视频文件优化
- 使用 H.264 编码的 MP4 格式
- 分辨率: 720p 或 1080p
- 比特率: 1-3 Mbps
- 时长: 建议不超过 30 分钟

### 2. 字幕文件优化
- 使用 UTF-8 编码
- 避免过长的单条字幕
- 合理控制字幕密度

### 3. API 调用优化
- 使用缓存机制(需要修改代码)
- 调整 timeout 参数
- 实现重试机制

---

## 技术支持

如遇到安装或部署问题:

1. 查看 [README.md](README.md) 了解项目详情
2. 查看 [USER_GUIDE.md](USER_GUIDE.md) 了解使用方法
3. 检查 Python 和依赖包版本
4. 查看控制台错误信息

---

**安装完成后,即可开始使用!** 🎉

参考 [USER_GUIDE.md](USER_GUIDE.md) 了解详细使用方法。
