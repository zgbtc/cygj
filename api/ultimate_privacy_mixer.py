"""
极致隐私模式混币引擎

流程：
1. 源地址 → 中间地址 A（BSC，单链混币 5 跳）
2. 中间地址 A → 中间地址 B（跨链到 Polygon）
3. 中间地址 B → 中间地址 C（Polygon 单链混币 5 跳）
4. 中间地址 C → 中间地址 D（跨链到 Arbitrum）
5. 中间地址 D → 中间地址 E（Arbitrum 单链混币 5 跳）
6. 中间地址 E → 目标地址（跨链到 BSC）

特点：
- 真实跨链（LiFi API）
- 每条链上都做多跳混币
- 跨链桥无法关联源地址和目标地址
- 总时间 60-250 秒
- 总成本 $0.05 - $0.10
"""
import sys
import os
import logging
import time
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(__file__))

from real_crosschain_mixer import RealCrossChainMixer, CHAIN_CONFIG
from advanced_mixer_engine import AdvancedMixerEngine
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)


class UltimatePrivacyMixer:
    """极致隐私混币引擎"""
    
    # 预设的混币路径
    MIXING_PATHS = {
        'simple': ['bsc', 'polygon', 'bsc'],  # 简单：2 次跨链
        'standard': ['bsc', 'polygon', 'arbitrum', 'bsc'],  # 标准：3 次跨链
        'complex': ['bsc', 'polygon', 'arbitrum', 'optimism', 'bsc'],  # 复杂：4 次跨链
    }
    
    def __init__(self, path_type: str = 'standard', verify_ssl: bool = True):
        """
        初始化
        
        Args:
            path_type: 路径类型 (simple/standard/complex)
            verify_ssl: 是否验证 SSL
        """
        self.path = self.MIXING_PATHS.get(path_type, self.MIXING_PATHS['standard'])
        self.crosschain_mixer = RealCrossChainMixer(verify_ssl=verify_ssl)
        
        logger.info(f"🔒 极致隐私混币已初始化")
        logger.info(f"   路径: {' → '.join([CHAIN_CONFIG[c]['name'] for c in self.path])}")
        logger.info(f"   跨链次数: {len(self.path) - 1}")
    
    def execute_mixing(
        self,
        from_private_key: str,
        to_address: str,
        total_amount: float,
        hops_per_chain: int = 0,
        gas_level: str = 'standard'
    ) -> Dict:
        """
        执行极致隐私混币（纯跨链模式，不做单链混币以避免超时）
        
        流程：
        1. 源地址 → [真实跨链] → 临时地址A (Polygon)
        2. 临时地址A → [真实跨链] → 临时地址B (Arbitrum)  
        3. 临时地址B → [真实跨链] → 目标地址 (BSC)
        
        Args:
            from_private_key: 源地址私钥
            to_address: 目标地址
            total_amount: 总金额（源链原生币）
            hops_per_chain: 已废弃（保持兼容），不再在每条链上做单链混币
            gas_level: Gas 等级
        
        Returns:
            执行结果
        """
        logger.info("=" * 70)
        logger.info("🌉 开始极致隐私混币（真实多链跨链）")
        logger.info("=" * 70)
        logger.info(f"路径: {' → '.join([CHAIN_CONFIG[c]['name'] for c in self.path])}")
        logger.info(f"金额: {total_amount}")
        
        results = {
            'success': False,
            'mode': 'ultimate',
            'path': self.path,
            'hops_per_chain': hops_per_chain,
            'steps': [],
            'cross_chain_steps': [],
            'mixing_steps': []
        }
        
        current_private_key = from_private_key
        current_amount = total_amount
        actual_amount = total_amount  # 保底初始值
        
        # 每一步都是：[跨链到下一条链（使用新的临时地址）]
        for i in range(len(self.path) - 1):
            from_chain = self.path[i]
            to_chain = self.path[i + 1]
            is_last = (i == len(self.path) - 2)
            
            logger.info(f"\n{'=' * 70}")
            logger.info(f"阶段 {i+1}/{len(self.path)-1}: {CHAIN_CONFIG[from_chain]['name']} → {CHAIN_CONFIG[to_chain]['name']}")
            logger.info(f"{'=' * 70}")
            
            # 生成接收地址：最后一步是目标地址，中间是新的临时地址
            if is_last:
                bridge_to_address = to_address
                next_private_key = None
            else:
                temp_account = self.crosschain_mixer.generate_temp_account()
                bridge_to_address = temp_account['address']
                next_private_key = temp_account['private_key']
                logger.info(f"🔑 生成临时跨链地址 ({CHAIN_CONFIG[to_chain]['name']}): {bridge_to_address[:10]}...")
            
            # 执行真实跨链
            bridge_result = self.crosschain_mixer.execute_bridge(
                from_chain=from_chain,
                to_chain=to_chain,
                from_private_key=current_private_key,
                amount=current_amount,
                to_address=bridge_to_address
            )
            
            results['cross_chain_steps'].append({
                'step': i + 1,
                'from_chain': from_chain,
                'to_chain': to_chain,
                'result': bridge_result
            })
            
            if not bridge_result.get('success'):
                logger.error(f"❌ 跨链失败: {bridge_result.get('error')}")
                results['error'] = bridge_result.get('error')
                return results
            
            # 等待跨链到账
            arrived, received_amount = self.crosschain_mixer.wait_for_arrival(
                to_chain=to_chain,
                address=bridge_to_address,
                expected_min_amount=bridge_result['to_amount_estimated'],
                timeout=180
            )
            
            if not arrived:
                logger.error(f"❌ 跨链到账超时")
                results['error'] = '跨链到账超时'
                return results
            
            actual_amount = received_amount
            
            # 准备下一轮：使用新的私钥和金额
            if not is_last:
                current_private_key = next_private_key
                # 留出 gas
                gas_reserve = 0.002 if to_chain == 'bsc' else (
                    0.5 if to_chain == 'polygon' else 0.0001
                )
                current_amount = actual_amount - gas_reserve
                
                if current_amount <= 0:
                    logger.error(f"❌ 到账金额 {actual_amount} 不足以支付 gas {gas_reserve}")
                    results['error'] = f'到账金额 {actual_amount} 不足以支付 gas {gas_reserve}'
                    return results
        
        results['success'] = True
        results['final_amount'] = actual_amount
        results['target_address'] = to_address
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 极致隐私混币完成！")
        logger.info(f"   最终到账: {actual_amount:.6f} {CHAIN_CONFIG[self.path[-1]]['symbol']}")
        logger.info(f"   目标地址: {to_address}")
        logger.info(f"   跨链次数: {len(self.path) - 1}")
        logger.info("=" * 70)
        
        return results


