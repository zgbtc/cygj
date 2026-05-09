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
        mnemonic: str = None
    ) -> Dict:
        """创建隐私转账计划"""
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
        
        # 生成中间地址
        wallet = HDWallet(mnemonic)
        intermediate_addresses = wallet.generate_addresses(num_hops)
        
        # 生成跨链路径（如果启用）
        crosschain_path = None
        if self.mode_config['use_crosschain'] and self.bridge:
            crosschain_path = self.bridge.multi_chain_mixing_path(self.chain, num_hops)
        
        plan = {
            'from_address': from_address,
            'from_private_key': from_private_key,
            'to_address': to_address,
            'mnemonic': wallet.mnemonic,
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
        
        # 阶段 0: 源地址隔离（如果启用）
        if use_isolation:
            logger.info(f"\n🔒 阶段 0: 源地址隔离")
            
            # 使用第一个中间地址作为隔离层
            isolation_addr_1 = intermediate_addresses[0]['address']
            isolation_pk_1 = intermediate_addresses[0]['private_key']
            
            try:
                result = self._send_transaction(
                    from_private_key=from_private_key,
                    to_address=isolation_addr_1,
                    amount=fees['net_amount'],
                    gas_level=gas_level
                )
                
                results.append({
                    'stage': 0,
                    'from': from_address,
                    'to': isolation_addr_1,
                    'amount': fees['net_amount'],
                    'status': 'success',
                    'tx_hash': result['tx_hash'],
                    'purpose': 'source_isolation'
                })
                
                logger.info(f"  ✅ 源地址隔离: {from_address[:10]}... → {isolation_addr_1[:10]}...")
                logger.info(f"  🔒 链上无法直接追溯到源地址")
                
                # 关键：等待资金真正到账再进入阶段 1（否则读到的余额为 0）
                logger.info(f"  ⏳ 等待资金到账...")
                try:
                    receipt = self.w3.eth.wait_for_transaction_receipt(
                        result['tx_hash'], timeout=30
                    )
                    if receipt['status'] != 1:
                        raise Exception("源地址隔离交易上链但失败")
                    logger.info(f"  ✅ 资金已到账 (区块 {receipt['blockNumber']})")
                except Exception as wait_err:
                    logger.warning(f"  ⚠️ 等待超时，降级到原地址: {wait_err}")
                    # 降级：不做源地址隔离
                    pass
                
                # 隔离延迟
                if isolation_delay > 0:
                    logger.info(f"     ⏳ 隔离延迟 {isolation_delay} 秒...")
                    time.sleep(isolation_delay)
                
                # 更新起始私钥和地址
                from_private_key = isolation_pk_1
                from_address = isolation_addr_1
                
            except Exception as e:
                logger.error(f"  ❌ 源地址隔离失败: {e}")
                results.append({
                    'stage': 0,
                    'from': from_address,
                    'to': isolation_addr_1,
                    'amount': fees['net_amount'],
                    'status': 'failed',
                    'error': str(e),
                    'purpose': 'source_isolation'
                })
                # 如果隔离失败，继续使用原地址
        
        # 阶段 1: 分散到多个起始地址
        start_offset = 1 if use_isolation else 0  # 如果用了隔离，从第2个地址开始
        num_start_addresses = max(5, num_hops // 5)
        logger.info(f"\n🌱 阶段 1: 分散到 {num_start_addresses} 个起始地址")
        
        # 使用随机金额分配 —— 为每笔交易预留 gas（不只为 1 笔）
        current_balance = self.transfer_engine.get_balance(from_address)
        gas_reserve_per_tx = 0.0003
        # 为分散阶段所有交易预留 gas
        total_gas_reserve = gas_reserve_per_tx * (num_start_addresses + 2)
        available_amount = current_balance - total_gas_reserve

        # 防御：余额不足时跳过阶段 1，直接用当前地址作为起点进入阶段 2
        if available_amount <= 0:
            logger.warning(
                f"⚠️ 阶段 1 跳过：余额 {current_balance:.8f} 不足以分散 "
                f"({num_start_addresses} 笔 × gas)"
            )
            num_start_addresses = 0
            start_amounts = []
        else:
            start_amounts = self.generate_random_amounts(
                available_amount,
                num_start_addresses,
                use_round_numbers=True
            )
        
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
        
        # 阶段 2: 中间地址随机交叉跳转
        logger.info(f"\n🔀 阶段 2: 中间地址随机交叉跳转")
        
        remaining_hops = num_hops - num_start_addresses
        active_addresses = list(range(num_start_addresses))
        hop_count = 0
        
        while hop_count < remaining_hops and active_addresses:
            from_idx = random.choice(active_addresses)
            available_targets = [i for i in range(num_hops) if i != from_idx]
            to_idx = random.choice(available_targets)
            
            from_addr_info = intermediate_addresses[from_idx]
            to_addr_info = intermediate_addresses[to_idx]
            
            from_addr = from_addr_info['address']
            from_pk = from_addr_info['private_key']
            to_addr = to_addr_info['address']
            
            balance = self.transfer_engine.get_balance(from_addr)
            gas_reserve = 0.0003
            
            if balance <= gas_reserve:
                active_addresses.remove(from_idx)
                continue
            
            amount = balance - gas_reserve
            amount = round(amount, 8)
            
            if amount <= 0:
                active_addresses.remove(from_idx)
                continue
            
            try:
                result = self._send_transaction(
                    from_private_key=from_pk,
                    to_address=to_addr,
                    amount=amount,
                    gas_level=gas_level
                )
                
                results.append({
                    'stage': 2,
                    'hop': hop_count + 1,
                    'from': from_addr,
                    'to': to_addr,
                    'amount': amount,
                    'status': 'success',
                    'tx_hash': result['tx_hash']
                })
                
                logger.info(f"  ✅ 跳转 {hop_count + 1}/{remaining_hops}: {from_addr[:10]}... → {to_addr[:10]}... ({amount:.8f} BNB)")
                
                active_addresses.remove(from_idx)
                if to_idx not in active_addresses:
                    active_addresses.append(to_idx)
                
                hop_count += 1
                
                # 随机延迟
                delay = random.uniform(*delay_range)
                logger.info(f"     ⏳ 延迟 {delay:.1f} 秒...")
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"  ❌ 跳转 {hop_count + 1} 失败: {e}")
                results.append({
                    'stage': 2,
                    'hop': hop_count + 1,
                    'from': from_addr,
                    'to': to_addr,
                    'amount': amount,
                    'status': 'failed',
                    'error': str(e)
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
            gas_reserve = 0.0003
            
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
            
            # 获取隔离地址的余额
            balance = self.transfer_engine.get_balance(isolation_addr_2)
            gas_reserve = 0.0003
            
            if balance > gas_reserve:
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
                        'purpose': 'target_isolation'
                    })
        
        # 阶段 5: 转捐赠
        logger.info("\n💳 阶段 5: 转捐赠")
        
        service_fee = fees['service_fee']
        fee_address = FEE_CONFIG['fee_address']
        
        try:
            result = self._send_transaction(
                from_private_key=from_private_key,
                to_address=fee_address,
                amount=service_fee,
                gas_level=gas_level
            )
            
            logger.info(f"  ✅ 捐赠: {service_fee:.8f} BNB → {fee_address[:10]}...")
            
        except Exception as e:
            logger.error(f"  ❌ 捐赠转账失败: {e}")
        
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
        """发送单笔交易"""
        # 金额校验：必须为正数，防止 to_wei 溢出
        if amount is None or amount <= 0:
            raise ValueError(f"无效金额: {amount} (必须 > 0)")
        
        account = Account.from_key(from_private_key)
        from_address = account.address
        
        balance = self.transfer_engine.get_balance(from_address)
        if balance < amount:
            raise ValueError(f"余额不足: {balance} < {amount}")
        
        amount_wei = self.w3.to_wei(amount, 'ether')
        
        if nonce is None:
            # 使用 pending 避免快速连发时 nonce 冲突
            nonce = self.w3.eth.get_transaction_count(from_address, 'pending')
        
        gas_price_gwei = self.transfer_engine.chain_config['gas_price_gwei'].get(gas_level, 5)
        gas_price_wei = self.w3.to_wei(gas_price_gwei, 'gwei')
        
        to_address = Web3.to_checksum_address(to_address)
        
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': gas_price_wei,
            'chainId': self.transfer_engine.chain_config['chain_id']
        }
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, from_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return {
            'tx_hash': tx_hash.hex(),
            'from': from_address,
            'to': to_address,
            'amount': amount,
            'nonce': nonce,
            'explorer_url': f"{self.transfer_engine.chain_config['explorer']}/tx/{tx_hash.hex()}"
        }


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
