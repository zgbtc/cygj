"""LiFi跨链桥接 - 使用LiFi API实现真实跨链"""
import requests
import time
import logging
from typing import Dict, Optional
from web3 import Web3
from eth_account import Account

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LiFi API配置
LIFI_API_BASE = "https://li.quest/v1"

# 链ID映射
CHAIN_IDS = {
    'bsc': 56,
    'polygon': 137,
    'arbitrum': 42161,
    'optimism': 10,
    'avalanche': 43114,
    'base': 8453,
    'ethereum': 1
}

# RPC URLs
RPC_URLS = {
    'bsc': 'https://bsc-dataseed.binance.org',
    'polygon': 'https://polygon-rpc.com',
    'arbitrum': 'https://arb1.arbitrum.io/rpc',
    'optimism': 'https://mainnet.optimism.io',
    'avalanche': 'https://api.avax.network/ext/bc/C/rpc',
    'base': 'https://mainnet.base.org',
    'ethereum': 'https://eth.llamarpc.com'
}


class LiFiBridge:
    """LiFi跨链桥接引擎"""
    
    def __init__(self, use_proxy: bool = False):
        """
        初始化LiFi桥接
        
        Args:
            use_proxy: 是否使用代理池
        """
        self.use_proxy = use_proxy
        self.session = requests.Session()
        
        # 如果使用代理
        if use_proxy:
            try:
                from proxy_pool import get_proxy_pool
                proxy_pool = get_proxy_pool()
                proxy = proxy_pool.get_random_proxy()
                if proxy:
                    self.session.proxies = {'http': proxy, 'https': proxy}
                    logger.info(f"🔒 使用代理: {proxy}")
            except Exception as e:
                logger.warning(f"代理初始化失败: {e}")
        
        logger.info("✅ LiFi桥接引擎已初始化")
    
    def get_quote(
        self,
        from_chain: str,
        to_chain: str,
        from_token: str,
        to_token: str,
        amount: float,
        from_address: str
    ) -> Optional[Dict]:
        """
        获取跨链报价
        
        Args:
            from_chain: 源链名称
            to_chain: 目标链名称
            from_token: 源代币地址（0x0000...为原生币）
            to_token: 目标代币地址
            amount: 金额（Wei）
            from_address: 发送地址
        
        Returns:
            报价信息
        """
        try:
            from_chain_id = CHAIN_IDS.get(from_chain)
            to_chain_id = CHAIN_IDS.get(to_chain)
            
            if not from_chain_id or not to_chain_id:
                raise ValueError(f"不支持的链: {from_chain} 或 {to_chain}")
            
            # 调用LiFi API获取报价
            url = f"{LIFI_API_BASE}/quote"
            params = {
                'fromChain': from_chain_id,
                'toChain': to_chain_id,
                'fromToken': from_token,
                'toToken': to_token,
                'fromAmount': str(int(amount)),
                'fromAddress': from_address,
                'slippage': 0.03  # 3% 滑点
            }
            
            logger.info(f"📊 获取跨链报价: {from_chain} → {to_chain}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            quote = response.json()
            
            if 'estimate' in quote:
                estimate = quote['estimate']
                logger.info(f"  预计收到: {Web3.from_wei(int(estimate['toAmount']), 'ether')} {to_chain}")
                logger.info(f"  费用: {Web3.from_wei(int(estimate.get('gasCosts', [{}])[0].get('amount', 0)), 'ether')}")
            
            return quote
            
        except Exception as e:
            logger.error(f"获取报价失败: {e}")
            return None
    
    def execute_bridge(
        self,
        from_chain: str,
        to_chain: str,
        from_private_key: str,
        to_address: str,
        amount: float
    ) -> Dict:
        """
        执行跨链桥接
        
        Args:
            from_chain: 源链
            to_chain: 目标链
            from_private_key: 私钥
            to_address: 目标地址
            amount: 金额（Ether单位）
        
        Returns:
            交易结果
        """
        try:
            # 初始化Web3
            from_chain_id = CHAIN_IDS.get(from_chain)
            rpc_url = RPC_URLS.get(from_chain)
            
            if not rpc_url:
                raise ValueError(f"不支持的链: {from_chain}")
            
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            account = Account.from_key(from_private_key)
            from_address = account.address
            
            # 转换金额为Wei
            amount_wei = w3.to_wei(amount, 'ether')
            
            # 原生币地址（0x0000...）
            native_token = '0x0000000000000000000000000000000000000000'
            
            logger.info(f"\n🌉 执行跨链桥接:")
            logger.info(f"  从: {from_chain} ({from_address[:10]}...)")
            logger.info(f"  到: {to_chain} ({to_address[:10]}...)")
            logger.info(f"  金额: {amount}")
            
            # 1. 获取报价
            quote = self.get_quote(
                from_chain=from_chain,
                to_chain=to_chain,
                from_token=native_token,
                to_token=native_token,
                amount=amount_wei,
                from_address=from_address
            )
            
            if not quote:
                raise Exception("无法获取跨链报价")
            
            # 2. 构建交易
            if 'transactionRequest' not in quote:
                raise Exception("报价中缺少交易请求")
            
            tx_request = quote['transactionRequest']
            
            # 3. 准备交易参数
            nonce = w3.eth.get_transaction_count(from_address)
            
            tx = {
                'from': from_address,
                'to': Web3.to_checksum_address(tx_request['to']),
                'value': int(tx_request.get('value', 0), 16) if isinstance(tx_request.get('value', 0), str) else int(tx_request.get('value', 0)),
                'data': tx_request.get('data', '0x'),
                'gas': int(tx_request.get('gasLimit', '0x7A120'), 16) if isinstance(tx_request.get('gasLimit', 500000), str) else int(tx_request.get('gasLimit', 500000)),
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
                'chainId': from_chain_id
            }
            
            logger.info(f"  Gas估算: {tx['gas']}")
            
            # 4. 签名并发送
            signed_tx = w3.eth.account.sign_transaction(tx, from_private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"  ✅ 交易已发送: {tx_hash.hex()}")
            
            # 5. 等待确认
            logger.info(f"  ⏳ 等待确认...")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt['status'] == 1:
                logger.info(f"  ✅ 跨链成功！")
                
                return {
                    'success': True,
                    'from_chain': from_chain,
                    'to_chain': to_chain,
                    'tx_hash': tx_hash.hex(),
                    'amount': amount,
                    'quote': quote
                }
            else:
                raise Exception("交易失败")
                
        except Exception as e:
            logger.error(f"  ❌ 跨链失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_supported_chains(self) -> list:
        """获取支持的链列表"""
        try:
            url = f"{LIFI_API_BASE}/chains"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            chains = response.json()
            return [{'id': c['id'], 'name': c['name'], 'key': c['key']} for c in chains.get('chains', [])]
            
        except Exception as e:
            logger.error(f"获取链列表失败: {e}")
            return []

    def multi_chain_mixing_path(self, base_chain: str, num_hops: int) -> list:
        """
        生成多链隐私转账路径（每 10 跳跨链一次）
        
        Args:
            base_chain: 起始链（如 'bsc', 'bsc_testnet'）
            num_hops: 总跳数（用户指定）
        
        Returns:
            路径列表，每个元素为 {'chain': str, 'hop': int, 'type': 'same_chain'|'cross_chain'}
        
        规则：
        - 每 10 跳后插入一次跨链
        - 跨链到随机中间链
        - 最后一次跨链回到起始链（目标地址在起始链）
        """
        import random

        # 标准化链名
        chain_key = base_chain.replace('_testnet', '')
        if chain_key not in CHAIN_IDS:
            chain_key = 'bsc'

        # 可用的中间链（排除起始链）
        relay_chains = ['polygon', 'arbitrum', 'optimism', 'base']
        relay_chains = [c for c in relay_chains if c in CHAIN_IDS and c != chain_key]

        path = []
        current_chain = chain_key
        cross_interval = 10  # 每 10 跳跨链一次

        for hop_idx in range(1, num_hops + 1):
            # 判断是否需要跨链
            is_cross_hop = (hop_idx % cross_interval == 0) and (hop_idx < num_hops)
            is_last_hop = (hop_idx == num_hops)

            if is_last_hop and current_chain != chain_key:
                # 最后一跳：确保回到起始链（目标地址在起始链）
                path.append({
                    'chain': chain_key,
                    'hop': hop_idx,
                    'type': 'cross_chain',
                    'from_chain': current_chain,
                    'to_chain': chain_key
                })
                current_chain = chain_key
            elif is_cross_hop:
                # 跨链跳：切到一个不同的链
                candidates = [c for c in relay_chains + [chain_key] if c != current_chain]
                if not candidates:
                    candidates = relay_chains or [chain_key]
                next_chain = random.choice(candidates)
                path.append({
                    'chain': next_chain,
                    'hop': hop_idx,
                    'type': 'cross_chain',
                    'from_chain': current_chain,
                    'to_chain': next_chain
                })
                current_chain = next_chain
            else:
                # 同链跳
                path.append({
                    'chain': current_chain,
                    'hop': hop_idx,
                    'type': 'same_chain'
                })

        cross_count = sum(1 for p in path if p['type'] == 'cross_chain')
        logger.info(
            f"🗺️ 生成多链路径: {num_hops} 跳, 每 10 跳跨链一次, "
            f"共 {cross_count} 次跨链"
        )
        return path


# 全局实例
_lifi_bridge = None

def get_lifi_bridge(use_proxy: bool = False) -> LiFiBridge:
    """获取全局LiFi桥接实例"""
    global _lifi_bridge
    if _lifi_bridge is None:
        _lifi_bridge = LiFiBridge(use_proxy=use_proxy)
    return _lifi_bridge


if __name__ == '__main__':
    # 测试
    print("=" * 60)
    print("LiFi跨链桥接测试")
    print("=" * 60)
    
    bridge = LiFiBridge(use_proxy=False)
    
    # 获取支持的链
    chains = bridge.get_supported_chains()
    print(f"\n支持的链: {len(chains)}")
    for chain in chains[:10]:
        print(f"  - {chain['name']} (ID: {chain['id']})")
