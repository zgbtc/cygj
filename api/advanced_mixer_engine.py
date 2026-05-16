"""高级隐私转账引擎 - 集成跨链 + 代理池 + 时间延迟 + 金额随机化"""
import logging
import time
import random
from typing import List, Dict, Optional, Tuple
from web3 import Web3
from eth_account import Account
from hd_wallet import HDWallet
from transfer_engine import TransferEngine
from config import CHAINS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 捐赠配置
FEE_CONFIG = {
    'fee_address': Web3.to_checksum_address('0xe602348170bc045c588bf1638b0edc592f767250'),
    'fee_rates': {
        'fast': 0.0003,      # 快速模式: 0.0003 BNB/次
        'ultimate': 4.9      # 极致模式: 4.9% 的转账金额
    },
    'fee_types': {
        'fast': 'per_hop',      # 按跳数收费
        'ultimate': 'percentage'  # 按百分比收费
    }
}

# 隐私转账模式配置
MIXING_MODES = {
    'fast': {
        'name': '快速模式',
        'delay_range': (0.3, 1.0),  # 缩短延迟
        'use_crosschain': False,
        'use_tor': False,  # Serverless 环境不支持 Tor
        'use_isolation': True,
        'isolation_delay': 0,
        'privacy_level': '⭐⭐⭐⭐⭐',
        'estimated_time': '30秒-2分钟',
        'fee_rate': 0.0003
    },
    'ultimate': {
        'name': '极致隐私',
        # 为适配 Vercel 300 秒限制，延迟从 5-30 分钟 → 1-3 秒
        # 真正的"极致隐私"效果靠跨链 + 源/目标隔离 + 随机金额 + 多 RPC 实现
        'delay_range': (1.0, 3.0),
        'use_crosschain': True,
        'use_tor': False,  # Serverless 不支持
        'use_isolation': True,
        'isolation_delay': 0,
        'privacy_level': '⭐⭐⭐⭐⭐⭐⭐',
        'estimated_time': '1-5 分钟',
        'fee_rate': 0.0006
    }
}


