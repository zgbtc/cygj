# 高级混币器 - 使用指南

## 🎯 功能特性

### 三种混币模式

#### 1. ⚡ 快速模式 (Fast Mode)
- **隐私等级**: ⭐⭐⭐
- **延迟**: 1-3 秒
- **完成时间**: 约 30 分钟
- **特点**: 
  - 多路径混币
  - 随机金额分配
  - 适合测试和小额资金
- **适用场景**: 快速测试、小额混币

#### 2. 🔒 隐私模式 (Privacy Mode)
- **隐私等级**: ⭐⭐⭐⭐⭐
- **延迟**: 5-30 分钟
- **完成时间**: 1-2 天
- **特点**:
  - 多路径混币
  - 随机金额分配（30% 圆整金额）
  - **Tor 代理支持**
  - 长时间延迟
- **适用场景**: 中等金额、需要高隐私保护

#### 3. 🛡️ 极致隐私模式 (Ultimate Mode)
- **隐私等级**: ⭐⭐⭐⭐⭐⭐⭐
- **延迟**: 30-120 分钟
- **完成时间**: 3-7 天
- **特点**:
  - **跨链混币** (BSC → Polygon → Arbitrum → BSC)
  - 多路径混币
  - 随机金额分配（30% 圆整金额）
  - **Tor 代理支持**
  - 超长时间延迟
- **适用场景**: 大额资金、需要极致隐私保护

---

## 🔐 隐私保护技术

### 1. 多路径混币
```
传统线性路径: A → B → C → D → Target (容易追踪)

多路径混币:
  A → B1 ↘
  A → B2 → C1 → Target
  A → B3 ↗
```

### 2. 金额随机化
- 完全随机分配金额（不是均分）
- 30% 使用圆整金额（0.01, 0.05, 0.1, 0.5, 1.0 BNB）
- 避免精确小数，模拟人类行为

### 3. 时间去关联
- 快速模式: 1-3 秒延迟
- 隐私模式: 5-30 分钟延迟
- 极致模式: 30-120 分钟延迟
- 打破时间关联性

### 4. Tor 网络支持
- 隐藏真实 IP 地址
- 通过 Tor 代理发送交易
- RPC 节点无法追踪到真实用户

### 5. 跨链混币（极致模式）
```
BSC (源地址)
  ↓ 混币
  ↓ 桥接到 Polygon
Polygon
  ↓ 混币
  ↓ 桥接到 Arbitrum
Arbitrum
  ↓ 混币
  ↓ 桥回 BSC
BSC (目标地址)
```

---

## 📦 安装和配置

### 1. 安装依赖

```bash
cd api
pip install -r requirements.txt
```

### 2. 配置 Tor（隐私模式和极致模式需要）

#### Windows:
1. 下载 Tor Expert Bundle: https://www.torproject.org/download/tor/
2. 解压并运行 `tor.exe`
3. 默认 SOCKS5 代理: `127.0.0.1:9050`

#### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt-get install tor
sudo service tor start

# Mac
brew install tor
brew services start tor
```

### 3. 验证 Tor 连接

```bash
# 测试 Tor 是否运行
curl --socks5 127.0.0.1:9050 https://check.torproject.org
```

---

## 🚀 使用方法

### 前端使用

1. 访问 https://cygj-crypto-tools.vercel.app
2. 选择混币模式（快速/隐私/极致）
3. 填写参数：
   - 网络: BSC Testnet / BSC Mainnet
   - 源地址私钥
   - 目标地址
   - 转账金额
   - 跳数（10-100000）
4. 点击"执行混币"

### API 调用

```python
import requests

# 快速模式
response = requests.post('https://cygj-crypto-tools.vercel.app/api/mixer', json={
    'chain': 'bsc_testnet',
    'mode': 'fast',
    'from_private_key': 'YOUR_PRIVATE_KEY',
    'to_address': '0x...',
    'total_amount': 0.1,
    'num_hops': 100
})

# 隐私模式（需要 Tor）
response = requests.post('https://cygj-crypto-tools.vercel.app/api/mixer', json={
    'chain': 'bsc',
    'mode': 'privacy',
    'from_private_key': 'YOUR_PRIVATE_KEY',
    'to_address': '0x...',
    'total_amount': 1.0,
    'num_hops': 500
})

