"""配置文件"""

# 支持的链配置
CHAINS = {
    'bsc': {
        'name': 'BSC (Binance Smart Chain)',
        'chain_id': 56,
        'rpc_url': 'https://bsc-dataseed1.binance.org/',
        'explorer': 'https://bscscan.com',
        'native_token': 'BNB',
        'gas_price_gwei': {
            'slow': 3,
            'standard': 5,
            'fast': 10,
            'instant': 20
        }
    },
    'bsc_testnet': {
        'name': 'BSC Testnet',
        'chain_id': 97,
        'rpc_url': 'https://data-seed-prebsc-1-s1.binance.org:8545/',
        'explorer': 'https://testnet.bscscan.com',
        'native_token': 'tBNB',
        'gas_price_gwei': {
            'slow': 10,
            'standard': 10,
            'fast': 10,
            'instant': 10
        }
    }
}

# 转账限制
MIN_ADDRESSES = 10
MAX_ADDRESSES = 10000

# Gas 限制
GAS_LIMIT = 21000
