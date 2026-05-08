"""跨链混币引擎 - 实现多链混币流程"""
import logging
import time
import random
from typing import Dict, List
from web3 import Web3
from eth_account import Account
from lifi_bridge import get_lifi_bridge
from mixer_engine import MixerEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrossChainMixer:
    """跨链混币引擎"""
    
    def __init__(self, use_proxy: bool = True):
        """
        初始化跨链混币引擎
        
        Args:
            use_proxy: 是否使用代理池
        """
        self.use_proxy = use_proxy
        self.bridge = get_lifi_bridge(use_proxy=use_proxy)
        
        # 跨链路径配置
        self.crosschain_routes = [
            ['bsc', 'polygon', 'arbitrum', 'bsc'],  # 路径1: BSC → Polygon → Arbitrum → BSC
            ['polygon', 'bsc', 'optimism', 'polygon'],  # 路径2: Polygon → BSC → Optimism → Polygon
            ['arbitrum', 'polygon', 'bsc', 'arbitrum'],  # 路径3: Arbitrum → Polygon → BSC → Arbitrum
        ]
        
        logger.info("✅ 跨链混币引擎已初始化")
    
    def plan_crosschain_mixing(
        self,
        start_chain: str,
        num_hops: int,
        total_amount: float
    ) -> Dict:
        """
        规划跨链混币路径
        
        Args:
            start_chain: 起始链
            num_hops: 总跳数
            total_amount: 总金额
        
        Returns:
            混币计划
        """
        # 选择合适的跨链路径
        route = self._select_route(start_chain)
        
        # 计算每条链上的跳数
        num_chains = len(route)
        hops_per_chain = num_hops // num_chains
        
        # 分配金额（考虑跨链费用）
        crosschain_fee_per_hop = 0.002  # 每次跨链约0.002
        total_crosschain_fee = crosschain_fee_per_hop * (num_chains - 1)
        
        plan = {
            'route': route,
            'num_chains': num_chains,
            'hops_per_chain': hops_per_chain,
            'total_hops': num_hops,
            'total_amount': total_amount,
            'crosschain_fee': total_crosschain_fee,
            'steps': []
        }
        
        # 生成每一步的计划
        remaining_amount = total_amount
        
        for i, chain in enumerate(route):
            is_last = (i == len(route) - 1)
            
            step = {
                'step': i + 1,
                'chain': chain,
                'action': 'mix',
                'hops': hops_per_chain,
                'amount': remaining_amount
            }
            
            # 如果不是最后一步，添加跨链
            if not is_last:
                next_chain = route[i + 1]
                step['next_action'] = 'bridge'
                step['bridge_to'] = next_chain
                remaining_amount -= crosschain_fee_per_hop
            
            plan['steps'].append(step)
        
        return plan
    
    def _select_route(self, start_chain: str) -> List[str]:
        """选择跨链路径"""
        # 找到以start_chain开头的路径
        for route in self.crosschain_routes:
            if route[0] == start_chain:
                return route
        
        # 如果没有找到，使用默认路径
        return ['bsc', 'polygon', 'arbitrum', 'bsc']
    
    def execute_crosschain_mixing(
        self,
        plan: Dict,
        from_private_key: str,
        to_address: str,
        mnemonic: str = None
    ) -> Dict:
        """
        执行跨链混币 - 真正无法追溯版本
        
        关键改进：
        1. 每次跨链前，混币到新的临时地址
        2. 用临时地址的私钥执行跨链
        3. 到新链后，从临时地址继续混币
        4. 跨链桥只能看到：临时地址B → 临时地址C（无法关联源地址A）
        
        Args:
            plan: 混币计划
            from_private_key: 源地址私钥
            to_address: 目标地址
            mnemonic: 助记词（用于生成临时地址）
        
        Returns:
            执行结果
        """
        logger.info("=" * 60)
        logger.info("开始跨链混币（真正无法追溯）")
        logger.info("=" * 60)
        
        account = Account.from_key(from_private_key)
        from_address = account.address
        
        logger.info(f"路径: {' → '.join(plan['route'])}")
        logger.info(f"总跳数: {plan['total_hops']}")
        logger.info(f"总金额: {plan['total_amount']}")
        logger.info(f"🔒 隐私保护：每次跨链使用新的临时地址")
        
        results = []
        current_private_key = from_private_key
        current_amount = plan['total_amount']
        temp_addresses = []  # 记录使用的临时地址
        
        # 执行每一步
        for step_idx, step in enumerate(plan['steps']):
            chain = step['chain']
            hops = step['hops']
            is_last_step = (step_idx == len(plan['steps']) - 1)
            
            logger.info(f"\n{'=' * 60}")
            logger.info(f"步骤 {step['step']}: 在 {chain} 上混币")
            logger.info(f"{'=' * 60}")
            
            # 1. 在当前链上混币
            mixer = MixerEngine(chain=chain, use_proxy=self.use_proxy)
            
            # 决定混币的目标地址
            if is_last_step:
                # 最后一步：混币到用户指定的目标地址
                mix_target = to_address
                logger.info(f"✅ 最后一步：混币到目标地址 {to_address[:10]}...")
            else:
                # 中间步骤：混币到新的临时地址（用于跨链）
                # 使用HD钱包生成临时地址
                if mnemonic:
                    from hd_wallet import HDWallet
                    hd = HDWallet(mnemonic)
                    # 使用不同的索引生成不同的临时地址
                    temp_account = hd.get_account(step_idx + 100)  # 从索引100开始
                    mix_target = temp_account['address']
                    temp_private_key = temp_account['private_key']
                else:
                    # 如果没有助记词，随机生成临时账户
                    temp_account = Account.create()
                    mix_target = temp_account.address
                    temp_private_key = temp_account.key.hex()
                
                temp_addresses.append({
                    'chain': chain,
                    'address': mix_target,
                    'purpose': 'bridge_source'
                })
                logger.info(f"🔑 生成临时地址：{mix_target[:10]}... (用于跨链)")
            
            # 创建混币计划
            mix_plan = mixer.create_mixing_plan(
                from_private_key=current_private_key,
                to_address=mix_target,
                total_amount=current_amount,
                num_hops=hops,
                mnemonic=mnemonic
            )
            
            # 执行混币
            mix_result = mixer.execute_mixing(
                plan=mix_plan,
                gas_level='standard',
                delay_range=(1, 3)
            )
            
            results.append({
                'step': step['step'],
                'chain': chain,
                'action': 'mix',
                'result': mix_result,
                'temp_address': mix_target if not is_last_step else None
            })
            
            # 2. 如果需要跨链
            if 'next_action' in step and step['next_action'] == 'bridge':
                next_chain = step['bridge_to']
                
                logger.info(f"\n{'=' * 60}")
                logger.info(f"跨链: {chain} → {next_chain}")
                logger.info(f"{'=' * 60}")
                
                # 获取混币后的余额
                if mix_result['success']:
                    bridge_amount = mix_result['total_collected']
                    
                    # 生成下一条链的临时接收地址
                    if mnemonic:
                        from hd_wallet import HDWallet
                        hd = HDWallet(mnemonic)
                        next_temp_account = hd.get_account(step_idx + 200)  # 从索引200开始
                        bridge_to_address = next_temp_account['address']
                        next_private_key = next_temp_account['private_key']
                    else:
                        next_temp_account = Account.create()
                        bridge_to_address = next_temp_account.address
                        next_private_key = next_temp_account.key.hex()
                    
                    temp_addresses.append({
                        'chain': next_chain,
                        'address': bridge_to_address,
                        'purpose': 'bridge_destination'
                    })
                    
                    logger.info(f"🔑 跨链源地址：{mix_target[:10]}...")
                    logger.info(f"🔑 跨链目标地址：{bridge_to_address[:10]}...")
                    logger.info(f"🔒 跨链桥只能看到：{mix_target[:10]}... → {bridge_to_address[:10]}...")
                    logger.info(f"🔒 无法关联到源地址：{from_address[:10]}...")
                    
                    # 使用临时地址的私钥执行跨链
                    bridge_result = self.bridge.execute_bridge(
                        from_chain=chain,
                        to_chain=next_chain,
                        from_private_key=temp_private_key,  # 使用临时地址私钥
                        to_address=bridge_to_address,  # 跨链到新的临时地址
                        amount=bridge_amount
                    )
                    
                    results.append({
                        'step': step['step'],
                        'chain': chain,
                        'action': 'bridge',
                        'to_chain': next_chain,
                        'result': bridge_result,
                        'bridge_from': mix_target,
                        'bridge_to': bridge_to_address
                    })
                    
                    # 更新当前私钥和金额（下一步从新的临时地址开始）
                    if bridge_result['success']:
                        current_private_key = next_private_key
                        current_amount = bridge_amount - 0.002  # 扣除跨链费
                    
                    # 等待跨链完成
                    logger.info("⏳ 等待跨链完成...")
                    time.sleep(60)  # 等待1分钟
        
        # 统计结果
        total_success = sum(1 for r in results if r['result'].get('success', False))
        total_failed = len(results) - total_success
        
        logger.info("\n" + "=" * 60)
        logger.info("跨链混币完成")
        logger.info("=" * 60)
        logger.info(f"总步骤: {len(results)}")
        logger.info(f"成功: {total_success}")
        logger.info(f"失败: {total_failed}")
        logger.info(f"🔒 使用了 {len(temp_addresses)} 个临时地址")
        logger.info(f"🔒 隐私保护：跨链桥无法追溯到源地址")
        
        return {
            'success': total_success > 0,
            'plan': plan,
            'results': results,
            'total_steps': len(results),
            'success_count': total_success,
            'failed_count': total_failed,
            'temp_addresses': temp_addresses,
            'privacy_level': 'maximum'
        }


if __name__ == '__main__':
    # 测试
    print("=" * 60)
    print("跨链混币引擎测试")
    print("=" * 60)
    
    mixer = CrossChainMixer(use_proxy=False)
    
    # 生成混币计划
    plan = mixer.plan_crosschain_mixing(
        start_chain='bsc',
        num_hops=100,
        total_amount=0.1
    )
    
    print(f"\n混币计划:")
    print(f"  路径: {' → '.join(plan['route'])}")
    print(f"  总跳数: {plan['total_hops']}")
    print(f"  每链跳数: {plan['hops_per_chain']}")
    print(f"  跨链费用: {plan['crosschain_fee']} BNB")
    
    print(f"\n详细步骤:")
    for step in plan['steps']:
        print(f"  步骤 {step['step']}: {step['chain']} 混币 {step['hops']} 跳")
        if 'bridge_to' in step:
            print(f"           → 跨链到 {step['bridge_to']}")
