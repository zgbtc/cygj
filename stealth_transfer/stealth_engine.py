"""隐私转账引擎 - 分散资金到多个地址"""
import logging
from typing import List, Dict, Optional
from transfer_engine import TransferEngine
from hd_wallet import HDWallet
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StealthTransferEngine:
    """隐私转账引擎"""
    
    def __init__(self, chain: str = 'bsc'):
        self.transfer_engine = TransferEngine(chain)
        self.chain = chain
    
    def create_stealth_transfer_plan(
        self,
        total_amount: float,
        num_addresses: int,
        mnemonic: str = None,
        distribution: str = 'random'
    ) -> Dict:
        """
        创建隐私转账计划
        
        Args:
            total_amount: 总转账金额
            num_addresses: 目标地址数量 (10-10000)
            mnemonic: 助记词（可选，不提供则自动生成）
            distribution: 分配方式 ('equal' 平均分配, 'random' 随机分配)
        
        Returns:
            转账计划
        """
        if num_addresses < 10:
            raise ValueError("地址数量不能少于 10 个")
        if num_addresses > 10000:
            raise ValueError("地址数量不能超过 10000 个")
        
        # 生成地址
        wallet = HDWallet(mnemonic)
        addresses = wallet.generate_addresses(num_addresses)
        
        # 分配金额
        amounts = self._distribute_amount(total_amount, num_addresses, distribution)
        
        # 创建接收者列表
        recipients = []
        for i, addr in enumerate(addresses):
            recipients.append({
                'index': addr['index'],
                'address': addr['address'],
                'private_key': addr['private_key'],
                'amount': amounts[i],
                'path': addr['path']
            })
        
        return {
            'mnemonic': wallet.mnemonic,
            'total_amount': total_amount,
            'num_addresses': num_addresses,
            'distribution': distribution,
            'recipients': recipients,
            'chain': self.chain
        }
    
    def _distribute_amount(
        self,
        total_amount: float,
        num_addresses: int,
        distribution: str
    ) -> List[float]:
        """
        分配金额到各个地址
        
        Args:
            total_amount: 总金额
            num_addresses: 地址数量
            distribution: 分配方式
        
        Returns:
            金额列表
        """
        if distribution == 'equal':
            # 平均分配
            amount_per_address = total_amount / num_addresses
            return [round(amount_per_address, 8)] * num_addresses
        
        elif distribution == 'random':
            # 随机分配（更隐私）
            amounts = []
            remaining = total_amount
            
            for i in range(num_addresses - 1):
                # 随机分配 0.5% - 2% 的剩余金额
                min_ratio = 0.005
                max_ratio = 0.02
                ratio = random.uniform(min_ratio, max_ratio)
                amount = remaining * ratio
                amount = round(amount, 8)
                amounts.append(amount)
                remaining -= amount
            
            # 最后一个地址获得剩余金额
            amounts.append(round(remaining, 8))
            
            # 打乱顺序，增加隐私性
            random.shuffle(amounts)
            return amounts
        
        else:
            raise ValueError(f"不支持的分配方式: {distribution}")
    
    def execute_stealth_transfer(
        self,
        from_private_key: str,
        plan: Dict,
        gas_level: str = 'standard'
    ) -> Dict:
        """
        执行隐私转账
        
        Args:
            from_private_key: 源地址私钥
            plan: 转账计划（由 create_stealth_transfer_plan 生成）
            gas_level: Gas 等级
        
        Returns:
            执行结果
        """
        recipients = [
            {'address': r['address'], 'amount': r['amount']}
            for r in plan['recipients']
        ]
        
        logger.info(f"开始隐私转账: {len(recipients)} 个地址")
        
        # 执行批量转账
        results = self.transfer_engine.send_batch_transfers(
            private_key=from_private_key,
            recipients=recipients,
            gas_price_level=gas_level
        )
        
        # 统计结果
        success_count = sum(1 for r in results if r['status'] == 'pending')
        failed_count = len(results) - success_count
        
        return {
            'success': success_count > 0,
            'total': len(results),
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results,
            'mnemonic': plan['mnemonic'],
            'chain': self.chain
        }
    
    def estimate_stealth_transfer_cost(
        self,
        num_addresses: int,
        gas_level: str = 'standard'
    ) -> Dict:
        """估算隐私转账费用"""
        return self.transfer_engine.estimate_gas_cost(num_addresses, gas_level)


def quick_stealth_transfer(
    from_private_key: str,
    total_amount: float,
    num_addresses: int,
    chain: str = 'bsc',
    distribution: str = 'random',
    gas_level: str = 'standard'
) -> Dict:
    """
    快速隐私转账
    
    Args:
        from_private_key: 源地址私钥
        total_amount: 总金额
        num_addresses: 目标地址数量
        chain: 链
        distribution: 分配方式
        gas_level: Gas 等级
    
    Returns:
        执行结果（包含助记词）
    """
    engine = StealthTransferEngine(chain)
    
    # 创建计划
    plan = engine.create_stealth_transfer_plan(
        total_amount=total_amount,
        num_addresses=num_addresses,
        distribution=distribution
    )
    
    # 执行转账
    result = engine.execute_stealth_transfer(
        from_private_key=from_private_key,
        plan=plan,
        gas_level=gas_level
    )
    
    return result


if __name__ == '__main__':
    # 测试
    print("=" * 60)
    print("隐私转账引擎测试")
    print("=" * 60)
    
    engine = StealthTransferEngine('bsc_testnet')
    
    # 创建转账计划
    plan = engine.create_stealth_transfer_plan(
        total_amount=1.0,
        num_addresses=10,
        distribution='random'
    )
    
    print(f"\n助记词: {plan['mnemonic']}")
    print(f"总金额: {plan['total_amount']} BNB")
    print(f"地址数量: {plan['num_addresses']}")
    print(f"\n前 5 个接收地址:")
    for r in plan['recipients'][:5]:
        print(f"  [{r['index']}] {r['address']}: {r['amount']} BNB")
    
    print(f"\n估算费用:")
    estimate = engine.estimate_stealth_transfer_cost(10, 'standard')
    print(f"  Gas 费用: {estimate['total_cost']} {estimate['token']}")
