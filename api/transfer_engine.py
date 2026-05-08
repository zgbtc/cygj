"""转账引擎核心逻辑"""
import time
import logging
from typing import List, Dict, Optional
from web3 import Web3
from eth_account import Account
from config import CHAINS, GAS_LIMIT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransferEngine:
    def __init__(self, chain: str = 'bsc'):
        if chain not in CHAINS:
            raise ValueError(f"不支持的链: {chain}")
        
        self.chain_config = CHAINS[chain]
        self.w3 = Web3(Web3.HTTPProvider(self.chain_config['rpc_url']))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"无法连接到 {chain} 网络")
        
        logger.info(f"已连接到 {self.chain_config['name']}")
    
    def validate_addresses(self, addresses: List[str]) -> tuple[bool, str]:
        """验证地址列表"""
        if not addresses:
            return False, "地址列表为空"
        
        if len(addresses) < 10:
            return False, f"地址数量不足，最少需要 10 个地址"
        
        if len(addresses) > 10000:
            return False, f"地址数量超限，最多支持 10000 个地址"
        
        for addr in addresses:
            if not self.w3.is_address(addr):
                return False, f"无效的地址: {addr}"
        
        return True, "验证通过"
    
    def estimate_gas_cost(self, num_addresses: int, gas_price_level: str = 'standard') -> Dict:
        """估算总 Gas 费用"""
        gas_price_gwei = self.chain_config['gas_price_gwei'].get(gas_price_level, 5)
        gas_price_wei = self.w3.to_wei(gas_price_gwei, 'gwei')
        
        total_gas = GAS_LIMIT * num_addresses
        total_cost_wei = total_gas * gas_price_wei
        total_cost_ether = self.w3.from_wei(total_cost_wei, 'ether')
        
        return {
            'num_addresses': num_addresses,
            'gas_price_gwei': gas_price_gwei,
            'gas_per_tx': GAS_LIMIT,
            'total_gas': total_gas,
            'total_cost_wei': total_cost_wei,
            'total_cost': float(total_cost_ether),
            'token': self.chain_config['native_token']
        }
    
    def get_balance(self, address: str) -> float:
        """获取地址余额"""
        balance_wei = self.w3.eth.get_balance(address)
        return float(self.w3.from_wei(balance_wei, 'ether'))
    
    def build_transaction(self, from_address: str, to_address: str, 
                         amount_wei: int, gas_price_level: str = 'standard') -> Dict:
        """构建交易"""
        gas_price_gwei = self.chain_config['gas_price_gwei'].get(gas_price_level, 5)
        gas_price_wei = self.w3.to_wei(gas_price_gwei, 'gwei')
        
        nonce = self.w3.eth.get_transaction_count(from_address)
        
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': amount_wei,
            'gas': GAS_LIMIT,
            'gasPrice': gas_price_wei,
            'chainId': self.chain_config['chain_id']
        }
        
        return tx
    
    def send_batch_transfers(self, private_key: str, recipients: List[Dict], 
                            gas_price_level: str = 'standard') -> List[Dict]:
        """批量发送转账
        
        Args:
            private_key: 发送方私钥
            recipients: 接收方列表 [{'address': '0x...', 'amount': 0.01}, ...]
            gas_price_level: Gas 价格等级
        
        Returns:
            交易结果列表
        """
        account = Account.from_key(private_key)
        from_address = account.address
        
        # 验证地址
        addresses = [r['address'] for r in recipients]
        valid, msg = self.validate_addresses(addresses)
        if not valid:
            raise ValueError(msg)
        
        # 检查余额
        balance = self.get_balance(from_address)
        total_amount = sum(r['amount'] for r in recipients)
        gas_cost = self.estimate_gas_cost(len(recipients), gas_price_level)
        
        required_balance = total_amount + gas_cost['total_cost']
        if balance < required_balance:
            raise ValueError(
                f"余额不足。需要: {required_balance} {self.chain_config['native_token']}, "
                f"当前: {balance} {self.chain_config['native_token']}"
            )
        
        results = []
        nonce = self.w3.eth.get_transaction_count(from_address)
        
        for i, recipient in enumerate(recipients):
            try:
                to_address = recipient['address']
                amount = recipient['amount']
                amount_wei = self.w3.to_wei(amount, 'ether')
                
                tx = self.build_transaction(from_address, to_address, amount_wei, gas_price_level)
                tx['nonce'] = nonce + i
                
                signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                result = {
                    'index': i + 1,
                    'to': to_address,
                    'amount': amount,
                    'tx_hash': tx_hash.hex(),
                    'status': 'pending',
                    'explorer_url': f"{self.chain_config['explorer']}/tx/{tx_hash.hex()}"
                }
                
                results.append(result)
                logger.info(f"[{i+1}/{len(recipients)}] 已发送到 {to_address}: {amount} {self.chain_config['native_token']}")
                
                # 避免 nonce 冲突，添加小延迟
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"发送到 {recipient['address']} 失败: {str(e)}")
                results.append({
                    'index': i + 1,
                    'to': recipient['address'],
                    'amount': recipient['amount'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
