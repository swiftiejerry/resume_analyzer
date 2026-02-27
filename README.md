<div align="center">

# 🚀 AI Resume Analyzer

**基于 FastAPI + TailwindCSS 的大模型驱动简历解析与岗位匹配专家系统**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Aliyun FC](https://img.shields.io/badge/Platform-Aliyun_FC3.0-FF6A00.svg?logo=alibabacloud)](https://fcnext.console.aliyun.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[特性](#-核心特性) •
[架构](#-系统架构) •
[快速开始](#-快速开始) •
[部署指南](#-线上部署) •
[API文档](#-api-接口清单) •
[目录结构](#-项目目录结构)

</div>

---

## ✨ 核心特性

- 📄 **双擎驱动 PDF 解析**：优先使用实体文本提取，无缝回退至 `qwen-vl-max` 多模态视觉大模型处理扫描版/纯图片简历。
- 🧠 **大模型信息抽取**：对接阿里云通义千问大模型，精准结构化提取姓名、电话、邮箱、教育背景、核心技能及工作经验。
- 🎯 **智能岗位匹配**：基于输入的 JD (Job Description)，AI 多维度打分（0-100分）并生成专业的人岗匹配分析短评。
- ⚡ **极致性能缓存**：引入 Redis 缓存层，对同一份简历和岗位的匹配结果实现毫秒级复用，极大节省大模型 Token 开销。
- ☁️ **云原生 Serverless**：前后端完全分离。前端托管于 GitHub Pages，后端一键部署至阿里云函数计算（Function Compute 3.0）。

## 🏗 系统架构

系统采用清晰的模块化设计，前后端通过 RESTful API 通信：

*   **前端展示**：纯 HTML/JS + TailwindCSS，无构建负担，支持拖拽交互与响应式动态结果展示。
*   **网关接入**：FastAPI 提供高性能异步接口，并配置全域跨域（CORS）支持分离部署。
*   **业务编排**：
    *   `PDFService`：负责 PDF 内容鉴定与跨格式内容提取。
    *   `AIService`：组装 Prompt，调度大模型（文本模型 `qwen-turbo` / 多模态模型 `qwen-vl-max`）。
    *   `RedisService`：处理高并发下的结果缓存与降级容灾。

## 🚀 快速开始

### 1. 环境准备

请确保本地已安装 Python 3.10+ 环境。

```bash
# 1. 创建并激活虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # Mac/Linux

# 2. 安装核心依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件，填入你的配置信息配置：

```env
# 大模型鉴权 (必填，前往阿里云百炼获取)
DASHSCOPE_API_KEY=your_dashscope_api_key

# 缓存配置 (可选，若不填则降级为内存字典缓存)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### 3. 本地启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
启动后：
- 访问页面：[http://localhost:8000/](http://localhost:8000/)
- 接口文档 (Swagger UI)：[http://localhost:8000/docs](http://localhost:8000/docs)

---

## ☁️ 线上部署

本项目专门为 Serverless 场景深度优化，支持**前端托管、后端无服务器计算**方案。我们提供了包含 GitHub / 阿里云一键部署脚本。

### 方式 A：一键部署脚本 (推荐)

项目内置了 `Deploy-GitHub.ps1` (Windows PowerShell) 脚本，支持双端闭环自动化：

1. 修改 `static/index.html` 第 176 行的 `API_BASE` 指向你的真实生产后端。
2. 运行脚本：
   ```powershell
   .\Deploy-GitHub.ps1
   ```
3. 根据提示输入 GitHub Username 和 Token，脚本将自动建库、推送代码、触发 GitHub Actions 发布 Frontend。

### 方式 B：手动发版至阿里云 FC 3.0

请确保已安装 Node.js 和 Serverless Devs CLI：

```bash
# 1. 安装工具并配置凭证
npm install -g @serverless-devs/s
s config add

# 2. 根据 s.yaml 一键部署后端
s deploy
```

发布后，控制台会打印你的专属 API 域名（形如 `https://***.cn-hangzhou.fcapp.run`）。

---

## 📡 API 接口清单

完整的 OpenAPI 文档在服务启动后可通过 `/docs` 路由查看。核心接口如下：

### 1. 抽取简历信息
- **POST** [`/api/resume/analyze`](#)
- **Content-Type**: `multipart/form-data`
- **参数**: `file` (PDF 格式的文件)
- **返回**: 结构化的姓名、电话、技能、经历等 JSON 数据以及简历特征 UUID。

### 2. 岗位智能匹配
- **POST** [`/api/resume/match`](#)
- **Content-Type**: `application/json`
- **Body**: 
  ```json
  {
    "resume_text": "...",
    "job_description": "后端开发工程师，熟练掌握 FastAPI..."
  }
  ```
- **返回**: 匹配总分（0-100）及详细的优劣势短评。

---

## 📂 项目目录结构

```text
resume_analyzer/
├── api/             # API 路由控制层 (Controllers)
├── core/            # 核心全局配置 (环境变量、日志格式)
├── models/          # Pydantic 进出参数据模型
├── services/        # 核心业务逻辑实现 (大模型、PDF、Redis)
├── static/          # 前端交互视图 (HTML/JS/CSS)
├── tests/           # Pytest 全量单元与集成自动化测试
├── main.py          # FastAPI application 入口点
├── s.yaml           # 阿里云 FC Deploy 声明式配置
└── requirements.txt # Python 依赖清单
```

<div align="center">
  <p><i>Made with ❤️ using FastAPI & DashScope</i></p>
</div>
