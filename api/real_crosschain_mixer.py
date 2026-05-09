"""
真实跨链混币引擎 - 基于 LiFi API

核心流程：
1. 源地址 → 中间地址 A（BSC）
2. 中间地址 A → 中间地址 B（Polygon，通过 LiFi 跨链）
3. 中间地址 B → 中间地址 C（Arbitrum，通过 LiFi 跨链）
4. 中间地址 C → 目标地址（BSC，通过 LiFi 跨链）

隐私保护：
- 每次跨链使用新的中间地址
- 跨链桥只能看到中间地址之间的交易
- 链上分析工具无法关联源地址和目标地址
"""
import requests
import time
import logging
import os
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from eth_account import Account

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LiFi API
LIFI_API_BASE = "https://li.quest/v1"

# 链配置
CHAIN_CONFIG = {
    'bsc': {
        'id': 56,
        'name': 'BSC',
        'rpc': 'https://bsc-dataseed.binance.org',
        'symbol': 'BNB',
        'explorer': 'https://bscscan.com'
    },
    'polygon': {
        'id': 137,
        'name': 'Polygon',
        'rpc': 'https://polygon-rpc.com',
        'symbol': 'MATIC',
        'explorer': 'https://polygonscan.com'
    },
    'arbitrum': {
        'id': 42161,
        'name': 'Arbitrum',
        'rpc': 'https://arb1.arbitrum.io/rpc',
        'symbol': 'ETH',
        'explorer': 'https://arbiscan.io'
    },
    'optimism': {
        'id': 10,
        'name': 'Optimism',
        'rpc': 'https://mainnet.optimism.io',
        'symbol': 'ETH',
        'explorer': 'https://optimistic.etherscan.io'
    },
    'base': {
        'id': 8453,
        'name': 'Base',
        'rpc': 'https://mainnet.base.org',
        'symbol': 'ETH',
        'explorer': 'https://basescan.org'
    },
    'avalanche': {
        'id': 43114,
        'name': 'Avalanche',
        'rpc': 'https://api.avax.network/ext/bc/C/rpc',
        'symbol': 'AVAX',
        'explorer': 'https://snowtrace.io'
    }
}

# 原生币地址
NATIVE_TOKEN = '0x0000000000000000000000000000000000000000'