# 极致隐私模式（需要 Tor + 跨链）
response = requests.post('https://cygj-crypto-tools.vercel.app/api/mixer', json={
    'chain': 'bsc',
    'mode': 'ultimate',
    'from_private_key': 'YOUR_PRIVATE_KEY',
    'to_address': '0x...',
    'total_amount': 10.0,
    'num_hops': 1000
})

result = response.json()
print(result)
```

---

## 💰 费用说明

### 服务费（固定）
- 10 跳: 0.003 BNB
- 50 跳: 0.015 BNB
- 100 跳: 0.03 BNB
- 500 跳: 0.15 BNB
- 1000 跳: 0.30 BNB

### Gas 费用（估算）
- 每次转账: ~0.00021 BNB
- 100 跳: ~0.021 BNB
- 1000 跳: ~0.21 BNB

### 跨链费用（极致模式）
- 每次跨链: ~0.002 BNB
- 3 次跨链: ~0.006 BNB

### 总费用示例
```
100 跳快速模式:
  服务费: 0.03 BNB
  Gas 费: 0.021 BNB
  总计: 0.051 BNB

1000 跳极致模式:
  服务费: 0.30 BNB
  Gas 费: 0.21 BNB
  跨链费: 0.006 BNB
  总计: 0.516 BNB
```

---

## ⚠️ 安全建议

### 1. 测试网测试
- 先在 BSC Testnet 测试
- 确认流程正常后再用主网

### 2. 私钥安全
- 不要在公共网络输入私钥
- 使用硬件钱包更安全
- 建议使用临时地址

### 3. 金额建议
- 快速模式: 0.01-1 BNB
- 隐私模式: 0.1-10 BNB
- 极致模式: 1-100 BNB

### 4. Tor 使用
- 确保 Tor 正常运行
- 不要同时使用 VPN 和 Tor
- 定期更新 Tor

### 5. 时间规划
- 隐私模式需要 1-2 天
- 极致模式需要 3-7 天
- 不要中断执行过程

---

## 🔍 技术原理

### 为什么跨链混币最安全？

1. **打破链上追踪**
   - BSC 上的交易无法追踪到 Polygon
   - 桥接合约是资金池，无法关联

2. **多个断点**
   - 每次跨链都是一个"断点"
   - 不同链的区块浏览器无法互查

3. **增加追踪成本**
   - 需要监控多条链
   - 需要分析跨链桥接数据
   - 成本指数级增加

### 为什么需要 Tor？

即使链上无法追踪，RPC 节点可能记录：
```
你的 IP → RPC 节点 → 记录:
  - IP: 123.45.67.89
  - 交易: 0xABC... → 0xDEF...
  - 时间: 2026-05-08 15:30
```

使用 Tor 后：
```
你的电脑 → Tor 网络 → RPC 节点
RPC 只能看到 Tor 出口节点 IP
无法追踪到真实用户
```

---

## 📊 性能对比

| 方案 | 隐私性 | 成本 | 时间 | 技术难度 |
|------|--------|------|------|----------|
| 快速模式 | ⭐⭐⭐ | 低 | 30分钟 | 简单 |
| 隐私模式 | ⭐⭐⭐⭐⭐ | 低 | 1-2天 | 中等 |
| 极致模式 | ⭐⭐⭐⭐⭐⭐⭐ | 中 | 3-7天 | 高 |

---

## 🐛 故障排除

### 1. Tor 连接失败
```bash
# 检查 Tor 是否运行
netstat -an | grep 9050

# 重启 Tor
sudo service tor restart  # Linux
brew services restart tor  # Mac
```

### 2. 跨链失败
- 检查源链余额是否足够
- 检查桥接费用是否足够
- 等待桥接确认（5-30分钟）

### 3. 交易失败
- 检查 Gas 价格是否过低
- 检查网络是否拥堵
- 增加 Gas Limit

---

## 📚 参考资料

- [Tornado Cash 白皮书](https://tornado.cash/Tornado.cash_whitepaper_v1.4.pdf)
- [JoinMarket 文档](https://github.com/JoinMarket-Org/joinmarket-clientserver)
- [LayerZero 文档](https://layerzero.network/developers)
- [Tor 项目](https://www.torproject.org/)

---

## 📞 支持

如有问题，请联系：
- GitHub: https://github.com/zgbtc/cygj
- Email: support@example.com

---

## ⚖️ 免责声明

本工具仅供学习和研究使用。用户需自行承担使用风险，遵守当地法律法规。开发者不对任何损失负责。
