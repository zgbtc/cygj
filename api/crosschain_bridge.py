"""跨链桥接引擎 - 支持多链转账"""
import time
import random
import logging
from typing import Dict, Optional
from web3 import Web3
from eth_account import Account

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 多链配置
CHAIN_CONFIGS = {
    'bsc': {
        'name': 'BSC',
        'chain_id': 56,
        'rpc_url': 'https://bsc-dataseed.binance.org',
        'native_token': 'BNB',
        'explorer': 'https://bscscan.com',
        'stargate_router': '0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
        'layerzero_chain_id': 102
    },
    'bsc_testnet': {
        'name': 'BSC Testnet',
        'chain_id': 97,
        'rpc_url': 'https://data-seed-prebsc-1-s1.binance.org:8545',
        'native_token': 'BNB',
        'explorer': 'https://testnet.bscscan.com',
        'stargate_router': '0xbB0f1be1E9CE9cB27EA5b0c3a85B7cc3381d8176',
        'layerzero_chain_id': 10102
    },
    'polygon': {
        'name': 'Polygon',
        'chain_id': 137,
        'rpc_url': 'https://polygon-rpc.com',
        'native_token': 'MATIC',
        'explorer': 'https://polygonscan.com',
        'stargate_router': '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        'layerzero_chain_id': 109
    },
    'arbitrum': {
        'name': 'Arbitrum',
        'chain_id': 42161,
        'rpc_url': 'https://arb1.arbitrum.io/rpc',
        'native_token': 'ETH',
        'explorer': 'https://arbiscan.io',
        'stargate_router': '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614',
        'layerzero_chain_id': 110
    },
    'optimism': {
        'name': 'Optimism',
        'chain_id': 10,
        'rpc_url': 'https://mainnet.optimism.io',
        'native_token': 'ETH',
        'explorer': 'https://optimistic.etherscan.io',
        'stargate_router': '0xB0D502E938ed5f4df2E681fE6E419ff29631d62b',
        'layerzero_chain_id': 111
    },
    'avalanche': {
        'name': 'Avalanche',
        'chain_id': 43114,
        'rpc_url': 'https://api.avax.network/ext/bc/C/rpc',
        'native_token': 'AVAX',
        'explorer': 'https://snowtrace.io',
        'stargate_router': '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        'layerzero_chain_id': 106
    }
}

# Stargate Router ABI (简化版，只包含 swap 函数)
STARGATE_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint16", "name": "_dstChainId", "type": "uint16"},
            {"internalType": "uint256", "name": "_srcPoolId", "type": "uint256"},
            {"internalType": "uint256", "name": "_dstPoolId", "type": "uint256"},
            {"internalType": "address payable", "name": "_refundAddress", "type": "address"},
            {"internalType": "uint256", "name": "_amountLD", "type": "uint256"},
            {"internalType": "uint256", "name": "_minAmountLD", "type": "uint256"},
            {
                "components": [
                    {"internalType": "uint256", "name": "dstGasForCall", "type": "uint256"},
                    {"internalType": "uint256", "name": "dstNativeAmount", "type": "uint256"},
                    {"internalType": "bytes", "name": "dstNativeAddr", "type": "bytes"}
                ],
                "internalType": "struct IStargateRouter.lzTxObj",
                "name": "_lzTxParams",
                "type": "tuple"
            },
            {"internalType": "bytes", "name": "_to", "type": "bytes"},
            {"internalType": "bytes", "name": "_payload", "type": "bytes"}
        ],
        "name": "swap",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint16", "name": "_dstChainId", "type": "uint16"},
            {"internalType": "uint8", "name": "_functionType", "type": "uint8"},
            {"internalType": "bytes", "name": "_toAddress", "type": "bytes"},
            {"internalType": "bytes", "name": "_transferAndCallPayload", "type": "bytes"},
            {
                "components": [
                    {"internalType": "uint256", "name": "dstGasForCall", "type": "uint256"},
                    {"internalType": "uint256", "name": "dstNativeAmount", "type": "uint256"},
                    {"internalType": "bytes", "name": "dstNativeAddr", "type": "bytes"}
                ],
                "internalType": "struct IStargateRouter.lzTxObj",
                "name": "_lzTxParams",
                "type": "tuple"
            }
        ],
        "name": "quoteLayerZeroFee",
        "outputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


