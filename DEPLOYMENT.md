# 部署指南

这是一个前后端分离的项目，需要分别部署前端和后端。

## 前端部署（Next.js）

前端已部署到 Netlify：https://cygj-crypto-tools.netlify.app

### 环境变量配置

在 Netlify 中设置环境变量：
- `NEXT_PUBLIC_API_URL`: 后端 API 地址

## 后端部署（Python Flask）

后端代码在 `stealth_transfer/` 目录，需要单独部署。

### 推荐部署方案

#### 1. Railway / Render（推荐）
- 支持 Python
- 自动部署
- 免费套餐可用

#### 2. Heroku
- 需要 `Procfile`
- 支持 Python

#### 3. AWS Lambda / Google Cloud Functions
- Serverless 方案
- 按需付费

### 部署步骤（以 Render 为例）

1. 在 Render 创建新的 Web Service
2. 连接 GitHub 仓库
3. 设置：
   - Root Directory: `stealth_transfer`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
4. 添加环境变量（从 `.env.example` 复制）
5. 部署完成后，获取 API URL
6. 在 Netlify 中设置 `NEXT_PUBLIC_API_URL` 为该 URL
7. 重新部署前端

## 当前状态

- ✅ 前端已部署到 Netlify
- ❌ 后端未部署（需要单独部署）
- ⚠️ 前端目前无法调用 API（因为后端未部署）

## 快速修复

如果只想展示前端界面（不需要实际功能），可以：
1. 移除 API 调用
2. 添加模拟数据
3. 显示"演示模式"提示
