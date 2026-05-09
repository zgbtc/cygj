<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

---

# CYGJ Crypto Tools 项目文档

## 📋 项目概述

**项目名称：** CYGJ Crypto Tools  
**项目定位：** 专业的 Web3 加密货币工具箱平台  
**域名：** https://tool.cygj.us  
**部署平台：** Vercel  
**技术栈：** Next.js + TypeScript + Tailwind CSS  
**后端 API：** Python (FastAPI)

---

## 🎯 核心功能

### 1. Stealth Transfer Router（隐私转账路由器）
- **状态：** ✅ 已上线
- **功能：** 多跳跨链混币服务，支持 68+ 条区块链
- **模式：**
  - **快速模式：** 单链混币，3-5 分钟到账
  - **极致隐私模式：** 多链跨链混币，8-50 小时到账
- **路由：** `/stealth-transfer`
- **文件：** `app/stealth-transfer/page.tsx`

### 2. HD Wallet Generator（HD 钱包生成器）
- **状态：** 🚧 即将上线
- **功能：** BIP44 标准 HD 钱包生成，支持批量生成

### 3. Batch Transfer（批量转账）
- **状态：** 🚧 即将上线
- **功能：** 批量发送 Token 到多个地址，支持 CSV 导入

### 4. Token Analyzer（代币分析器）
- **状态：** 🚧 即将上线
- **功能：** 代币持仓分析、交易历史查询

### 5. Gas Tracker（Gas 追踪器）
- **状态：** 🚧 即将上线
- **功能：** 实时 Gas 价格监控

### 6. NFT Batch Mint（NFT 批量铸造）
- **状态：** 🚧 即将上线
- **功能：** 批量铸造 NFT，支持 ERC-721/1155

---

## 🌐 多语言支持

### 实现方式
- **默认语言：** 英文 (EN)
- **支持语言：** 英文 (EN) / 中文 (ZH)
- **切换方式：** 右上角 Globe 图标按钮

### 已支持多语言的页面
- ✅ 首页 (`app/page.tsx`)
- ✅ 隐私转账页面 (`app/stealth-transfer/page.tsx`)
- ✅ Disclaimer 页面 (`app/disclaimer/page.tsx`)
- ✅ Terms 页面 (`app/terms/page.tsx`)
- ✅ Privacy 页面 (`app/privacy/page.tsx`)
- ✅ SEO 关键词页面 (`app/keywords/page.tsx`)

### 翻译对象结构
```typescript
const t = {
  en: {
    key: "English text"
  },
  zh: {
    key: "中文文本"
  }
};
```

---

## 🔍 SEO 优化策略

### 1. Metadata 优化
**文件：** `app/layout.tsx`

**优化内容：**
- ✅ Title：包含核心关键词（Stealth Transfer, HD Wallet, Batch Tools）
- ✅ Description：突出 Web3 工具箱定位
- ✅ Keywords：高流量关键词（batch wallet generator, batch check balance 等）
- ✅ OpenGraph：社交媒体分享优化
- ✅ Twitter Card：Twitter 分享优化
- ✅ Canonical URL：规范化 URL
- ✅ Robots：允许搜索引擎索引

**敏感词处理：**
- ❌ 避免使用：crypto mixer, 混币器
- ✅ 替换为：stealth transfer, privacy transfer, 隐匿转账

### 2. SEO 关键词页面
**路由：** `/keywords`  
**文件：** `app/keywords/page.tsx`  
**配置文件：** `lib/seo-keywords.ts`

**目的：** 提升关键词密度，专门给搜索引擎爬虫抓取

**关键词密度目标：**
- **高密度关键词（3%+）：**
  - 币工具 (cointool)
  - Web3工具箱 (web3 toolbox)
  - 加密工具箱 (crypto toolbox)
  - 加密货币工具 (crypto tools)

- **中等密度关键词（2-3%）：**
  - 批量钱包生成 (batch wallet generator)
  - 隐私转账 (stealth transfer)
  - 批量转账 (batch transfer)
  - HD钱包生成器 (HD wallet generator)

- **低密度关键词（1-2%）：**
  - 批量地址查询 (batch address check)
  - 批量发送Token (token multisender)
  - 跨链转账 (cross-chain transfer)
  - DeFi工具 (DeFi tools)
  - BSC工具 (BSC tools)
  - ETH工具 (ETH tools)

**入口：** 点击页面底部的 "© 2024 CYGJ Tools" 跳转

**添加新关键词的方法：**
1. 在 `lib/seo-keywords.ts` 中添加关键词配置
2. 在 `app/keywords/page.tsx` 中添加包含该关键词的句子
3. 使用 `<strong className="text-[#d4af37]">关键词</strong>` 高亮显示
4. 根据目标密度重复关键词 5-20 次

---

## 📊 数据分析

### Cloudflare Web Analytics
**集成方式：** 自动模式（Automatic）  
**Account ID：** `3da8bcb1202ea30dd8644f3a0095fdce`  
**Zone ID：** `efffb11a15b9b424ecf4a5f955a86007`  
**优势：** 完全匿名，不追踪用户个人信息

---

## 🎨 设计规范

