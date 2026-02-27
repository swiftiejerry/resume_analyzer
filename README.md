# AI 智能简历分析系统

这是一个基于 FastAPI + TailwindCSS 的 Serverless 架构 AI 简历分析工具。集成了阿里云通义千问大模型进行数据信息的提取和岗位匹配。

## 本地快速启动

1. **环境准备:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **环境变量配置:**
   在根目录下创建一个 `.env` 文件，输入以下内容（若无，系统会使用模拟数据）：
   ```env
   DASHSCOPE_API_KEY=your_aliyun_dashscope_api_key
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

3. **运行服务:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **访问界面:**
   打开浏览器访问: `http://localhost:8000/`

## 阿里云 Serverless (FC3.0) 部署指南

如果您已经安装了 Serverless Devs 工具 (`s` cli)：

1. 创建并配置阿里云凭证: `s config add`
2. 根目录下提供了一个 `s.yaml` 样例文件，运行如下命令一键部署：
   ```bash
   s deploy -y
   ```

## 目录结构
- `api/`: RESTful 路由定义
- `core/`: 核心配置
- `models/`: 数据模型类
- `services/`: AI、PDF 及 Redis 等核心业务逻辑
- `static/`: 前端页面静态资源
