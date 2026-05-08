"""混币器引擎 - Tumbler 实现"""
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

# 服务费配置
FEE_CONFIG = {
    'fee_address': Web3.to_checksum_address('0xe602348170bc045c588bf1638b0edc592f767250'),
    'fee_rates': {
        10: 0.003,    # 10 次转账：0.003 BNB 固定
        50: 0.015,    # 50 次：0.015 BNB
        100: 0.03,    # 100 次：0.03 BNB
        500: 0.15,    # 500 次：0.15 BNB
        1000: 0.30    # 1000 次：0.30 BNB
    }
}


class MixerEngine:
    """混币器引擎 - 通过多跳转账隐藏资金路径"""
    
    def __init__(self, chain: str = 'bsc_testnet'):
        self.transfer_engine = TransferEngine(chain)
        self.chain = chain
        self.w3 = self.transfer_engine.w3
    
    def calculate_fees(self, num_hops: int, total_amount: float) -> Dict:
        """
        计算费用
        
        Args:
            num_hops: 转账跳数
            total_amount: 总金额
        
        Returns:
            费用详情
        """
        # 服务费（固定金额，不是百分比）
        service_fee = FEE_CONFIG['fee_rates'].get(num_hops, 0.03)
        
        # Gas 费用估算
        gas_estimate = self.transfer_engine.estimate_gas_cost(num_hops, 'standard')
        gas_fee = gas_estimate['total_cost']
        
        # 总费用
        total_fee = service_fee + gas_fee
        
        # 用户实际收到
        net_amount = total_amount - total_fee
        
        return {
            'total_amount': total_amount,
            'service_fee': service_fee,
            'gas_fee': gas_fee,
            'total_fee': total_fee,
            'net_amount': net_amount,
            'num_hops': num_hops
        }
    
    def generate_mixing_path(
        self,
        num_addresses: int,
        min_hops: int = 3,
        max_hops: int = 10
    ) -> List[List[int]]:
        """
        生成混币路径
        
        Args:
            num_addresses: 中间地址数量
            min_hops: 最小跳数
            max_hops: 最大跳数
        
        Returns:
            路径列表，每条路径是地址索引列表
        """
        paths = []
        num_paths = max(3, num_addresses // 10)  # 至少 3 条路径
        
        for _ in range(num_paths):
            # 随机跳数
            num_hops = random.randint(min_hops, max_hops)
            
            # 随机选择地址索引
            path = random.sample(range(num_addresses), num_hops)
            paths.append(path)
        
        return paths
    
    def create_mixing_plan(
        self,
        from_private_key: str,
        to_address: str,
        total_amount: float,
        num_hops: int = 100,
        mnemonic: str = None
    ) -> Dict:
        """
        创建混币计划
        
        Args:
            from_private_key: 源地址私钥
            to_address: 目标地址
            total_amount: 总金额
            num_hops: 转账跳数（实际转账次数）
            mnemonic: 助记词（可选）
        
        Returns:
            混币计划
        """
        # 验证源地址
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
        
        # 生成中间地址（数量 = 跳数）
        wallet = HDWallet(mnemonic)
        intermediate_addresses = wallet.generate_addresses(num_hops)
        
        # 创建简单的线性路径：每个地址转到下一个地址
        # 这样正好是 num_hops 次转账
        transfer_path = list(range(num_hops))
        
        # 创建转账计划
        plan = {
            'from_address': from_address,
            'from_private_key': from_private_key,
            'to_address': to_address,
            'mnemonic': wallet.mnemonic,
            'total_amount': total_amount,
            'fees': fees,
            'num_hops': num_hops,
            'intermediate_addresses': intermediate_addresses,
            'transfer_path': transfer_path,  # 线性路径
            'chain': self.chain
        }
        
        return plan
    
    def execute_mixing(
        self,
        plan: Dict,
        gas_level: str = 'standard',
        delay_range: Tuple[int, int] = (1, 3)
    ) -> Dict:
        """
        执行混币 - 线性路径版本
        
        Args:
            plan: 混币计划
            gas_level: Gas 等级
            delay_range: 延迟范围（秒）
        
        Returns:
            执行结果
        """
        logger.info("=" * 60)
        logger.info("开始执行混币")
        logger.info("=" * 60)
        
        from_address = plan['from_address']
        from_private_key = plan['from_private_key']
        to_address = plan['to_address']
        intermediate_addresses = plan['intermediate_addresses']
        transfer_path = plan['transfer_path']
        fees = plan['fees']
        num_hops = plan['num_hops']
        
        results = []
        
        # 计算每次转账的金额（平均分配）
        amount_per_hop = fees['net_amount'] / num_hops
        
        logger.info(f"\n总跳数: {num_hops}")
        logger.info(f"每跳金额: {amount_per_hop:.8f} BNB")
        
        # 第一步：从源地址转到第一个中间地址
        logger.info("\n开始线性转账...")
        
        first_addr = intermediate_addresses[0]['address']
        
        try:
            result = self._send_transaction(
                from_private_key=from_private_key,
                to_address=first_addr,
                amount=amount_per_hop,
                gas_level=gas_level
            )
            
            results.append({
                'hop': 1,
                'from': from_address,
                'to': first_addr,
                'amount': amount_per_hop,
                'status': 'success',
                'tx_hash': result['tx_hash']
            })
            
            logger.info(f"跳 1/{num_hops}: {from_address[:10]}... → {first_addr[:10]}... ({amount_per_hop:.8f} BNB)")
            time.sleep(random.uniform(*delay_range))
            
        except Exception as e:
            logger.error(f"跳 1 失败: {e}")
            results.append({
                'hop': 1,
                'from': from_address,
                'to': first_addr,
                'amount': amount_per_hop,
                'status': 'failed',
                'error': str(e)
            })
        
        # 第二步：在中间地址之间线性转账
        for i in range(len(transfer_path) - 1):
            hop_num = i + 2
            from_idx = transfer_path[i]
            to_idx = transfer_path[i + 1]
            
            from_addr_info = intermediate_addresses[from_idx]
            to_addr_info = intermediate_addresses[to_idx]
            
            from_addr = from_addr_info['address']
            from_pk = from_addr_info['private_key']
            to_addr = to_addr_info['address']
            
            # 获取当前余额
            balance = self.transfer_engine.get_balance(from_addr)
            
            # 预留 Gas 费用
            gas_reserve = 0.0003
            
            if balance <= gas_reserve:
                logger.warning(f"跳 {hop_num}/{num_hops}: {from_addr[:10]}... 余额不足，跳过")
                continue
            
            # 转账金额
            amount = balance - gas_reserve
            amount = round(amount, 8)
            
            if amount <= 0:
                logger.warning(f"跳 {hop_num}/{num_hops}: 金额为 0，跳过")
                continue
            
            try:
                result = self._send_transaction(
                    from_private_key=from_pk,
                    to_address=to_addr,
                    amount=amount,
                    gas_level=gas_level
                )
                
                results.append({
                    'hop': hop_num,
                    'from': from_addr,
                    'to': to_addr,
                    'amount': amount,
                    'status': 'success',
                    'tx_hash': result['tx_hash']
                })
                
                logger.info(f"跳 {hop_num}/{num_hops}: {from_addr[:10]}... → {to_addr[:10]}... ({amount:.8f} BNB)")
                time.sleep(random.uniform(*delay_range))
                
            except Exception as e:
                logger.error(f"跳 {hop_num}/{num_hops} 失败: {e}")
                results.append({
                    'hop': hop_num,
                    'from': from_addr,
                    'to': to_addr,
                    'amount': amount,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 第三步：从最后一个中间地址转到目标地址
        logger.info("\n汇总到目标地址...")
        
        last_addr_info = intermediate_addresses[-1]
        last_addr = last_addr_info['address']
        last_pk = last_addr_info['private_key']
        
        balance = self.transfer_engine.get_balance(last_addr)
        gas_reserve = 0.0003
        
        total_collected = 0
        
        if balance > gas_reserve:
            amount = balance - gas_reserve
            amount = round(amount, 8)
            total_collected = amount
            
            try:
                result = self._send_transaction(
                    from_private_key=last_pk,
                    to_address=to_address,
                    amount=amount,
                    gas_level=gas_level
                )
                
                results.append({
                    'hop': num_hops,
                    'from': last_addr,
                    'to': to_address,
                    'amount': amount,
                    'status': 'success',
                    'tx_hash': result['tx_hash']
                })
                
                logger.info(f"最终汇总: {last_addr[:10]}... → {to_address[:10]}... ({amount:.8f} BNB)")
                
            except Exception as e:
                logger.error(f"最终汇总失败: {e}")
                results.append({
                    'hop': num_hops,
                    'from': last_addr,
                    'to': to_address,
                    'amount': amount,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 第四步：转服务费
        logger.info("\n转服务费...")
        
        service_fee = fees['service_fee']
        fee_address = FEE_CONFIG['fee_address']
        
        try:
            result = self._send_transaction(
                from_private_key=from_private_key,
                to_address=fee_address,
                amount=service_fee,
                gas_level=gas_level
            )
            
            logger.info(f"服务费: {service_fee:.8f} BNB → {fee_address[:10]}...")
            
        except Exception as e:
            logger.error(f"服务费转账失败: {e}")
        
        # 统计结果
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = len(results) - success_count
        
        logger.info("\n" + "=" * 60)
        logger.info("混币完成")
        logger.info("=" * 60)
        logger.info(f"总交易数: {len(results)}")
        logger.info(f"成功: {success_count}")
        logger.info(f"失败: {failed_count}")
        logger.info(f"目标地址收到: {total_collected:.8f} BNB")
        logger.info(f"服务费: {service_fee:.8f} BNB")
        
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
        """
        执行混币
        
        Args:
            plan: 混币计划
            gas_level: Gas 等级
            delay_range: 延迟范围（秒）
        
        Returns:
            执行结果
        """
        logger.info("=" * 60)
        logger.info("开始执行混币")
        logger.info("=" * 60)
        
        from_address = plan['from_address']
        from_private_key = plan['from_private_key']
        to_address = plan['to_address']
        intermediate_addresses = plan['intermediate_addresses']
        paths = plan['paths']
        fees = plan['fees']
        
        results = []
        
        # 第一步：从源地址分散到多个中间地址
        logger.info("\n第 1 步：分散资金到中间地址")
        
        # 计算每条路径的起始金额
        num_paths = len(paths)
        amount_per_path = fees['net_amount'] / num_paths
        
        # 获取源地址的 nonce
        source_nonce = self.w3.eth.get_transaction_count(from_address)
        
        # 给每条路径的第一个地址转账
        for i, path in enumerate(paths):
            first_addr_index = path[0]
            first_addr = intermediate_addresses[first_addr_index]['address']
            
            # 添加随机性
            amount = amount_per_path * random.uniform(0.95, 1.05)
            amount = round(amount, 8)
            
            # 确保金额足够支付 Gas
            min_amount = 0.0003  # 最小 0.0003 BNB
            if amount < min_amount:
                logger.warning(f"  路径 {i+1}: 金额太小 ({amount}), 跳过")
                continue
            
            try:
                result = self._send_transaction(
                    from_private_key=from_private_key,
                    to_address=first_addr,
                    amount=amount,
                    gas_level=gas_level,
                    nonce=source_nonce + i
                )
                
                results.append({
                    'step': 1,
                    'path_index': i,
                    'from': from_address,
                    'to': first_addr,
                    'amount': amount,
                    'status': 'success',
                    'tx_hash': result['tx_hash']
                })
                
                logger.info(f"  路径 {i+1}: {from_address[:10]}... → {first_addr[:10]}... ({amount} BNB)")
                
                # 延迟
                time.sleep(random.uniform(*delay_range))
                
            except Exception as e:
                logger.error(f"  路径 {i+1} 失败: {e}")
                results.append({
                    'step': 1,
                    'path_index': i,
                    'from': from_address,
                    'to': first_addr,
                    'amount': amount,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 第二步：在中间地址之间跳转
        logger.info("\n第 2 步：中间地址跳转")
        
        for path_index, path in enumerate(paths):
            logger.info(f"\n  路径 {path_index + 1} ({len(path)} 跳):")
            
            for hop_index in range(len(path) - 1):
                from_addr_index = path[hop_index]
                to_addr_index = path[hop_index + 1]
                
                from_addr_info = intermediate_addresses[from_addr_index]
                to_addr_info = intermediate_addresses[to_addr_index]
                
                from_addr = from_addr_info['address']
                from_pk = from_addr_info['private_key']
                to_addr = to_addr_info['address']
                
                # 获取当前余额
                balance = self.transfer_engine.get_balance(from_addr)
                
                # 最小保留 Gas 费用
                gas_reserve = 0.0003
                
                if balance <= gas_reserve:
                    logger.warning(f"    跳 {hop_index + 1}: {from_addr[:10]}... 余额不足 ({balance}), 跳过")
                    continue
                
                # 转账金额（留一点 Gas）
                amount = balance - gas_reserve
                amount = round(amount, 8)
                
                if amount <= 0:
                    logger.warning(f"    跳 {hop_index + 1}: {from_addr[:10]}... 金额为 0，跳过")
                    continue
                
                try:
                    result = self._send_transaction(
                        from_private_key=from_pk,
                        to_address=to_addr,
                        amount=amount,
                        gas_level=gas_level
                    )
                    
                    results.append({
                        'step': 2,
                        'path_index': path_index,
                        'hop_index': hop_index,
                        'from': from_addr,
                        'to': to_addr,
                        'amount': amount,
                        'status': 'success',
                        'tx_hash': result['tx_hash']
                    })
                    
                    logger.info(f"    跳 {hop_index + 1}: {from_addr[:10]}... → {to_addr[:10]}... ({amount} BNB)")
                    
                    # 延迟
                    time.sleep(random.uniform(*delay_range))
                    
                except Exception as e:
                    logger.error(f"    跳 {hop_index + 1} 失败: {e}")
                    results.append({
                        'step': 2,
                        'path_index': path_index,
                        'hop_index': hop_index,
                        'from': from_addr,
                        'to': to_addr,
                        'amount': amount,
                        'status': 'failed',
                        'error': str(e)
                    })
        
        # 第三步：汇总到目标地址和服务费地址
        logger.info("\n第 3 步：汇总到目标地址")
        
        total_collected = 0
        
        # 收集所有路径的最后一个地址的余额
        for path_index, path in enumerate(paths):
            last_addr_index = path[-1]
            last_addr_info = intermediate_addresses[last_addr_index]
            last_addr = last_addr_info['address']
            last_pk = last_addr_info['private_key']
            
            balance = self.transfer_engine.get_balance(last_addr)
            
            gas_reserve = 0.0003
            
            if balance <= gas_reserve:
                logger.warning(f"  路径 {path_index + 1} 最后地址余额不足 ({balance}), 跳过")
                continue
            
            # 转到目标地址
            amount = balance - gas_reserve
            amount = round(amount, 8)
            
            if amount <= 0:
                logger.warning(f"  路径 {path_index + 1} 金额为 0，跳过")
                continue
            
            total_collected += amount
            
            try:
                result = self._send_transaction(
                    from_private_key=last_pk,
                    to_address=to_address,
                    amount=amount,
                    gas_level=gas_level
                )
                
                results.append({
                    'step': 3,
                    'path_index': path_index,
                    'from': last_addr,
                    'to': to_address,
                    'amount': amount,
                    'status': 'success',
                    'tx_hash': result['tx_hash']
                })
                
                logger.info(f"  路径 {path_index + 1}: {last_addr[:10]}... → {to_address[:10]}... ({amount} BNB)")
                
                time.sleep(random.uniform(*delay_range))
                
            except Exception as e:
                logger.error(f"  路径 {path_index + 1} 汇总失败: {e}")
                results.append({
                    'step': 3,
                    'path_index': path_index,
                    'from': last_addr,
                    'to': to_address,
                    'amount': amount,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 第四步：转服务费
        logger.info("\n第 4 步：转服务费")
        
        service_fee = fees['service_fee']
        fee_address = FEE_CONFIG['fee_address']
        
        try:
            result = self._send_transaction(
                from_private_key=from_private_key,
                to_address=fee_address,
                amount=service_fee,
                gas_level=gas_level
            )
            
            results.append({
                'step': 4,
                'from': from_address,
                'to': fee_address,
                'amount': service_fee,
                'status': 'success',
                'tx_hash': result['tx_hash']
            })
            
            logger.info(f"  服务费: {from_address[:10]}... → {fee_address[:10]}... ({service_fee} BNB)")
            
        except Exception as e:
            logger.error(f"  服务费转账失败: {e}")
            results.append({
                'step': 4,
                'from': from_address,
                'to': fee_address,
                'amount': service_fee,
                'status': 'failed',
                'error': str(e)
            })
        
        # 统计结果
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = len(results) - success_count
        
        logger.info("\n" + "=" * 60)
        logger.info("混币完成")
        logger.info("=" * 60)
        logger.info(f"总交易数: {len(results)}")
        logger.info(f"成功: {success_count}")
        logger.info(f"失败: {failed_count}")
        logger.info(f"目标地址收到: {total_collected} BNB")
        logger.info(f"服务费: {service_fee} BNB")
        
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
        
        # 检查余额
        balance = self.transfer_engine.get_balance(from_address)
        if balance < amount:
            raise ValueError(f"余额不足: {balance} < {amount}")
        
        amount_wei = self.w3.to_wei(amount, 'ether')
        
        # 获取 nonce
        if nonce is None:
            nonce = self.w3.eth.get_transaction_count(from_address)
        
        # 构建交易
        gas_price_gwei = self.transfer_engine.chain_config['gas_price_gwei'].get(gas_level, 5)
        gas_price_wei = self.w3.to_wei(gas_price_gwei, 'gwei')
        
        # 确保地址格式正确
        to_address = Web3.to_checksum_address(to_address)
        
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': gas_price_wei,
            'chainId': self.transfer_engine.chain_config['chain_id']
        }
        
        # 签名
        signed_tx = self.w3.eth.account.sign_transaction(tx, from_private_key)
        
        # 发送
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
    # 测试
    print("混币器引擎已加载")
