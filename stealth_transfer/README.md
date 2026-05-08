# 隐私批量转账工具 - Stealth Transfer

基于 Web3 的批量转账工具，支持一次性向 10-10000 个地址发送代币。

## 🎭 核心功能：隐私转账

**从一个助记词生成多个地址，将资金分散到这些地址中，保护隐私！**

- 自动从助记词生成 10-10000 个地址
- 支持随机分配或平均分配金额
- 所有地址可用助记词恢复
- 隐藏资金来源，保护隐私

## 功能特性

- ✅ **隐私转账**：从助记词生成多个地址，分散资金
- ✅ 支持 BSC (Binance Smart Chain) 主网和测试网
- ✅ 批量转账：10-10000 个地址
- ✅ 多种 Gas 价格等级：慢速、标准、快速、即时
- ✅ 实时余额查询
- ✅ Gas 费用估算
- ✅ 地址验证
- ✅ 交易状态追踪
- 🔜 未来支持：Solana、Ethereum、Polygon 等多链

## 安装

```bash
cd stealth_transfer
pip install -r requirements.txt
```

## 使用方式

### 1. Web 界面（推荐）

启动服务后访问：
- **隐私转账**: http://localhost:5000/stealth.html
- **普通转账**: http://localhost:5000/

#### 隐私转账步骤：
1. 选择网络（BSC 主网/测试网）
2. 输入源地址私钥
3. 设置总金额和目标地址数量（10-10000）
4. 选择分配方式（随机/平均）
5. 可选：输入已有助记词，或留空自动生成
6. 选择 Gas 等级
7. 预览计划
8. 执行转账
9. **保存助记词！**所有地址都可以用这个助记词恢复

### 2. 命令行工具

#### 隐私转账 CLI
```bash
python stealth_cli.py
```

交互式界面，支持：
- 生成地址模式（仅查看，不转账）
- 执行转账模式（完整流程）

#### 普通批量转账 CLI
```bash
python cli.py
```

#### API 端点

**隐私转账相关**

**生成隐私地址**
```http
POST /api/stealth/generate
Content-Type: application/json

{
  "count": 100,
  "mnemonic": "可选，留空自动生成"
}
```

**创建隐私转账计划**
```http
POST /api/stealth/plan
Content-Type: application/json

{
  "chain": "bsc",
  "total_amount": 1.0,
  "num_addresses": 100,
  "distribution": "random",
  "mnemonic": "可选"
}
```

**执行隐私转账**
```http
POST /api/stealth/execute
Content-Type: application/json

{
  "chain": "bsc",
  "from_private_key": "0x...",
  "total_amount": 1.0,
  "num_addresses": 100,
  "distribution": "random",
  "gas_level": "standard"
}
```

**估算隐私转账费用**
```http
POST /api/stealth/estimate
Content-Type: application/json

{
  "chain": "bsc",
  "num_addresses": 100,
  "gas_level": "standard"
}
```

**普通转账相关**

**获取支持的链**
```http
GET /api/chains
```

**估算费用**
```http
POST /api/estimate
Content-Type: application/json

{
  "chain": "bsc",
  "num_addresses": 100,
  "gas_level": "standard"
}
```

**查询余额**
```http
POST /api/balance
Content-Type: application/json

{
  "chain": "bsc",
  "address": "0x..."
}
```

**批量转账**
```http
POST /api/transfer
Content-Type: application/json

{
  "chain": "bsc",
  "private_key": "0x...",
  "recipients": [
    {"address": "0x...", "amount": 0.01},
    {"address": "0x...", "amount": 0.02}
  ],
  "gas_level": "standard"
}
```

**验证地址**
```http
POST /api/validate
Content-Type: application/json

{
  "chain": "bsc",
  "addresses": ["0x...", "0x..."]
}
```

### 3. Python 脚本

#### 隐私转账示例
```python
from stealth_engine import StealthTransferEngine

# 初始化引擎
engine = StealthTransferEngine('bsc_testnet')

# 创建隐私转账计划
plan = engine.create_stealth_transfer_plan(
    total_amount=1.0,           # 总金额
    num_addresses=100,          # 生成 100 个地址
    distribution='random'       # 随机分配（更隐私）
)

print(f"助记词: {plan['mnemonic']}")
print(f"生成了 {len(plan['recipients'])} 个地址")

# 执行转账
result = engine.execute_stealth_transfer(
    from_private_key='0x你的私钥',
    plan=plan,
    gas_level='standard'
)

print(f"成功: {result['success_count']}, 失败: {result['failed_count']}")
print(f"助记词: {result['mnemonic']}")  # 保存这个！
```

#### 仅生成地址（不转账）
```python
from hd_wallet import HDWallet

# 生成新钱包
wallet = HDWallet()
print(f"助记词: {wallet.mnemonic}")

# 生成 100 个地址
addresses = wallet.generate_addresses(100)
for addr in addresses[:10]:
    print(f"[{addr['index']}] {addr['address']}")
```

#### 从助记词恢复地址
```python
from hd_wallet import HDWallet

# 从已有助记词恢复
mnemonic = "your twelve word mnemonic phrase here ..."
wallet = HDWallet(mnemonic)

# 获取特定索引的地址
account = wallet.get_account(0)  # 第一个地址
print(f"地址: {account['address']}")
print(f"私钥: {account['private_key']}")
```

#### 普通批量转账
```python
from transfer_engine import TransferEngine

# 初始化引擎
engine = TransferEngine('bsc')

# 准备接收地址列表
recipients = [
    {'address': '0x1234...', 'amount': 0.01},
    {'address': '0x5678...', 'amount': 0.02},
    # ... 更多地址
]

# 执行批量转账
private_key = '0x...'
results = engine.send_batch_transfers(
    private_key=private_key,
    recipients=recipients,
    gas_price_level='standard'
)

# 查看结果
for result in results:
    print(f"{result['to']}: {result['status']}")
    if result['status'] == 'pending':
        print(f"交易哈希: {result['tx_hash']}")
```

## Gas 价格等级

| 等级 | BSC 主网 | 说明 |
|------|----------|------|
| slow | 3 Gwei | 慢速，费用最低 |
| standard | 5 Gwei | 标准，推荐使用 |
| fast | 10 Gwei | 快速 |
| instant | 20 Gwei | 即时，费用最高 |

## 配置说明

编辑 `config.py` 可以：
- 添加新的链支持
- 调整 Gas 价格
- 修改转账数量限制
- 更改 RPC 节点

## 安全提示

⚠️ **重要安全建议**：

1. **私钥安全**：永远不要在代码中硬编码私钥
2. **测试先行**：先在测试网测试，确认无误后再使用主网
3. **小额测试**：首次使用建议先小额测试
4. **备份数据**：保存好交易记录和私钥备份
5. **网络安全**：使用 HTTPS 和安全的 RPC 节点

## 扩展开发

### 添加新链支持

在 `config.py` 中添加新链配置：

```python
CHAINS = {
    'solana': {
        'name': 'Solana',
        'chain_id': 101,
        'rpc_url': 'https://api.mainnet-beta.solana.com',
        'explorer': 'https://solscan.io',
        'native_token': 'SOL',
        'gas_price_gwei': {
            'slow': 1,
            'standard': 2,
            'fast': 5,
            'instant': 10
        }
    }
}
```

然后在 `transfer_engine.py` 中实现对应的转账逻辑。

## 许可证

MIT License

## 免责声明

本工具仅供学习和研究使用。使用本工具进行任何转账操作，风险自负。开发者不对任何资金损失负责。
