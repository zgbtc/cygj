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
        执行跨链混币
        
        Args:
            plan: 混币计划
            from_private_key: 源地址私钥
            to_address: 目标地址
            mnemonic: 助记词
        
        Returns:
            执行结果
        """
        logger.info("=" * 60)
        logger.info("开始跨链混币")
        logger.info("=" * 60)
        
        account = Account.from_key(from_private_key)
        from_address = account.address
        
        logger.info(f"路径: {' → '.join(plan['route'])}")
        logger.info(f"总跳数: {plan['total_hops']}")
        logger.info(f"总金额: {plan['total_amount']}")
        
        results = []
        current_private_key = from_private_key
        current_amount = plan['total_amount']
        
        # 执行每一步
        for step in plan['steps']:
            chain = step['chain']
            hops = step['hops']
            
            logger.info(f"\n{'=' * 60}")
            logger.info(f"步骤 {step['step']}: 在 {chain} 上混币")
            logger.info(f"{'=' * 60}")
            
            # 1. 在当前链上混币
            mixer = MixerEngine(chain=chain, use_proxy=self.use_proxy)
            
            # 创建混币计划
            mix_plan = mixer.create_mixing_plan(
                from_private_key=current_private_key,
                to_address=to_address,  # 临时目标地址
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
                'result': mix_result
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
                    
                    # 执行跨链
                    bridge_result = self.bridge.execute_bridge(
                        from_chain=chain,
                        to_chain=next_chain,
                        from_private_key=current_private_key,
                        to_address=to_address,
                        amount=bridge_amount
                    )
                    
                    results.append({
                        'step': step['step'],
                        'chain': chain,
                        'action': 'bridge',
                        'to_chain': next_chain,
                        'result': bridge_result
                    })
                    
                    # 更新当前金额
                    if bridge_result['success']:
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
        
        return {
            'success': total_success > 0,
            'plan': plan,
            'results': results,
            'total_steps': len(results),
            'success_count': total_success,
            'failed_count': total_failed
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
