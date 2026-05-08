"""HD 钱包 - 从助记词生成多个地址"""
from mnemonic import Mnemonic
from eth_account import Account
from typing import List, Dict
import secrets

# 启用 HD 钱包功能
Account.enable_unaudited_hdwallet_features()


class HDWallet:
    """分层确定性钱包 (BIP44)"""
    
    def __init__(self, mnemonic: str = None, language: str = 'english'):
        """
        初始化 HD 钱包
        
        Args:
            mnemonic: 助记词，如果为空则生成新的
            language: 助记词语言
        """
        self.mnemo = Mnemonic(language)
        
        if mnemonic:
            if not self.mnemo.check(mnemonic):
                raise ValueError("无效的助记词")
            self.mnemonic = mnemonic
        else:
            # 生成新的助记词
            self.mnemonic = self.mnemo.generate(strength=128)
    
    def generate_addresses(self, count: int, start_index: int = 0) -> List[Dict]:
        """
        从助记词生成多个地址
        
        Args:
            count: 生成地址数量
            start_index: 起始索引
        
        Returns:
            地址列表，每个包含 address 和 private_key
        """
        addresses = []
        
        for i in range(start_index, start_index + count):
            # BIP44 路径: m/44'/60'/0'/0/{index}
            # 60' 是 Ethereum 的 coin type
            account_path = f"m/44'/60'/0'/0/{i}"
            account = Account.from_mnemonic(self.mnemonic, account_path=account_path)
            
            addresses.append({
                'index': i,
                'address': account.address,
                'private_key': account.key.hex(),
                'path': account_path
            })
        
        return addresses
    
    def get_account(self, index: int) -> Dict:
        """获取指定索引的账户"""
        accounts = self.generate_addresses(1, index)
        return accounts[0]
    
    @staticmethod
    def from_mnemonic_to_private_key(mnemonic: str, index: int = 0) -> str:
        """
        从助记词提取指定索引的私钥
        
        Args:
            mnemonic: 助记词
            index: 地址索引（默认 0，即第一个地址）
        
        Returns:
            私钥（hex 格式）
        """
        mnemo = Mnemonic('english')
        if not mnemo.check(mnemonic):
            raise ValueError("无效的助记词")
        
        account_path = f"m/44'/60'/0'/0/{index}"
        account = Account.from_mnemonic(mnemonic, account_path=account_path)
        return account.key.hex()
    
    @staticmethod
    def generate_random_mnemonic(word_count: int = 12) -> str:
        """
        生成随机助记词
        
        Args:
            word_count: 单词数量 (12, 15, 18, 21, 24)
        """
        strength_map = {
            12: 128,
            15: 160,
            18: 192,
            21: 224,
            24: 256
        }
        
        if word_count not in strength_map:
            raise ValueError("word_count 必须是 12, 15, 18, 21 或 24")
        
        mnemo = Mnemonic('english')
        return mnemo.generate(strength=strength_map[word_count])


def create_stealth_addresses(count: int, mnemonic: str = None) -> tuple[str, List[Dict]]:
    """
    创建隐私地址
    
    Args:
        count: 地址数量
        mnemonic: 助记词（可选）
    
    Returns:
        (助记词, 地址列表)
    """
    wallet = HDWallet(mnemonic)
    addresses = wallet.generate_addresses(count)
    return wallet.mnemonic, addresses


if __name__ == '__main__':
    # 测试
    print("=" * 60)
    print("HD 钱包测试")
    print("=" * 60)
    
    # 生成新钱包
    wallet = HDWallet()
    print(f"\n助记词: {wallet.mnemonic}")
    
    # 生成 10 个地址
    print("\n生成 10 个地址:")
    addresses = wallet.generate_addresses(10)
    for addr in addresses:
        print(f"[{addr['index']}] {addr['address']}")
    
    # 从已有助记词恢复
    print("\n\n从助记词恢复:")
    test_mnemonic = wallet.mnemonic
    wallet2 = HDWallet(test_mnemonic)
    addresses2 = wallet2.generate_addresses(3)
    for addr in addresses2:
        print(f"[{addr['index']}] {addr['address']}")
        print(f"     私钥: {addr['private_key']}")