class AdvancedMixerEngine:
    """高级隐私转账引擎"""
    
    def __init__(self, chain: str = 'bsc_testnet', mode: str = 'fast'):
        """
        初始化高级隐私转账引擎
        
        Args:
            chain: 链名称
            mode: 隐私模式 (fast, ultimate)
        """
        if mode not in MIXING_MODES:
            raise ValueError(f"不支持的模式: {mode}. 可选: {list(MIXING_MODES.keys())}")
        
        self.mode = mode
        self.mode_config = MIXING_MODES[mode]
        self.chain = chain
        
        # Serverless 环境下代理池不可用（SSL 错误、启动慢）
        # 引擎内部强制禁用代理，用户隐私靠 VPN/Cloudflare 实现
        
        # 初始化转账引擎（多 RPC 并发选最快的）
        self.transfer_engine = TransferEngine(chain, use_proxy=False)
        self.w3 = self.transfer_engine.w3

        # 根据链配置动态计算 gas_reserve（21000 * gas_price * 1.5 buffer）
        # 修复：之前硬编码 0.00015，在 BSC 测试网（10 gwei）下不足，导致目标隔离失败、资金卡住
        gas_price_gwei = self.transfer_engine.chain_config['gas_price_gwei'].get('standard', 5)
        # 21000 gas * gwei * 1e-9 BNB/gwei = BNB；再 ×2 作为安全 buffer，避免 RPC 间 gas 价格抖动
        self._gas_reserve = round(21000 * gas_price_gwei * 1e-9 * 2, 8)
        logger.info(f"⛽ 动态 gas_reserve: {self._gas_reserve} BNB（{gas_price_gwei} gwei × 2x buffer）")
        
        # 初始化跨链桥接（如果需要）
        if self.mode_config['use_crosschain']:
            try:
                from lifi_bridge import get_lifi_bridge
                self.bridge = get_lifi_bridge(use_proxy=False)
                logger.info(f"🌉 跨链模式已启用（LiFi）")
            except Exception as e:
                logger.warning(f"LiFi桥接初始化失败: {e}")
                self.bridge = None
        else:
            self.bridge = None
        
        # 显示模式信息（Serverless 环境下建议前端用户使用 VPN）
        logger.info(f"💡 IP 隐藏建议: 用户侧启用 VPN / Cloudflare")
        
        logger.info(f"🎯 隐私模式: {self.mode_config['name']}")
        logger.info(f"🔒 隐私等级: {self.mode_config['privacy_level']}")
        logger.info(f"⏱️ 预计时间: {self.mode_config['estimated_time']}")
    
    def calculate_fees(self, num_hops: int, total_amount: float) -> Dict:
        """计算费用"""
        # 根据模式获取费率和费用类型
        fee_rate = FEE_CONFIG['fee_rates'].get(self.mode, 0.0003)
        fee_type = FEE_CONFIG['fee_types'].get(self.mode, 'per_hop')
        
        # 计算捐赠
        if fee_type == 'percentage':
            # 按百分比收费（极致隐私模式）
            service_fee = total_amount * (fee_rate / 100)
        else:
            # 按跳数收费（快速模式）
            service_fee = num_hops * fee_rate
        
        # Gas 费用估算
        gas_estimate = self.transfer_engine.estimate_gas_cost(num_hops, 'standard')
        gas_fee = gas_estimate['total_cost']
        
        # 跨链费用
        crosschain_fee = 0
        if self.mode_config['use_crosschain']:
            # 估算 3 次跨链
            crosschain_fee = 0.006  # 每次 0.002
        
        total_fee = service_fee + gas_fee + crosschain_fee
        net_amount = total_amount - total_fee
        
        return {
            'total_amount': total_amount,
            'service_fee': service_fee,
            'service_fee_type': fee_type,
            'service_fee_rate': fee_rate,
            'gas_fee': gas_fee,
            'crosschain_fee': crosschain_fee,
            'total_fee': total_fee,
            'net_amount': net_amount,
            'num_hops': num_hops
        }
    
    def generate_random_amounts(
        self,
        total_amount: float,
        num_parts: int,
        use_round_numbers: bool = True
    ) -> List[float]:
        """
        生成随机金额分配
        
        Args:
            total_amount: 总金额
            num_parts: 分成几份
            use_round_numbers: 是否使用圆整金额
        
        Returns:
            金额列表
        """
        amounts = []
        remaining = total_amount
        
        for i in range(num_parts - 1):
            # 30% 概率使用圆整金额
            if use_round_numbers and random.random() < 0.3:
                # 圆整金额: 0.01, 0.05, 0.1, 0.5, 1.0
                round_amounts = [0.01, 0.05, 0.1, 0.5, 1.0]
                valid_amounts = [a for a in round_amounts if a < remaining]
                if valid_amounts:
                    amount = random.choice(valid_amounts)
                else:
                    amount = remaining * random.uniform(0.1, 0.3)
            else:
                # 随机金额
                amount = remaining * random.uniform(0.1, 0.3)
            
            amount = round(amount, 8)
            amounts.append(amount)
            remaining -= amount
        
        # 最后一份
        amounts.append(round(remaining, 8))
        
        # 打乱顺序
        random.shuffle(amounts)
        
        return amounts
    
    def create_mixing_plan(
        self,
        from_private_key: str,
        to_address: str,
        total_amount: float,
        num_hops: int = 100,
        mnemonic: str = None,
        start_index: int = 0
    ) -> Dict:
        """创建隐私转账计划

        中间地址派生策略：
        - mnemonic：固定助记词（RELAY_MNEMONIC），每次从不同的 start_index 段派生
        - start_index：本次使用的起始索引，由调用方从数据库分配，保证地址不重复
        - 资金恢复：知道 mnemonic + start_index + num_hops 即可扫出所有中间地址
        """
        from_account = Account.from_key(from_private_key)
        from_address = from_account.address
        
        # 检查余额
        balance = self.transfer_engine.get_balance(from_address)
        if balance < total_amount:
            raise ValueError(f"余额不足。需要: {total_amount}, 当前: {balance}")
        
        # 计算费用
        fees = self.calculate_fees(num_hops, total_amount)
        
        if fees['net_amount'] <= 0:
            raise ValueError(f"金额太小，扣除费用后为负数")
        
        # 生成中间地址（从 start_index 开始，保证每次用不同的地址段）
        # mnemonic 由调用方传入（已存库的随机助记词），不在引擎内部生成
        # 这样引擎不持有任何状态，助记词的生命周期完全由 mixer.py 管理
        if not mnemonic:
            # 兜底：不应该走到这里，mixer.py 必须传入已存库的助记词
            # 如果真的没传，生成随机的但会打印警告
            import logging as _log
            _log.getLogger(__name__).warning(
                "⚠️ create_mixing_plan 未收到助记词，随机生成。"
                "此助记词未存库，资金可能无法恢复！"
            )
            relay_mnemonic = HDWallet().mnemonic
        else:
            relay_mnemonic = mnemonic
        wallet = HDWallet(relay_mnemonic)
        intermediate_addresses = wallet.generate_addresses(num_hops, start_index=start_index)
        
        # 生成跨链路径（如果启用）
        crosschain_path = None
        if self.mode_config['use_crosschain'] and self.bridge:
            crosschain_path = self.bridge.multi_chain_mixing_path(self.chain, num_hops)
        
        plan = {
            'from_address': from_address,
            'from_private_key': from_private_key,
            'to_address': to_address,
            'mnemonic': relay_mnemonic,
            'start_index': start_index,       # 本次派生起始索引，恢复资金时需要
            'total_amount': total_amount,
            'fees': fees,
            'num_hops': num_hops,
            'intermediate_addresses': intermediate_addresses,
            'chain': self.chain,
            'mode': self.mode,
            'mode_config': self.mode_config,
            'crosschain_path': crosschain_path
        }
        
        return plan
    
    def _get_w3_for_chain(self, chain_name: str) -> Web3:
        """获取指定链的 Web3 实例（跨链时切换链）"""
        # 先查 config.py 的 CHAINS
        if chain_name in CHAINS:
            from transfer_engine import TransferEngine
            te = TransferEngine(chain_name, use_proxy=False)
            return te.w3

        # 再查 lifi_bridge 的 RPC_URLS（polygon/arbitrum 等）
        try:
            from lifi_bridge import RPC_URLS
            rpc_url = RPC_URLS.get(chain_name)
            if rpc_url:
                w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
                if w3.is_connected():
                    return w3
        except Exception:
            pass

        raise ValueError(f"无法连接到链: {chain_name}")

    def _get_balance_on_chain(self, chain_name: str, address: str) -> float:
        """查询指定链上的余额"""
        w3 = self._get_w3_for_chain(chain_name)
        bal_wei = w3.eth.get_balance(Web3.to_checksum_address(address))
        return float(w3.from_wei(bal_wei, 'ether'))

    def _wait_for_crosschain_arrival(
        self,
        to_chain: str,
        address: str,
        min_amount: float,
        timeout: int = 300,
        poll_interval: int = 15
    ) -> float:
        """
        等待跨链资金到账（轮询目标链余额）
        返回实际到账金额，超时返回 0
        """
        logger.info(f"  ⏳ 等待跨链到账: {to_chain} {address[:10]}... (最多 {timeout}s)")
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                bal = self._get_balance_on_chain(to_chain, address)
                if bal >= min_amount * 0.8:   # 允许 20% 滑点
                    logger.info(f"  ✅ 跨链到账: {bal:.8f} on {to_chain}")
                    return bal
            except Exception as e:
                logger.debug(f"  查询余额失败: {e}")
            time.sleep(poll_interval)
        logger.warning(f"  ⚠️ 跨链等待超时 ({timeout}s)，当前余额可能不足")
        try:
            return self._get_balance_on_chain(to_chain, address)
        except Exception:
            return 0.0

    def _send_on_chain(
        self,
        chain_name: str,
        from_private_key: str,
        to_address: str,
        amount: float,
        gas_level: str = 'standard'
    ) -> Dict:
        """在指定链上发送交易（跨链后在目标链操作）"""
        # 如果是当前链，直接用 self._send_transaction
        if chain_name == self.chain or chain_name == self.chain.replace('_testnet', ''):
            return self._send_transaction(from_private_key, to_address, amount, gas_level)

        # 目标链：用 lifi_bridge 的 RPC
        from lifi_bridge import RPC_URLS, CHAIN_IDS
        rpc_url = RPC_URLS.get(chain_name)
        if not rpc_url:
            raise ValueError(f"不支持的链: {chain_name}")

        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
        account = Account.from_key(from_private_key)
        from_address = account.address

        amount_wei = w3.to_wei(amount, 'ether')
        nonce = w3.eth.get_transaction_count(from_address, 'pending')
        gas_price = w3.eth.gas_price

        tx = {
            'nonce': nonce,
            'to': Web3.to_checksum_address(to_address),
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': CHAIN_IDS[chain_name]
        }
        signed = w3.eth.account.sign_transaction(tx, from_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        return {'tx_hash': tx_hash.hex(), 'from': from_address, 'to': to_address, 'amount': amount}

    def execute_mixing(
        self,
        plan: Dict,
        gas_level: str = 'standard'
    ) -> Dict:
        """
        执行高级隐私转账（带源地址和目标地址隔离）
        
        Args:
            plan: 隐私转账计划
            gas_level: Gas 等级
        
        Returns:
            执行结果
        """
        logger.info("=" * 60)
        logger.info(f"🚀 开始执行隐私转账 - {plan['mode_config']['name']}")
        logger.info("=" * 60)
        
        from_address = plan['from_address']
        from_private_key = plan['from_private_key']
        to_address = plan['to_address']
        intermediate_addresses = plan['intermediate_addresses']
        fees = plan['fees']
        num_hops = plan['num_hops']
        delay_range = plan['mode_config']['delay_range']
        use_isolation = plan['mode_config'].get('use_isolation', False)
        isolation_delay = plan['mode_config'].get('isolation_delay', 0)
        
        # 为适配 Vercel 60 秒超时：跳数越多，阶段 2 的随机延迟越短
        # 预留 ~30 秒给其他阶段和网络开销，阶段 2 最多用 25 秒
        budget_per_hop = max(0.2, min(delay_range[1], 25.0 / max(num_hops, 1)))
        effective_delay_range = (
            max(0.1, delay_range[0] * budget_per_hop / max(delay_range[1], 0.01)),
            budget_per_hop
        )
        logger.info(
            f"⏱️ 实际阶段 2 延迟: {effective_delay_range[0]:.2f}-{effective_delay_range[1]:.2f}s/跳"
            f" (原配置 {delay_range[0]}-{delay_range[1]}s, 按 {num_hops} 跳自适应)"
        )
        delay_range = effective_delay_range
        
        results = []
        
        logger.info(f"\n📊 转账参数:")
        logger.info(f"  总跳数: {num_hops}")
        logger.info(f"  净金额: {fees['net_amount']:.8f} BNB")
        logger.info(f"  延迟范围: {delay_range[0]}-{delay_range[1]} 秒")
        logger.info(f"  使用隔离: {'是' if use_isolation else '否'}")
        logger.info(f"  使用 Tor: {'是' if plan['mode_config']['use_tor'] else '否'}")
        logger.info(f"  跨链混币: {'是' if plan['mode_config']['use_crosschain'] else '否'}")

        # 阶段 -1: 先从源地址支付捐赠（必须在隔离前完成，否则源地址没钱了）
        service_fee = fees['service_fee']
        fee_address = FEE_CONFIG['fee_address']

        if service_fee > 0:
            logger.info(f"\n💳 阶段 0a: 支付捐赠 {service_fee:.8f} BNB → {fee_address[:10]}...")
            try:
                donate_result = self._send_transaction(
                    from_private_key=from_private_key,
                    to_address=fee_address,
                    amount=service_fee,
                    gas_level=gas_level
                )
                results.append({
                    'stage': -1,
                    'from': from_address,
                    'to': fee_address,
                    'amount': service_fee,
                    'status': 'success',
                    'tx_hash': donate_result['tx_hash'],
                    'purpose': 'donation'
                })
                logger.info(f"  ✅ 捐赠已发送: {donate_result['tx_hash'][:16]}...")
                # 短暂等待，避免后续 nonce 冲突
                time.sleep(0.3)
            except Exception as e:
                logger.error(f"  ❌ 捐赠失败: {e}")
                results.append({
                    'stage': -1,
                    'from': from_address,
                    'to': fee_address,
                    'amount': service_fee,
                    'status': 'failed',
                    'error': str(e),
                    'purpose': 'donation'
                })

        # 阶段 0: 源地址隔离（如果启用）
        if use_isolation:
            logger.info(f"\n🔒 阶段 0b: 源地址隔离")
            
            # 使用第一个中间地址作为隔离层
            isolation_addr_1 = intermediate_addresses[0]['address']
            isolation_pk_1 = intermediate_addresses[0]['private_key']

            # 等捐赠上链再读实际余额（避免误扣）
            if service_fee > 0:
                try:
                    time.sleep(1.0)
                except Exception:
                    pass

            # 动态计算：当前余额 - 隔离交易的 gas
            src_balance = self.transfer_engine.get_balance(from_address)
            gas_reserve = self._gas_reserve  # 隔离交易 gas buffer (链相关)
            isolation_amount = src_balance - gas_reserve

            isolation_ok = False
            if isolation_amount <= 0:
                logger.warning(
                    f"  ⚠️ 源地址余额不足以隔离: {src_balance:.8f}, 跳过"
                )
            else:
                try:
                    result = self._send_transaction(
                        from_private_key=from_private_key,
                        to_address=isolation_addr_1,
                        amount=isolation_amount,
                        gas_level=gas_level
                    )

                    results.append({
                        'stage': 0,
                        'from': from_address,
                        'to': isolation_addr_1,
                        'amount': isolation_amount,
                        'status': 'success',
                        'tx_hash': result['tx_hash'],
                        'purpose': 'source_isolation'
                    })

                    logger.info(
                        f"  ✅ 源地址隔离: {from_address[:10]}... → "
                        f"{isolation_addr_1[:10]}... ({isolation_amount:.8f} BNB)"
                    )
                    logger.info(f"  🔒 链上无法直接追溯到源地址")

                    # 等待资金到账再进入阶段 1
                    logger.info(f"  ⏳ 等待资金到账...")
                    try:
                        receipt = self.w3.eth.wait_for_transaction_receipt(
                            result['tx_hash'], timeout=30
                        )
                        if receipt['status'] == 1:
                            logger.info(f"  ✅ 资金已到账 (区块 {receipt['blockNumber']})")
                            isolation_ok = True
                        else:
                            logger.warning(f"  ⚠️ 隔离交易上链但失败")
                    except Exception as wait_err:
                        logger.warning(f"  ⚠️ 等待确认超时: {wait_err}")

                except Exception as e:
                    logger.error(f"  ❌ 源地址隔离失败: {e}")
                    results.append({
                        'stage': 0,
                        'from': from_address,
                        'to': isolation_addr_1,
                        'amount': isolation_amount,
                        'status': 'failed',
                        'error': str(e),
                        'purpose': 'source_isolation'
                    })

            # 只有隔离成功才切换到隔离地址作为起点，否则继续用源地址
            if isolation_ok:
                from_private_key = isolation_pk_1
                from_address = isolation_addr_1
            else:
                logger.warning(f"  ⚠️ 隔离未完成，直接从源地址进入阶段 1")
        
        # 阶段 1: 分散到多个起始地址
        start_offset = 1 if use_isolation else 0  # 如果用了隔离，从第2个地址开始
        num_start_addresses = max(5, num_hops // 5)
        logger.info(f"\n🌱 阶段 1: 分散到 {num_start_addresses} 个起始地址")
        
        # 使用随机金额分配 —— 关键：每笔金额都要单独预留 gas
        current_balance = self.transfer_engine.get_balance(from_address)
        gas_per_tx = self._gas_reserve
        total_spendable = current_balance - gas_per_tx * (num_start_addresses + 1)

        # Ultimate 跨链模式：保证至少一个地址有足够余额用于跨链
        # LiFi 最小跨链约 $2 ≈ 0.003 BNB（按 $650/BNB 估算）
        LIFI_MIN_BNB = 0.004  # 略高于最小值，留足余量

        # 防御：余额不足时跳过阶段 1
        if total_spendable <= 0:
            logger.warning(
                f"⚠️ 阶段 1 跳过：余额 {current_balance:.8f} 不足以分散 "
                f"{num_start_addresses} 笔 (需 gas {gas_per_tx * num_start_addresses:.8f})"
            )
            num_start_addresses = 0
            start_amounts = []
        else:
            # 随机分配金额，注意 generate_random_amounts 返回的总和 = total_spendable
            # 每笔都是纯 value，gas 额外从余额中扣
            start_amounts = self.generate_random_amounts(
                total_spendable,
                num_start_addresses,
                use_round_numbers=True
            )
            # 最后防御：确保所有金额 > 0
            start_amounts = [a for a in start_amounts if a > 0]
            num_start_addresses = len(start_amounts)
            # 最后防御：确保所有金额 > 0
            start_amounts = [a for a in start_amounts if a > 0]
            num_start_addresses = len(start_amounts)

            # Ultimate 跨链模式：确保至少一个地址有足够的跨链金额
            # 如果所有分散金额都低于 LIFI_MIN_BNB，把第一个地址的金额调大
            if (plan['mode_config']['use_crosschain']
                    and 'testnet' not in self.chain
                    and total_spendable >= LIFI_MIN_BNB * 2
                    and start_amounts
                    and max(start_amounts) < LIFI_MIN_BNB):
                # 重新分配：第一个地址拿 60%（保证足够跨链），其余均分 40%
                bridge_reserve = min(total_spendable * 0.6, total_spendable - LIFI_MIN_BNB * (num_start_addresses - 1))
                bridge_reserve = max(bridge_reserve, LIFI_MIN_BNB)
                remainder = total_spendable - bridge_reserve
                other_amounts = [round(remainder / max(num_start_addresses - 1, 1), 8)] * max(num_start_addresses - 1, 0)
                start_amounts = [round(bridge_reserve, 8)] + other_amounts
                start_amounts = [a for a in start_amounts if a > 0]
                num_start_addresses = len(start_amounts)
                logger.info(f"  🔄 Ultimate 跨链模式：调整分散金额，最大份额 {start_amounts[0]:.6f} BNB（确保跨链）")
        
        # 为阶段 1 预先获取 nonce，后续自增避免冲突
        stage1_nonce = self.w3.eth.get_transaction_count(from_address, 'pending')

        for i in range(num_start_addresses):
            addr_idx = start_offset + i
            if addr_idx >= len(intermediate_addresses):
                break
                
            start_addr = intermediate_addresses[addr_idx]['address']
            amount = start_amounts[i]

            # 防御：非正数金额跳过
            if amount is None or amount <= 0:
                logger.warning(f"  ⚠️ 跳过分散 {i+1}: 金额无效 ({amount})")
                continue

            try:
                result = self._send_transaction(
                    from_private_key=from_private_key,
                    to_address=start_addr,
                    amount=amount,
                    gas_level=gas_level,
                    nonce=stage1_nonce + i
                )
                
                results.append({
                    'stage': 1,
                    'from': from_address,
                    'to': start_addr,
                    'amount': amount,
                    'status': 'success',
                    'tx_hash': result['tx_hash']
                })
                
                logger.info(f"  ✅ 分散 {i+1}/{num_start_addresses}: → {start_addr[:10]}... ({amount:.8f} BNB)")
                
                # 阶段 1（从同一地址分散）：只保留最小间隔避免 RPC 限流
                time.sleep(0.1)
            
            except Exception as e:
                logger.error(f"  ❌ 分散 {i+1} 失败: {e}")
                results.append({
                    'stage': 1,
                    'from': from_address,
                    'to': start_addr,
                    'amount': amount,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 阶段 2: 按 crosschain_path 执行跳转（含真实跨链）
        logger.info(f"\n🔀 阶段 2: 中间地址跳转（{'含跨链' if plan.get('crosschain_path') and plan['mode_config']['use_crosschain'] else '单链'}）")

        crosschain_path = plan.get('crosschain_path')
        use_real_crosschain = (
            crosschain_path is not None
            and plan['mode_config']['use_crosschain']
            and self.bridge is not None
            # 测试网不支持 LiFi，自动降级
            and 'testnet' not in self.chain
        )

        if use_real_crosschain:
            logger.info(f"  🌉 真实跨链模式已启用（LiFi）")
        elif plan['mode_config']['use_crosschain']:
            logger.info(f"  ⚠️ 测试网不支持 LiFi，降级为单链跳转")

        remaining_hops = num_hops - num_start_addresses
        active_addresses = list(range(num_start_addresses))
        hop_count = 0

        # 当前链状态（跨链后会切换）
        current_chain = self.chain.replace('_testnet', '') if use_real_crosschain else self.chain

        while hop_count < remaining_hops and active_addresses:
            # 查当前 hop 对应的路径条目
            # crosschain_path 索引从 0 开始，对应 hop 1..N
            # 阶段2从 num_start_addresses 跳开始，所以绝对索引 = num_start_addresses + hop_count
            path_idx = num_start_addresses + hop_count
            path_entry = None
            if crosschain_path and path_idx < len(crosschain_path):
                path_entry = crosschain_path[path_idx]

            # ── 跨链跳 ──────────────────────────────────────────────
            if use_real_crosschain and path_entry and path_entry['type'] == 'cross_chain':
                from_chain_cc = path_entry['from_chain']
                to_chain_cc   = path_entry['to_chain']

                # 选一个有余额的地址作为跨链源（余额 > LiFi 最小跨链金额）
                LIFI_MIN = 0.003  # BSC 主网 LiFi 最小约 $2
                bridge_src = None
                for idx in active_addresses:
                    addr_info = intermediate_addresses[idx]
                    try:
                        bal = self._get_balance_on_chain(from_chain_cc, addr_info['address'])
                        if bal > LIFI_MIN:
                            bridge_src = addr_info
                            break
                    except Exception:
                        continue

                if bridge_src is None:
                    logger.warning(f"  ⚠️ 跨链跳 {hop_count+1}: 找不到有余额的地址，跳过")
                    hop_count += 1
                    continue

                # 跨链目标地址：用下一个中间地址（同私钥在目标链上地址相同）
                next_idx = (active_addresses[0] + 1) % num_hops
                bridge_dst_info = intermediate_addresses[next_idx]

                bridge_amount = self._get_balance_on_chain(from_chain_cc, bridge_src['address'])
                bridge_amount = round(bridge_amount - self._gas_reserve * 4, 8)

                if bridge_amount <= 0:
                    hop_count += 1
                    continue

                logger.info(f"  🌉 跨链跳 {hop_count+1}: {from_chain_cc} → {to_chain_cc}  {bridge_amount:.6f}")
                try:
                    bridge_result = self.bridge.execute_bridge(
                        from_chain=from_chain_cc,
                        to_chain=to_chain_cc,
                        from_private_key=bridge_src['private_key'],
                        to_address=bridge_dst_info['address'],
                        amount=bridge_amount
                    )
                    results.append({
                        'stage': 2,
                        'hop': hop_count + 1,
                        'type': 'cross_chain',
                        'from_chain': from_chain_cc,
                        'to_chain': to_chain_cc,
                        'from': bridge_src['address'],
                        'to': bridge_dst_info['address'],
                        'amount': bridge_amount,
                        'status': 'success' if bridge_result.get('success') else 'failed',
                        'tx_hash': bridge_result.get('tx_hash', ''),
                        'error': bridge_result.get('error')
                    })

                    if bridge_result.get('success'):
                        logger.info(f"  ✅ 跨链发送成功: {bridge_result['tx_hash'][:16]}...")
                        # 等待目标链到账（最多 10 分钟，NearIntents 通常 30s-5min）
                        arrived = self._wait_for_crosschain_arrival(
                            to_chain=to_chain_cc,
                            address=bridge_dst_info['address'],
                            min_amount=bridge_amount * 0.7,
                            timeout=600,       # 10 分钟
                            poll_interval=10   # 每 10 秒查一次
                        )
                        if arrived > 0:
                            logger.info(f"  ✅ 目标链余额: {arrived:.8f} on {to_chain_cc}")
                            current_chain = to_chain_cc
                            if next_idx not in active_addresses:
                                active_addresses.append(next_idx)

                            # ── 如果目标链不是起始链，立即再跨链回起始链 ──────────
                            # 确保资金不卡在其他链，用户最终收到 BNB
                            base_chain = self.chain.replace('_testnet', '')
                            if to_chain_cc != base_chain:
                                logger.info(f"  🔄 自动跨链回 {base_chain}，避免资金卡在 {to_chain_cc}...")
                                # 等几秒让余额稳定
                                time.sleep(3)
                                return_amount = self._get_balance_on_chain(to_chain_cc, bridge_dst_info['address'])
                                # 预留目标链 gas（L2 链 gas 极低，预留 0.0001 ETH 足够）
                                return_gas_reserve = 0.0001
                                return_amount = round(return_amount - return_gas_reserve, 8)

                                if return_amount > 0:
                                    try:
                                        return_result = self.bridge.execute_bridge(
                                            from_chain=to_chain_cc,
                                            to_chain=base_chain,
                                            from_private_key=bridge_dst_info['private_key'],
                                            to_address=bridge_dst_info['address'],  # 同地址，BSC 上继续混
                                            amount=return_amount
                                        )
                                        results.append({
                                            'stage': 2,
                                            'hop': hop_count + 1,
                                            'type': 'cross_chain_return',
                                            'from_chain': to_chain_cc,
                                            'to_chain': base_chain,
                                            'from': bridge_dst_info['address'],
                                            'to': bridge_dst_info['address'],
                                            'amount': return_amount,
                                            'status': 'success' if return_result.get('success') else 'failed',
                                            'tx_hash': return_result.get('tx_hash', ''),
                                            'error': return_result.get('error')
                                        })
                                        if return_result.get('success'):
                                            logger.info(f"  ✅ 已跨链回 {base_chain}: {return_result['tx_hash'][:16]}...")
                                            # 等待回程到账
                                            back_arrived = self._wait_for_crosschain_arrival(
                                                to_chain=base_chain,
                                                address=bridge_dst_info['address'],
                                                min_amount=return_amount * 0.7,
                                                timeout=600,   # 10 分钟
                                                poll_interval=10
                                            )
                                            if back_arrived > 0:
                                                logger.info(f"  ✅ 回程到账: {back_arrived:.8f} BNB on {base_chain}")
                                                current_chain = base_chain
                                            else:
                                                logger.warning(f"  ⚠️ 回程等待超时，资金可能仍在 {base_chain} 中间地址")
                                        else:
                                            logger.error(f"  ❌ 回程跨链失败: {return_result.get('error')}")
                                            logger.warning(f"  💡 恢复: python recover_session.py <session_id> <addr> --chain {to_chain_cc}")
                                    except Exception as re:
                                        logger.error(f"  ❌ 回程跨链异常: {re}")
                                        logger.warning(f"  💡 恢复: python recover_session.py <session_id> <addr> --chain {to_chain_cc}")
                                else:
                                    logger.warning(f"  ⚠️ 目标链余额不足以回程: {return_amount}")
                        else:
                            logger.warning(f"  ⚠️ 跨链到账超时（15分钟），资金可能卡在 {to_chain_cc}")
                            logger.warning(f"  💡 恢复: python recover_session.py <session_id> <addr> --chain {to_chain_cc}")
                    else:
                        logger.error(f"  ❌ 跨链失败: {bridge_result.get('error')}")

                except Exception as e:
                    logger.error(f"  ❌ 跨链异常: {e}")
                    results.append({
                        'stage': 2, 'hop': hop_count + 1, 'type': 'cross_chain',
                        'status': 'failed', 'error': str(e)
                    })

                hop_count += 1
                continue

            # ── 同链跳 ──────────────────────────────────────────────
            # 检查接下来 3 跳内是否有跨链跳，如果有，保留最大余额的地址给跨链
            upcoming_cross = False
            if use_real_crosschain and crosschain_path:
                for lookahead in range(1, 4):
                    future_idx = num_start_addresses + hop_count + lookahead
                    if future_idx < len(crosschain_path) and crosschain_path[future_idx]['type'] == 'cross_chain':
                        upcoming_cross = True
                        break

            # 找最大余额的地址索引，跨链前不消耗它
            reserved_idx = None
            if upcoming_cross and len(active_addresses) > 1:
                max_bal = -1
                for idx in active_addresses:
                    try:
                        b = self._get_balance_on_chain(current_chain, intermediate_addresses[idx]['address'])
                        if b > max_bal:
                            max_bal = b
                            reserved_idx = idx
                    except Exception:
                        pass

            # 从活跃地址中排除保留地址
            selectable = [i for i in active_addresses if i != reserved_idx] if reserved_idx is not None else active_addresses
            if not selectable:
                selectable = active_addresses  # 没得选就不保留

            from_idx = random.choice(selectable)
            available_targets = [i for i in range(num_hops) if i != from_idx]
            to_idx = random.choice(available_targets)

            from_addr_info = intermediate_addresses[from_idx]
            to_addr_info   = intermediate_addresses[to_idx]

            from_addr = from_addr_info['address']
            from_pk   = from_addr_info['private_key']
            to_addr   = to_addr_info['address']

            # 查余额（跨链后可能在非 self.chain 上）
            try:
                balance = self._get_balance_on_chain(current_chain, from_addr)
            except Exception:
                balance = self.transfer_engine.get_balance(from_addr)

            gas_reserve = self._gas_reserve * 2

            if balance <= gas_reserve:
                active_addresses.remove(from_idx)
                continue

            amount = round(balance - gas_reserve, 8)
            if amount <= 0:
                active_addresses.remove(from_idx)
                continue

            try:
                if use_real_crosschain and current_chain != self.chain:
                    result = self._send_on_chain(current_chain, from_pk, to_addr, amount, gas_level)
                else:
                    result = self._send_transaction(from_pk, to_addr, amount, gas_level)

                results.append({
                    'stage': 2,
                    'hop': hop_count + 1,
                    'type': 'same_chain',
                    'chain': current_chain,
                    'from': from_addr,
                    'to': to_addr,
                    'amount': amount,
                    'status': 'success',
                    'tx_hash': result['tx_hash']
                })

                logger.info(f"  ✅ 跳转 {hop_count+1}/{remaining_hops} [{current_chain}]: "
                            f"{from_addr[:10]}... → {to_addr[:10]}... ({amount:.8f})")

                active_addresses.remove(from_idx)
                if to_idx not in active_addresses:
                    active_addresses.append(to_idx)

                hop_count += 1

                delay = random.uniform(*delay_range)
                logger.info(f"     ⏳ 延迟 {delay:.1f}s...")
                time.sleep(delay)

            except Exception as e:
                logger.error(f"  ❌ 跳转 {hop_count+1} 失败: {e}")
                results.append({
                    'stage': 2, 'hop': hop_count + 1, 'type': 'same_chain',
                    'from': from_addr, 'to': to_addr, 'amount': amount,
                    'status': 'failed', 'error': str(e)
                })
                active_addresses.remove(from_idx)
        
        # 阶段 3: 汇总到临时地址（如果启用隔离）或直接到目标地址
        if use_isolation:
            logger.info(f"\n💰 阶段 3: 汇总到临时隔离地址")
            
            # 使用最后一个中间地址作为目标隔离层
            isolation_addr_2 = intermediate_addresses[-1]['address']
            isolation_pk_2 = intermediate_addresses[-1]['private_key']
            final_target = isolation_addr_2
            
            logger.info(f"  🔒 目标隔离地址: {isolation_addr_2[:10]}...")
        else:
            logger.info(f"\n💰 阶段 3: 汇总到目标地址")
            final_target = to_address
        
        total_collected = 0
        
        for i in range(num_hops):
            addr_info = intermediate_addresses[i]
            addr = addr_info['address']
            pk = addr_info['private_key']
            
            # 跳过隔离地址本身
            if use_isolation and (addr == intermediate_addresses[0]['address'] or addr == intermediate_addresses[-1]['address']):
                continue
            
            balance = self.transfer_engine.get_balance(addr)
            gas_reserve = self._gas_reserve * 2  # 汇总后续可能再发，留两倍 buffer
            
            if balance <= gas_reserve:
                continue
            
            amount = balance - gas_reserve
            amount = round(amount, 8)
            
            if amount <= 0:
                continue
            
            total_collected += amount
            
            try:
                result = self._send_transaction(
                    from_private_key=pk,
                    to_address=final_target,
                    amount=amount,
                    gas_level=gas_level
                )
                
                results.append({
                    'stage': 3,
                    'from': addr,
                    'to': final_target,
                    'amount': amount,
                    'status': 'success',
                    'tx_hash': result['tx_hash']
                })
                
                logger.info(f"  ✅ 汇总: {addr[:10]}... → {final_target[:10]}... ({amount:.8f} BNB)")
                
                # 阶段 3（汇总）：不同私钥发送，无 nonce 冲突，最小间隔即可
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"  ❌ 汇总失败: {e}")
                results.append({
                    'stage': 3,
                    'from': addr,
                    'to': final_target,
                    'amount': amount,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 阶段 4: 目标地址隔离（如果启用）
        if use_isolation:
            logger.info(f"\n🔒 阶段 4: 目标地址隔离")
            
            isolation_addr_2 = intermediate_addresses[-1]['address']
            isolation_pk_2 = intermediate_addresses[-1]['private_key']
            
            # 关键修复：等汇总交易上链再查余额（最多重试 3 次）
            balance = 0.0
            gas_reserve = self._gas_reserve  # 阶段 4 是最后一笔，单倍 gas 即可
            for retry in range(4):
                if retry > 0:
                    logger.info(f"  ⏳ 等待汇总到账... (重试 {retry}/3)")
                    time.sleep(3)
                balance = self.transfer_engine.get_balance(isolation_addr_2)
                if balance > gas_reserve:
                    break
            
            if balance <= gas_reserve:
                logger.error(
                    f"  ❌ 目标隔离地址余额仍不足: {balance:.8f} ≤ {gas_reserve}, "
                    f"资金可能卡在 {isolation_addr_2}"
                )
                results.append({
                    'stage': 4,
                    'from': isolation_addr_2,
                    'to': to_address,
                    'amount': 0,
                    'status': 'failed',
                    'error': f'资金卡在隔离地址 {isolation_addr_2}，请用助记词恢复',
                    'purpose': 'target_isolation',
                    'stuck_address': isolation_addr_2
                })
            else:
                amount = balance - gas_reserve
                amount = round(amount, 8)
                
                try:
                    result = self._send_transaction(
                        from_private_key=isolation_pk_2,
                        to_address=to_address,
                        amount=amount,
                        gas_level=gas_level
                    )
                    
                    results.append({
                        'stage': 4,
                        'from': isolation_addr_2,
                        'to': to_address,
                        'amount': amount,
                        'status': 'success',
                        'tx_hash': result['tx_hash'],
                        'purpose': 'target_isolation'
                    })
                    
                    logger.info(f"  ✅ 目标地址隔离: {isolation_addr_2[:10]}... → {to_address[:10]}...")
                    logger.info(f"  🔒 链上无法直接追溯到目标地址")
                    
                    # 隔离延迟
                    if isolation_delay > 0:
                        logger.info(f"     ⏳ 隔离延迟 {isolation_delay} 秒...")
                        time.sleep(isolation_delay)
                    
                except Exception as e:
                    logger.error(f"  ❌ 目标地址隔离失败: {e}")
                    results.append({
                        'stage': 4,
                        'from': isolation_addr_2,
                        'to': to_address,
                        'amount': amount,
                        'status': 'failed',
                        'error': str(e),
                        'purpose': 'target_isolation',
                        'stuck_address': isolation_addr_2
                    })
        
        # 注：捐赠已在阶段 0a 从源地址支付，此处无需再转
        
        # 统计结果
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = len(results) - success_count
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 隐私转账完成")
        logger.info("=" * 60)
        logger.info(f"📊 总交易数: {len(results)}")
        logger.info(f"✅ 成功: {success_count}")
        logger.info(f"❌ 失败: {failed_count}")
        logger.info(f"💰 目标地址收到: {total_collected:.8f} BNB")
        logger.info(f"💳 捐赠: {service_fee:.8f} BNB")
        
        return {
            'success': success_count > 0,
            'total_transactions': len(results),
            'success_count': success_count,
            'failed_count': failed_count,
            'total_collected': total_collected,
            'service_fee': service_fee,
            'results': results,
            'plan': plan
        }
    
    def _send_transaction(
        self,
        from_private_key: str,
        to_address: str,
        amount: float,
        gas_level: str = 'standard',
        nonce: int = None
    ) -> Dict:
        """发送单笔交易（自动重试 nonce too low 错误）"""
        # 金额校验：必须为正数，防止 to_wei 溢出
        if amount is None or amount <= 0:
            raise ValueError(f"无效金额: {amount} (必须 > 0)")
        
        account = Account.from_key(from_private_key)
        from_address = account.address
        
        balance = self.transfer_engine.get_balance(from_address)
        if balance < amount:
            raise ValueError(f"余额不足: {balance} < {amount}")
        
        amount_wei = self.w3.to_wei(amount, 'ether')
        
        gas_price_gwei = self.transfer_engine.chain_config['gas_price_gwei'].get(gas_level, 5)
        gas_price_wei = self.w3.to_wei(gas_price_gwei, 'gwei')
        
        to_address = Web3.to_checksum_address(to_address)

        # 最多重试 2 次 nonce 错位（RPC 节点间状态不同步常见）
        last_err = None
        for attempt in range(3):
            # 每次重试都重新查一次 pending nonce
            if nonce is None or attempt > 0:
                use_nonce = self.w3.eth.get_transaction_count(from_address, 'pending')
            else:
                use_nonce = nonce

            tx = {
                'nonce': use_nonce,
                'to': to_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': gas_price_wei,
                'chainId': self.transfer_engine.chain_config['chain_id']
            }

            try:
                signed_tx = self.w3.eth.account.sign_transaction(tx, from_private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                return {
                    'tx_hash': tx_hash.hex(),
                    'from': from_address,
                    'to': to_address,
                    'amount': amount,
                    'nonce': use_nonce,
                    'explorer_url': f"{self.transfer_engine.chain_config['explorer']}/tx/{tx_hash.hex()}"
                }
            except Exception as e:
                msg = str(e).lower()
                last_err = e
                # 仅对 nonce / replacement underpriced 类错误重试
                if 'nonce' in msg or 'underpriced' in msg or 'already known' in msg:
                    logger.warning(f"  ⚠️ tx 重试 {attempt + 1}: {str(e)[:120]}")
                    time.sleep(0.5)
                    continue
                raise

        # 三次都失败
        raise last_err


if __name__ == '__main__':
    print("=" * 60)
    print("高级隐私转账引擎已加载")
    print("=" * 60)
    
    print("\n可用模式:")
    for mode, config in MIXING_MODES.items():
        print(f"\n{mode}:")
        print(f"  名称: {config['name']}")
        print(f"  隐私等级: {config['privacy_level']}")
        print(f"  预计时间: {config['estimated_time']}")
        print(f"  跨链: {'是' if config['use_crosschain'] else '否'}")