class CrossChainBridge:
    """跨链桥接引擎"""
    
    def __init__(self, use_tor: bool = False):
        """
        初始化跨链桥接引擎
        
        Args:
            use_tor: 是否使用 Tor 代理
        """
        self.use_tor = use_tor
        self.chains = {}
        
        # 初始化所有链的连接
        for chain_name, config in CHAIN_CONFIGS.items():
            try:
                if use_tor:
                    # 使用 Tor SOCKS5 代理
                    import requests
                    session = requests.Session()
                    session.proxies = {
                        'http': 'socks5h://127.0.0.1:9050',
                        'https': 'socks5h://127.0.0.1:9050'
                    }
                    w3 = Web3(Web3.HTTPProvider(config['rpc_url'], session=session))
                else:
                    w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
                
                if w3.is_connected():
                    self.chains[chain_name] = {
                        'w3': w3,
                        'config': config
                    }
                    logger.info(f"✅ 已连接到 {config['name']}")
                else:
                    logger.warning(f"⚠️ 无法连接到 {config['name']}")
            except Exception as e:
                logger.error(f"❌ 连接 {config['name']} 失败: {e}")
    
    def get_balance(self, chain: str, address: str) -> float:
        """获取指定链上的余额"""
        if chain not in self.chains:
            raise ValueError(f"不支持的链: {chain}")
        
        w3 = self.chains[chain]['w3']
        balance_wei = w3.eth.get_balance(address)
        return float(w3.from_wei(balance_wei, 'ether'))
    
    def estimate_bridge_fee(
        self,
        from_chain: str,
        to_chain: str,
        amount: float
    ) -> Dict:
        """
        估算跨链桥接费用
        
        Args:
            from_chain: 源链
            to_chain: 目标链
            amount: 金额
        
        Returns:
            费用详情
        """
        # 简化版：固定费用估算
        # 实际应该调用 Stargate 的 quoteLayerZeroFee
        
        base_fee = 0.001  # 基础费用
        gas_fee = 0.002   # Gas 费用
        
        total_fee = base_fee + gas_fee
        net_amount = amount - total_fee
        
        return {
            'from_chain': from_chain,
            'to_chain': to_chain,
            'amount': amount,
            'base_fee': base_fee,
            'gas_fee': gas_fee,
            'total_fee': total_fee,
            'net_amount': net_amount
        }
    
    def bridge_native_token(
        self,
        from_chain: str,
        to_chain: str,
        from_private_key: str,
        to_address: str,
        amount: float,
        slippage: float = 0.01
    ) -> Dict:
        """
        跨链桥接原生代币
        
        Args:
            from_chain: 源链
            to_chain: 目标链
            from_private_key: 源地址私钥
            to_address: 目标地址
            amount: 金额
            slippage: 滑点容忍度
        
        Returns:
            交易结果
        """
        if from_chain not in self.chains:
            raise ValueError(f"不支持的源链: {from_chain}")
        if to_chain not in self.chains:
            raise ValueError(f"不支持的目标链: {to_chain}")
        
        from_w3 = self.chains[from_chain]['w3']
        from_config = self.chains[from_chain]['config']
        to_config = self.chains[to_chain]['config']
        
        # 获取账户
        account = Account.from_key(from_private_key)
        from_address = account.address
        
        # 检查余额
        balance = self.get_balance(from_chain, from_address)
        if balance < amount:
            raise ValueError(f"余额不足: {balance} < {amount}")
        
        logger.info(f"\n🌉 跨链桥接:")
        logger.info(f"  从: {from_config['name']} ({from_address[:10]}...)")
        logger.info(f"  到: {to_config['name']} ({to_address[:10]}...)")
        logger.info(f"  金额: {amount} {from_config['native_token']}")
        
        try:
            # 注意：这是简化版实现
            # 实际应该调用 Stargate Router 合约
            # 这里我们使用直接转账模拟跨链（仅用于演示）
            
            amount_wei = from_w3.to_wei(amount, 'ether')
            
            # 构建交易
            nonce = from_w3.eth.get_transaction_count(from_address)
            gas_price = from_w3.eth.gas_price
            
            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': gas_price,
                'chainId': from_config['chain_id']
            }
            
            # 签名并发送
            signed_tx = from_w3.eth.account.sign_transaction(tx, from_private_key)
            tx_hash = from_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"  ✅ 交易已发送: {tx_hash.hex()}")
            logger.info(f"  浏览器: {from_config['explorer']}/tx/{tx_hash.hex()}")
            
            return {
                'success': True,
                'from_chain': from_chain,
                'to_chain': to_chain,
                'from_address': from_address,
                'to_address': to_address,
                'amount': amount,
                'tx_hash': tx_hash.hex(),
                'explorer_url': f"{from_config['explorer']}/tx/{tx_hash.hex()}"
            }
            
        except Exception as e:
            logger.error(f"  ❌ 跨链桥接失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def multi_chain_mixing_path(
        self,
        start_chain: str,
        num_hops: int
    ) -> list:
        """
        生成多链混币路径
        
        Args:
            start_chain: 起始链
            num_hops: 跳数
        
        Returns:
            路径列表 [{'chain': 'bsc', 'action': 'mix'}, {'chain': 'polygon', 'action': 'bridge'}, ...]
        """
        available_chains = list(self.chains.keys())
        if start_chain not in available_chains:
            raise ValueError(f"起始链 {start_chain} 不可用")
        
        path = []
        current_chain = start_chain
        
        # 在起始链上混币
        path.append({
            'chain': current_chain,
            'action': 'mix',
            'hops': max(10, num_hops // 4)
        })
        
        # 跨链到其他链
        remaining_chains = [c for c in available_chains if c != current_chain]
        
        if len(remaining_chains) >= 2:
            # 至少跨 2 条链
            chain1 = random.choice(remaining_chains)
            path.append({
                'chain': chain1,
                'action': 'bridge',
                'from': current_chain,
                'to': chain1
            })
            
            # 在第二条链上混币
            path.append({
                'chain': chain1,
                'action': 'mix',
                'hops': max(10, num_hops // 4)
            })
            
            # 跨到第三条链
            remaining_chains2 = [c for c in remaining_chains if c != chain1]
            if remaining_chains2:
                chain2 = random.choice(remaining_chains2)
                path.append({
                    'chain': chain2,
                    'action': 'bridge',
                    'from': chain1,
                    'to': chain2
                })
                
                # 在第三条链上混币
                path.append({
                    'chain': chain2,
                    'action': 'mix',
                    'hops': max(10, num_hops // 4)
                })
                
                # 桥回起始链
                path.append({
                    'chain': start_chain,
                    'action': 'bridge',
                    'from': chain2,
                    'to': start_chain
                })
        
        # 最后在起始链上汇总
        path.append({
            'chain': start_chain,
            'action': 'collect'
        })
        
        return path


if __name__ == '__main__':
    # 测试
    print("=" * 60)
    print("跨链桥接引擎测试")
    print("=" * 60)
    
    bridge = CrossChainBridge(use_tor=False)
    
    print(f"\n可用链: {list(bridge.chains.keys())}")
    
    # 生成跨链路径
    path = bridge.multi_chain_mixing_path('bsc_testnet', 100)
    print(f"\n跨链混币路径:")
    for i, step in enumerate(path):
        print(f"  {i+1}. {step}")