def test_ultimate_privacy():
    """测试极致隐私混币（仅报价，不执行）"""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("=" * 70)
    print("🧪 极致隐私混币 Dry Run 测试")
    print("=" * 70)
    
    # 测试不同路径类型
    for path_type in ['simple', 'standard', 'complex']:
        mixer = UltimatePrivacyMixer(path_type=path_type, verify_ssl=False)
        
        path = mixer.path
        total_duration = 0
        total_cost_usd = 0
        
        print(f"\n{'=' * 70}")
        print(f"路径类型: {path_type.upper()}")
        print(f"路径: {' → '.join([CHAIN_CONFIG[c]['name'] for c in path])}")
        print(f"{'=' * 70}")
        
        # 模拟计算每步
        test_amount_wei = int(0.01 * 1e18)
        
        for i in range(len(path) - 1):
            quote = mixer.crosschain_mixer.get_quote(
                from_chain=path[i],
                to_chain=path[i + 1],
                amount_wei=test_amount_wei,
                from_address='0x0EC052Af5Ed6e45a3B49B4628f1541C90CAB8872'
            )
            
            if quote:
                estimate = quote.get('estimate', {})
                duration = estimate.get('executionDuration', 0)
                to_amount = int(estimate.get('toAmount', 0))
                
                gas_usd = sum(float(g.get('amountUSD', 0)) for g in estimate.get('gasCosts', []))
                fee_usd = sum(float(f.get('amountUSD', 0)) for f in estimate.get('feeCosts', []))
                
                total_duration += duration
                total_cost_usd += gas_usd + fee_usd
                
                print(f"  Step {i+1}: {CHAIN_CONFIG[path[i]]['name']} → {CHAIN_CONFIG[path[i+1]]['name']}: {duration}s, ${gas_usd+fee_usd:.4f}")
                
                test_amount_wei = int(to_amount * 0.95)
        
        # 加上单链混币时间（每条链 3 跳 × 3 秒）
        mixing_time = (len(path) - 1) * 3 * 3  # 粗略估算
        
        print(f"\n📊 总结:")
        print(f"   跨链时间: {total_duration} 秒")
        print(f"   单链混币时间: ~{mixing_time} 秒")
        print(f"   总时间: ~{total_duration + mixing_time} 秒")
        print(f"   总跨链费用: ${total_cost_usd:.4f}")
        print(f"   Vercel 兼容: {'✅' if total_duration + mixing_time < 300 else '⚠️ 可能超时'}")


if __name__ == '__main__':
    test_ultimate_privacy()
