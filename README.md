# Crypto Tools Hub - 加密工具聚合平台

一个精选的加密货币工具聚合平台，帮助用户发现和使用优质的 Web3 工具。

## 🎯 特性

- ✅ 精选优质工具
- ✅ 分类浏览
- ✅ 搜索功能
- ✅ 响应式设计
- ✅ 无需后端
- ✅ 快速部署

## 🛠️ 技术栈

- HTML5
- Tailwind CSS (CDN)
- Vanilla JavaScript
- 无需构建工具

## 📦 项目结构

```
crypto-tools-hub/
├── index.html              # 主页
├── app.js                  # 主页逻辑
├── stealth-transfer/       # Stealth Transfer 工具页
│   └── index.html
└── README.md
```

## 🚀 快速开始

### 方式 1: 直接打开

直接用浏览器打开 `index.html` 文件即可。

### 方式 2: 本地服务器

```bash
# 使用 Python
python -m http.server 8000

# 使用 Node.js
npx serve

# 使用 PHP
php -S localhost:8000
```

然后访问 http://localhost:8000

## 📝 添加新工具

编辑 `app.js` 文件，在 `tools` 数组中添加新工具：

```javascript
{
    id: 7,
    name: "Your Tool Name",
    category: "privacy", // privacy, defi, analytics, wallet
    description: "工具描述",
    icon: "🔧",
    features: [
        "特性 1",
        "特性 2",
        "特性 3"
    ],
    chains: ["BSC", "ETH"],
    url: "/your-tool",
    status: "active", // active 或 coming-soon
    rating: 4.5,
    users: "1K+"
}
```

## 🎨 自定义

### 修改颜色主题

在 `index.html` 的 `<style>` 标签中修改：

```css
.gradient-bg {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}
```

### 修改分类

在 `index.html` 的分类部分添加或修改分类卡片。

## 📱 已集成工具

### 1. Stealth Transfer 🎭
- **类型**: 隐私工具
- **功能**: 多跳混币器
- **链**: BSC, ETH
- **状态**: ✅ 可用

### 2. HD Wallet Generator 🔐
- **类型**: 钱包工具
- **功能**: BIP44 HD 钱包生成
- **链**: BSC, ETH, Polygon
- **状态**: ✅ 可用

### 3. Batch Transfer 💸
- **类型**: DeFi 工具
- **功能**: 批量转账
- **链**: BSC, ETH, Polygon
- **状态**: ✅ 可用

### 4-6. 即将推出
- Token Analyzer 📊
- Gas Tracker ⛽
- NFT Batch Mint 🎨

## 🌐 部署

### Vercel

1. 安装 Vercel CLI:
```bash
npm i -g vercel
```

2. 部署:
```bash
vercel
```

### Netlify

1. 拖拽整个文件夹到 Netlify Drop
2. 或使用 Netlify CLI:
```bash
npm i -g netlify-cli
netlify deploy
```

### GitHub Pages

1. 推送到 GitHub 仓库
2. 在仓库设置中启用 GitHub Pages
3. 选择 main 分支

## 📊 工具分类

- 🎭 **隐私工具**: 混币器、隐私钱包
- 💰 **DeFi 工具**: 交易、流动性、批量操作
- 📊 **数据分析**: 链上数据、图表、追踪
- 🔐 **钱包工具**: HD 钱包、管理工具

## 🔗 相关链接

- Stealth Transfer 后端: `http://localhost:5000`
- 文档: 查看各工具页面
- GitHub: [Your Repo]

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 PR 添加新工具或改进现有功能！

## ⚠️ 免责声明

本平台仅提供工具聚合服务，不对工具的安全性和可靠性负责。使用前请自行评估风险。

## 📧 联系方式

- Twitter: [@your-twitter]
- Discord: [Your Discord]
- Email: your-email@example.com