class RealCrossChainMixer:
    """真实跨链混币引擎"""
    
    def __init__(self, verify_ssl: bool = True):
        """
        初始化
        
        Args:
            verify_ssl: 是否验证 SSL（本地测试可能需要关闭）
        """
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        # 如果禁用 SSL，同时禁用警告
        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 初始化各链的 Web3 实例
        self.web3_instances = {}
        for chain_key, config in CHAIN_CONFIG.items():
            try:
                self.web3_instances[chain_key] = Web3(Web3.HTTPProvider(config['rpc']))
            except Exception as e:
                logger.warning(f"初始化 {chain_key} RPC 失败: {e}")
        
        logger.info("✅ 真实跨链混币引擎已初始化")
    
    def get_quote(
        self,
        from_chain: str,
        to_chain: str,
        amount_wei: int,
        from_address: str,
        to_address: str = None
    ) -> Optional[Dict]:
        """
        获取 LiFi 跨链报价 - 带 SSL 自动降级
        """
        from_id = CHAIN_CONFIG[from_chain]['id']
        to_id = CHAIN_CONFIG[to_chain]['id']
        
        params = {
            'fromChain': from_id,
            'toChain': to_id,
            'fromToken': NATIVE_TOKEN,
            'toToken': NATIVE_TOKEN,
            'fromAmount': str(amount_wei),
            'fromAddress': from_address,
            'slippage': 0.03
        }
        if to_address:
            params['toAddress'] = to_address
        
        # 首次尝试 - 根据配置验证 SSL
        try:
            response = self.session.get(
                f"{LIFI_API_BASE}/quote",
                params=params,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"LiFi 报价失败: {response.status_code} - {response.text[:200]}")
                return None
        except requests.exceptions.SSLError as ssl_err:
            # SSL 错误自动降级重试
            logger.warning(f"SSL 错误，自动降级重试: {ssl_err}")
            try:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                fallback_session = requests.Session()
                fallback_session.verify = False
                
                response = fallback_session.get(
                    f"{LIFI_API_BASE}/quote",
                    params=params,
                    timeout=30
                )
                if response.status_code == 200:
                    # 降级成功，之后都不验证 SSL
                    self.session = fallback_session
                    logger.info("✅ SSL 降级成功")
                    return response.json()
                else:
                    logger.error(f"LiFi 报价失败(降级): {response.status_code}")
                    return None
            except Exception as e:
                logger.error(f"LiFi 降级重试失败: {e}")
                return None
        except Exception as e:
            logger.error(f"LiFi 报价异常: {e}")
            return None
    
    def execute_bridge(
        self,
        from_chain: str,
        to_chain: str,
        from_private_key: str,
        amount: float,
        to_address: str = None
    ) -> Dict:
        """
        执行一次真实跨链
        
        Args:
            from_chain: 源链
            to_chain: 目标链
            from_private_key: 源地址私钥
            amount: 金额（Ether 单位）
            to_address: 接收地址（默认同发送地址）
        
        Returns:
            {
                'success': bool,
                'tx_hash': str,
                'from_chain': str,
                'to_chain': str,
                'from_amount': float,
                'to_amount_estimated': float,
                'tool': str,
                'duration': int
            }
        """
        w3 = self.web3_instances[from_chain]
        account = Account.from_key(from_private_key)
        from_address = account.address
        
        if not to_address:
            to_address = from_address
        
        amount_wei = w3.to_wei(amount, 'ether')
        
        logger.info(f"\n🌉 跨链: {CHAIN_CONFIG[from_chain]['name']} → {CHAIN_CONFIG[to_chain]['name']}")
        logger.info(f"   金额: {amount} {CHAIN_CONFIG[from_chain]['symbol']}")
        logger.info(f"   从: {from_address[:10]}...")
        logger.info(f"   到: {to_address[:10]}...")
        
        # 1. 获取报价
        quote = self.get_quote(from_chain, to_chain, amount_wei, from_address, to_address)
        if not quote:
            return {
                'success': False,
                'error': '无法获取跨链报价'
            }
        
        estimate = quote.get('estimate', {})
        tool = quote.get('tool', 'N/A')
        duration = estimate.get('executionDuration', 0)
        to_amount_estimated = int(estimate.get('toAmount', 0)) / 1e18
        
        logger.info(f"   桥接工具: {tool}")
        logger.info(f"   预计到账: {to_amount_estimated:.6f} {CHAIN_CONFIG[to_chain]['symbol']}")
        logger.info(f"   预计时间: {duration} 秒")
        
        # 2. 构建交易
        tx_request = quote.get('transactionRequest')
        if not tx_request:
            return {
                'success': False,
                'error': '报价中缺少交易请求'
            }
        
        nonce = w3.eth.get_transaction_count(from_address)
        
        tx = {
            'from': from_address,
            'to': Web3.to_checksum_address(tx_request['to']),
            'value': int(tx_request.get('value', 0)),
            'data': tx_request.get('data', '0x'),
            'gas': int(tx_request.get('gasLimit', 500000)),
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
            'chainId': CHAIN_CONFIG[from_chain]['id']
        }
        
        # 3. 签名并发送
        try:
            signed_tx = w3.eth.account.sign_transaction(tx, from_private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"   ✅ 交易已发送: {tx_hash_hex[:20]}...")
            logger.info(f"   🔗 {CHAIN_CONFIG[from_chain]['explorer']}/tx/{tx_hash_hex}")
            
            # 4. 等待源链确认
            logger.info(f"   ⏳ 等待源链确认...")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 1:
                logger.info(f"   ✅ 源链已确认（区块 {receipt['blockNumber']}）")
                
                return {
                    'success': True,
                    'tx_hash': tx_hash_hex,
                    'from_chain': from_chain,
                    'to_chain': to_chain,
                    'from_address': from_address,
                    'to_address': to_address,
                    'from_amount': amount,
                    'to_amount_estimated': to_amount_estimated,
                    'tool': tool,
                    'duration': duration,
                    'block_number': receipt['blockNumber']
                }
            else:
                return {
                    'success': False,
                    'error': '源链交易失败',
                    'tx_hash': tx_hash_hex
                }
                
        except Exception as e:
            logger.error(f"   ❌ 交易失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def wait_for_arrival(
        self,
        to_chain: str,
        address: str,
        expected_min_amount: float,
        timeout: int = 180
    ) -> Tuple[bool, float]:
        """
        等待跨链资金到账
        
        Args:
            to_chain: 目标链
            address: 接收地址
            expected_min_amount: 预期最小到账金额
            timeout: 超时时间（秒）
        
        Returns:
            (是否到账, 实际到账金额)
        """
        w3 = self.web3_instances[to_chain]
        address = w3.to_checksum_address(address)
        
        # 记录初始余额
        initial_balance = float(w3.from_wei(w3.eth.get_balance(address), 'ether'))
        
        logger.info(f"   ⏳ 等待资金到账 {to_chain} ({address[:10]}...)")
        logger.info(f"      初始余额: {initial_balance:.6f}")
        logger.info(f"      预期增加: {expected_min_amount:.6f}")
        
        start_time = time.time()
        # 前 30 秒快速轮询（每 2 秒），之后慢轮询（每 5 秒）
        fast_interval = 2
        slow_interval = 5
        
        while time.time() - start_time < timeout:
            current_balance = float(w3.from_wei(w3.eth.get_balance(address), 'ether'))
            received = current_balance - initial_balance
            
            if received >= expected_min_amount * 0.9:  # 允许 10% 误差
                elapsed = int(time.time() - start_time)
                logger.info(f"   ✅ 已到账: {received:.6f} ({CHAIN_CONFIG[to_chain]['symbol']}) (耗时 {elapsed} 秒)")
                return True, received
            
            # 自适应轮询间隔
            elapsed = time.time() - start_time
            interval = fast_interval if elapsed < 30 else slow_interval
            time.sleep(interval)
        
        final_balance = float(w3.from_wei(w3.eth.get_balance(address), 'ether'))
        received = final_balance - initial_balance
        logger.warning(f"   ⚠️ 等待超时: 已到账 {received:.6f}")
        return False, received
    
    def generate_temp_account(self) -> Dict:
        """生成临时账户"""
        account = Account.create()
        return {
            'address': account.address,
            'private_key': account.key.hex()
        }
    
    def execute_multi_chain_mixing(
        self,
        from_private_key: str,
        to_address: str,
        amount: float,
        path: List[str] = None
    ) -> Dict:
        """
        执行完整的多链混币
        
        Args:
            from_private_key: 源地址私钥
            to_address: 目标地址
            amount: 金额（源链原生币）
            path: 跨链路径 ['bsc', 'polygon', 'arbitrum', 'bsc']
                  默认 BSC → Polygon → Arbitrum → BSC
        
        Returns:
            执行结果
        """
        if path is None:
            path = ['bsc', 'polygon', 'arbitrum', 'bsc']
        
        start_chain = path[0]
        end_chain = path[-1]
        
        logger.info("=" * 70)
        logger.info("🌉 开始多链混币")
        logger.info("=" * 70)
        logger.info(f"路径: {' → '.join([CHAIN_CONFIG[c]['name'] for c in path])}")
        logger.info(f"金额: {amount} {CHAIN_CONFIG[start_chain]['symbol']}")
        logger.info(f"目标: {to_address}")
        
        # 生成中间账户（每个跨链步骤一个）
        temp_accounts = []
        for i in range(len(path) - 1):
            temp = self.generate_temp_account()
            temp_accounts.append(temp)
            logger.info(f"🔑 临时账户 {i+1}: {temp['address'][:10]}... ({CHAIN_CONFIG[path[i+1]]['name']})")
        
        results = {
            'success': False,
            'path': path,
            'steps': [],
            'temp_accounts': temp_accounts,
            'final_amount': 0
        }
        
        current_private_key = from_private_key
        current_amount = amount
        
        # 执行每一步跨链
        for i in range(len(path) - 1):
            from_chain = path[i]
            to_chain = path[i + 1]
            is_last = (i == len(path) - 2)
            
            # 最后一步：直接跨到目标地址
            # 中间步骤：跨到临时地址
            if is_last:
                bridge_to_address = to_address
                next_private_key = None
            else:
                bridge_to_address = temp_accounts[i]['address']
                next_private_key = temp_accounts[i]['private_key']
            
            logger.info(f"\n{'='*70}")
            logger.info(f"Step {i+1}/{len(path)-1}: {CHAIN_CONFIG[from_chain]['name']} → {CHAIN_CONFIG[to_chain]['name']}")
            logger.info(f"{'='*70}")
            
            # 执行跨链
            bridge_result = self.execute_bridge(
                from_chain=from_chain,
                to_chain=to_chain,
                from_private_key=current_private_key,
                amount=current_amount,
                to_address=bridge_to_address
            )
            
            results['steps'].append({
                'step': i + 1,
                'from_chain': from_chain,
                'to_chain': to_chain,
                'result': bridge_result
            })
            
            if not bridge_result['success']:
                logger.error(f"❌ Step {i+1} 失败，终止混币")
                results['error'] = bridge_result.get('error')
                return results
            
            # 等待跨链完成（资金到账目标链）
            expected_amount = bridge_result['to_amount_estimated']
            arrived, actual_amount = self.wait_for_arrival(
                to_chain=to_chain,
                address=bridge_to_address,
                expected_min_amount=expected_amount,
                timeout=180  # 3 分钟超时
            )
            
            if not arrived:
                logger.error(f"❌ Step {i+1} 等待到账超时")
                results['error'] = f'Step {i+1} 等待跨链到账超时'
                return results
            
            # 准备下一步
            if not is_last:
                current_private_key = next_private_key
                # 保留一点作为 gas（根据目标链调整）
                gas_reserve = 0.001 if to_chain in ['bsc', 'polygon', 'avalanche'] else 0.0001
                current_amount = actual_amount - gas_reserve
                
                if current_amount <= 0:
                    logger.error(f"❌ 到账金额 {actual_amount} 不足以支付 gas {gas_reserve}")
                    results['error'] = '到账金额不足以支付 gas'
                    return results
        
        results['success'] = True
        results['final_amount'] = actual_amount
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 多链混币完成！")
        logger.info(f"   最终到账: {actual_amount:.6f} {CHAIN_CONFIG[end_chain]['symbol']}")
        logger.info(f"   目标地址: {to_address}")
        logger.info("=" * 70)
        
        return results


# 全局实例
_mixer: Optional[RealCrossChainMixer] = None


def get_crosschain_mixer(verify_ssl: bool = True) -> RealCrossChainMixer:
    """获取全局实例"""
    global _mixer
    if _mixer is None:
        _mixer = RealCrossChainMixer(verify_ssl=verify_ssl)
    return _mixer
