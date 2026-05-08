# Crypto Tools Hub - 加密工具聚合平台

精选优质加密货币工具，助力您的 Web3 之旅

🌐 **在线演示**: [即将上线]

## 📸 项目截图

![首页](https://via.placeholder.com/800x400?text=Crypto+Tools+Hub)

## ✨ 功能特性

### 🎭 Stealth Transfer (已上线)
多跳混币器，通过交叉转账隐藏资金路径，保护隐私
- 10-1000 跳可选
- 自动路径生成
- 支持 BSC/ETH
- 服务费固定

### 即将推出
- 🔐 HD Wallet Generator - HD 钱包生成器
- 💸 Batch Transfer - 批量转账工具
- 📊 Token Analyzer - 代币分析工具
- ⛽ Gas Tracker - Gas 价格追踪
- 🎨 NFT Batch Mint - NFT 批量铸造

## 🚀 技术栈

### 前端
- **框架**: Next.js 16.2.6 (App Router + Turbopack)
- **UI**: React 19 + Tailwind CSS 4
- **语言**: TypeScript 5

### 后端
- **框架**: Flask
- **区块链**: Web3.py
- **钱包**: eth-account, mnemonic

## 📦 快速开始

### 前置要求
- Node.js 20+
- Python 3.10+
- npm 或 yarn

### 安装

```bash
# 克隆项目
git clone https://github.com/your-username/crypto-tools-hub.git
cd crypto-tools-hub

# 安装前端依赖
npm install

# 安装后端依赖
cd stealth_transfer
pip install -r requirements.txt
cd ..
```

### 开发

```bash
# 终端 1: 启动前端
npm run dev

# 终端 2: 启动后端
cd stealth_transfer
python app.py
```

访问 http://localhost:3000

## 📁 项目结构

```
crypto-tools-hub/
├── app/                      # Next.js App Router
│   ├── page.tsx             # 首页
│   ├── layout.tsx           # 布局
│   └── stealth-transfer/    # Stealth Transfer 页面
├── stealth_transfer/        # Flask 后端
│   ├── app.py              # API 服务
│   ├── mixer_engine.py     # 混币器引擎
│   ├── hd_wallet.py        # HD 钱包
│   └── static/             # 静态文件
├── public/                  # 静态资源
├── package.json            # 前端依赖
├── netlify.toml            # Netlify 配置
└── README.md               # 本文件
```

## 🎯 使用说明

### Stealth Transfer

1. 访问首页，默认显示 Stealth Transfer
2. 选择网络（BSC Testnet/Mainnet/Ethereum）
3. 输入源地址私钥
4. 输入目标地址
5. 输入转账金额
6. 选择跳数（推荐 100）
7. （可选）输入助记词
8. 查看费用估算
9. 点击"执行混币"

### 费用说明

| 跳数 | 服务费 | Gas 费用 (估算) | 推荐场景 |
|------|--------|----------------|---------|
| 10   | 0.003 BNB | 0.0021 BNB | 快速测试 |
| 100  | 0.03 BNB | 0.021 BNB | ⭐ 推荐使用 |
| 500  | 0.15 BNB | 0.105 BNB | 高隐私需求 |
| 1000 | 0.30 BNB | 0.21 BNB | 最高隐私 |

## 🔒 安全提示

- ⚠️ 请妥善保管私钥和助记词
- ⚠️ 不要泄露给任何人
- ⚠️ 建议先在测试网测试
- ⚠️ 建议从小额开始

## 🚀 部署

### Netlify 部署（前端）

1. 推送代码到 GitHub
2. 在 Netlify 导入项目
3. 自动部署

### 后端部署

参考 [部署指南.md](./部署指南.md)

## 📚 文档

- [使用说明.md](./使用说明.md) - 详细使用指南
- [快速启动.md](./快速启动.md) - 快速上手
- [部署指南.md](./部署指南.md) - 部署流程
- [测试报告.md](./测试报告.md) - 测试结果
- [项目总结.md](./项目总结.md) - 项目概览

## 🤝 贡献

欢迎提交 Pull Request 或 Issue！

## 📄 许可证

MIT License

## 📞 联系方式

- GitHub: [your-username](https://github.com/your-username)
- Twitter: [@your-twitter](https://twitter.com/your-username)
- Email: support@your-domain.com

---

© 2026 Crypto Tools Hub. All rights reserved.
