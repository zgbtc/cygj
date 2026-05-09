"""配置文件"""

# 支持的链配置
CHAINS = {
    'bsc': {
        'name': 'BSC (Binance Smart Chain)',
        'chain_id': 56,
        'rpc_url': 'https://bsc-dataseed.bnbchain.org/',
        # 多个备用 RPC（按优先级排序，前几个是对云环境友好的）
        'rpc_urls': [
            'https://bsc.publicnode.com',
            'https://bsc-rpc.publicnode.com',
            'https://binance.llamarpc.com',
            'https://bsc.drpc.org',
            'https://bsc.meowrpc.com',
            'https://1rpc.io/bnb',
            'https://bsc-dataseed.bnbchain.org/',
            'https://bsc-dataseed1.bnbchain.org/',
            'https://bsc-dataseed2.bnbchain.org/',
            'https://bsc-dataseed3.bnbchain.org/',
            'https://bsc-dataseed4.bnbchain.org/',
            'https://bsc-dataseed1.defibit.io/',
            'https://bsc-dataseed2.defibit.io/',
            'https://bsc-dataseed3.defibit.io/',
            'https://bsc-dataseed4.defibit.io/',
            'https://bsc-dataseed1.ninicoin.io/',
            'https://bsc-dataseed2.ninicoin.io/',
            'https://bsc-dataseed3.ninicoin.io/',
            'https://bsc-dataseed4.ninicoin.io/',
        ],
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
        'rpc_url': 'https://data-seed-prebsc-1-s1.bnbchain.org:8545/',
        'rpc_urls': [
            'https://bsc-testnet.publicnode.com',
            'https://bsc-testnet-rpc.publicnode.com',
            'https://bsc-testnet.drpc.org',
            'https://data-seed-prebsc-1-s1.bnbchain.org:8545/',
            'https://data-seed-prebsc-2-s1.bnbchain.org:8545/',
            'https://data-seed-prebsc-1-s2.bnbchain.org:8545/',
            'https://data-seed-prebsc-2-s2.bnbchain.org:8545/',
            'https://data-seed-prebsc-1-s3.bnbchain.org:8545/',
            'https://data-seed-prebsc-2-s3.bnbchain.org:8545/',
        ],
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