### 配色方案
- **主色：** 金色 `#d4af37`
- **辅助色：** 浅金色 `#ffd700`
- **背景色：** 深灰 `#1a1a1a`, 黑色 `#0a0a0a`
- **文字色：** 白色 `#ffffff`, 灰色 `#gray-400`
- **成功色：** 绿色 `#10b981`

### 组件样式
- **按钮：** 圆角 `rounded-lg`, 悬停效果 `hover:bg-[#d4af37]`
- **卡片：** 边框 `border-[#d4af37]/20`, 阴影 `shadow-2xl`
- **输入框：** 底部边框 `border-b-2 border-[#d4af37]/50`

---

## 📁 项目结构

```
crypto-tools-hub/
├── app/                          # Next.js App Router
│   ├── page.tsx                  # 首页
│   ├── layout.tsx                # 全局布局（Metadata）
│   ├── stealth-transfer/         # 隐私转账页面
│   │   └── page.tsx
│   ├── keywords/                 # SEO 关键词页面
│   │   └── page.tsx
│   ├── disclaimer/               # 免责声明
│   ├── terms/                    # 服务条款
│   ├── privacy/                  # 隐私政策
│   └── components/               # 组件
│       ├── Footer.tsx            # 页脚组件
│       └── AgreementModal.tsx    # 协议弹窗
├── lib/                          # 工具库
│   ├── config.ts                 # 配置文件
│   └── seo-keywords.ts           # SEO 关键词配置
├── api/                          # Python 后端 API
│   ├── mixer.py                  # 混币引擎
│   ├── advanced_mixer_engine.py  # 高级混币引擎
│   ├── crosschain_bridge.py      # 跨链桥接
│   └── proxy_pool.py             # 代理池
└── public/                       # 静态资源
```

---

## 🚀 部署流程

### Git 提交规范
```bash
# 添加文件
git add <files>

# 提交（使用规范的 commit message）
git commit -m "feat: 功能描述"
git commit -m "fix: 修复描述"
git commit -m "docs: 文档更新"
git commit -m "style: 样式调整"

# 推送到远程
git push origin main
```

### Vercel 自动部署
- 推送到 GitHub 后，Vercel 自动触发部署
- 构建时间：1-3 分钟
- 部署完成后自动更新 https://tool.cygj.us

---

## ⚠️ 重要注意事项

### 1. 敏感词处理
- **禁止使用：** crypto mixer, 混币器, mixing, tumbler
- **替换为：** stealth transfer, privacy transfer, 隐私转账, 隐匿转账

### 2. 安全与隐私
- 用户私钥/助记词仅在浏览器本地使用，不上传服务器
- 使用 Cloudflare Analytics（匿名），不使用 Google Analytics
- 所有中间地址通过 BIP44 派生，用户完全控制

### 3. 多语言开发
- 所有可见 UI 文本必须支持中英文切换
- Markdown 文档（如 FAQ）不需要翻译
- 默认语言为英文

### 4. SEO 优化
- 新增工具时，必须在 `/keywords` 页面添加对应关键词
- 关键词密度目标：核心词 3%+，次要词 2-3%，长尾词 1-2%
- 避免关键词堆砌，自然融入句子中

---

## 🔧 开发指南

### 添加新工具的步骤

1. **在首页添加工具卡片**（`app/page.tsx`）
   ```typescript
   {
     id: 7,
     name: "New Tool Name",
     category: "category",
     description: "Tool description",
     icon: "🎯",
     status: "coming-soon"
   }
   ```

2. **创建工具页面**（`app/new-tool/page.tsx`）
   - 复制现有页面作为模板
   - 添加多语言支持
   - 实现核心功能

3. **添加 SEO 关键词**
   - 在 `lib/seo-keywords.ts` 中添加关键词配置
   - 在 `app/keywords/page.tsx` 中添加关键词内容

4. **更新 Metadata**（`app/layout.tsx`）
   - 在 keywords 数组中添加新工具的关键词

5. **测试与部署**
   - 本地测试功能
   - 提交到 Git
   - Vercel 自动部署

---

## 📞 联系方式

**域名：** https://tool.cygj.us  
**GitHub：** https://github.com/zgbtc/cygj  
**Vercel：** https://vercel.com/zigong/cygj

---

## 📝 更新日志

### 2024-01-XX
- ✅ 添加 SEO 关键词页面 (`/keywords`)
- ✅ 创建关键词配置文件 (`lib/seo-keywords.ts`)
- ✅ 优化 Footer 组件，版权信息改为超链接
- ✅ 集成 Cloudflare Web Analytics（自动模式）
- ✅ 完善多语言支持（EN/ZH）
- ✅ 优化 Metadata（Title, Description, Keywords, OG Tags）

---

## 🤖 AI Agent 使用说明

**执行原则：** 请分步执行，每完成一个步骤就告诉我结果，不要一次性执行所有操作，避免长时间挂起

**常用命令：**
```bash
# 查看 Git 状态
git status

# 添加文件
git add <files>

# 提交
git commit -m "message"

# 推送
git push origin main
```

**文件路径规范：**
- 使用绝对路径：`d:\aiwork\crypto\crypto-tools-hub\...`
- Windows 系统，使用反斜杠 `\`