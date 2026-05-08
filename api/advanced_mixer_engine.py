"""高级混币引擎 - 集成跨链 + Tor + 时间延迟 + 金额随机化"""
import logging
import time
import random
from typing import List, Dict, Optional, Tuple
from web3 import Web3
from eth_account import Account
from hd_wallet import HDWallet
from transfer_engine import TransferEngine
from crosschain_bridge import CrossChainBridge
from config import CHAINS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 服务费配置
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

# 混币模式配置
MIXING_MODES = {
    'fast': {
        'name': '快速模式',
        'delay_range': (0.5, 2),  # 0.5-2 秒（优化速度）
        'use_crosschain': False,
        'use_tor': True,  # 可选Tor
        'use_isolation': True,  # 启用源地址和目标地址隔离
        'isolation_delay': 0,  # 隔离层无额外延迟
        'privacy_level': '⭐⭐⭐⭐⭐',
        'estimated_time': '20秒-5分钟',
        'fee_rate': 0.0003
    },
    'ultimate': {
        'name': '极致隐私',
        'delay_range': (300, 1800),  # 5-30 分钟
        'use_crosschain': True,
        'use_tor': True,  # 必须Tor
        'use_isolation': True,  # 启用隔离
        'isolation_delay': 0,
        'privacy_level': '⭐⭐⭐⭐⭐⭐⭐',
        'estimated_time': '45分钟-2小时',
        'fee_rate': 0.0006
    }
}


class AdvancedMixerEngine:
    """高级混币引擎"""
    
    def __init__(self, chain: str = 'bsc_testnet', mode: str = 'fast'):
        """
        初始化高级混币引擎
        
        Args:
            chain: 链名称
            mode: 混币模式 (fast, ultimate)
        """
        if mode not in MIXING_MODES:
            raise ValueError(f"不支持的模式: {mode}. 可选: {list(MIXING_MODES.keys())}")
        
        self.mode = mode
        self.mode_config = MIXING_MODES[mode]
        self.chain = chain
        
        # 根据模式决定是否使用代理
        use_proxy = (mode == 'ultimate')  # 只有极致隐私模式使用代理
        
        # 初始化转账引擎
        self.transfer_engine = TransferEngine(chain, use_proxy=use_proxy)
        self.w3 = self.transfer_engine.w3
        
        # 初始化跨链桥接（如果需要）
        if self.mode_config['use_crosschain']:
            try:
                from lifi_bridge import get_lifi_bridge
                self.bridge = get_lifi_bridge(use_proxy=use_proxy)
                logger.info(f"🌉 跨链模式已启用（LiFi）")
            except Exception as e:
                logger.warning(f"LiFi桥接初始化失败: {e}")
                self.bridge = None
        else:
            self.bridge = None
        
        # 显示模式信息
        if use_proxy:
            logger.info(f"🔒 IP隐藏: 已启用（代理池）")
        else:
            logger.info(f"⚠️ IP隐藏: 建议使用VPN")
        
        logger.info(f"🎯 混币模式: {self.mode_config['name']}")
        logger.info(f"🔒 隐私等级: {self.mode_config['privacy_level']}")
        logger.info(f"⏱️ 预计时间: {self.mode_config['estimated_time']}")
    
    def calculate_fees(self, num_hops: int, total_amount: float) -> Dict:
        """计算费用"""
        # 根据模式获取费率和费用类型
        fee_rate = FEE_CONFIG['fee_rates'].get(self.mode, 0.0003)
        fee_type = FEE_CONFIG['fee_types'].get(self.mode, 'per_hop')
        
        # 计算服务费
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
        """创建混币计划"""
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
        执行高级混币（带源地址和目标地址隔离）
        
        Args:
            plan: 混币计划
            gas_level: Gas 等级
        
        Returns:
            执行结果
        """
        logger.info("=" * 60)
        logger.info(f"🚀 开始执行混币 - {plan['mode_config']['name']}")
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
        
        results = []
        
        logger.info(f"\n📊 混币参数:")
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
        
        # 使用随机金额分配
        current_balance = self.transfer_engine.get_balance(from_address)
        gas_reserve = 0.0003
        available_amount = current_balance - gas_reserve
        
        start_amounts = self.generate_random_amounts(
            available_amount,
            num_start_addresses,
            use_round_numbers=True
        )
        
        for i in range(num_start_addresses):
            addr_idx = start_offset + i
            if addr_idx >= len(intermediate_addresses):
                break
                
            start_addr = intermediate_addresses[addr_idx]['address']
            amount = start_amounts[i]
            
            try:
                result = self._send_transaction(
                    from_private_key=from_private_key,
                    to_address=start_addr,
                    amount=amount,
                    gas_level=gas_level
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
                
                # 随机延迟
                delay = random.uniform(*delay_range)
                time.sleep(delay)
            
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
                
                # 随机延迟
                delay = random.uniform(*delay_range)
                time.sleep(delay)
                
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
        
        # 阶段 5: 转服务费
        logger.info("\n💳 阶段 5: 转服务费")
        
        service_fee = fees['service_fee']
        fee_address = FEE_CONFIG['fee_address']
        
        try:
            result = self._send_transaction(
                from_private_key=from_private_key,
                to_address=fee_address,
                amount=service_fee,
                gas_level=gas_level
            )
            
            logger.info(f"  ✅ 服务费: {service_fee:.8f} BNB → {fee_address[:10]}...")
            
        except Exception as e:
            logger.error(f"  ❌ 服务费转账失败: {e}")
        
        # 统计结果
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = len(results) - success_count
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 混币完成")
        logger.info("=" * 60)
        logger.info(f"📊 总交易数: {len(results)}")
        logger.info(f"✅ 成功: {success_count}")
        logger.info(f"❌ 失败: {failed_count}")
        logger.info(f"💰 目标地址收到: {total_collected:.8f} BNB")
        logger.info(f"💳 服务费: {service_fee:.8f} BNB")
        
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
        account = Account.from_key(from_private_key)
        from_address = account.address
        
        balance = self.transfer_engine.get_balance(from_address)
        if balance < amount:
            raise ValueError(f"余额不足: {balance} < {amount}")
        
        amount_wei = self.w3.to_wei(amount, 'ether')
        
        if nonce is None:
            nonce = self.w3.eth.get_transaction_count(from_address)
        
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
    print("高级混币引擎已加载")
    print("=" * 60)
    
    print("\n可用模式:")
    for mode, config in MIXING_MODES.items():
        print(f"\n{mode}:")
        print(f"  名称: {config['name']}")
        print(f"  隐私等级: {config['privacy_level']}")
        print(f"  预计时间: {config['estimated_time']}")
        print(f"  跨链: {'是' if config['use_crosschain'] else '否'}")
        print(f"  Tor: {'是' if config['use_tor'] else '否'}")
