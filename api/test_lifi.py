"""测试LiFi跨链桥接"""
from lifi_bridge import LiFiBridge

def test_lifi():
    print("=" * 60)
    print("测试LiFi跨链桥接")
    print("=" * 60)
    
    # 创建桥接实例
    bridge = LiFiBridge(use_proxy=False)
    
    # 1. 获取支持的链
    print("\n1. 获取支持的链...")
    chains = bridge.get_supported_chains()
    
    if chains:
        print(f"✅ 成功获取 {len(chains)} 条链")
        print("\n前10条链:")
        for chain in chains[:10]:
            print(f"  - {chain['name']} (ID: {chain['id']}, Key: {chain['key']})")
    else:
        print("❌ 获取链列表失败")
        return
    
    # 2. 测试获取报价（不需要真实私钥）
    print("\n2. 测试获取跨链报价...")
    print("  从: Polygon → BSC")
    print("  金额: 0.1 MATIC")
    
    from web3 import Web3
    test_address = "0x1234567890123456789012345678901234567890"
    amount_wei = Web3.to_wei(0.1, 'ether')
    
    quote = bridge.get_quote(
        from_chain='polygon',
        to_chain='bsc',
        from_token='0x0000000000000000000000000000000000000000',  # 原生币
        to_token='0x0000000000000000000000000000000000000000',
        amount=amount_wei,
        from_address=test_address
    )
    
    if quote:
        print("✅ 成功获取报价")
        if 'estimate' in quote:
            estimate = quote['estimate']
            print(f"  预计收到: {Web3.from_wei(int(estimate['toAmount']), 'ether')} BNB")
            print(f"  执行时间: {estimate.get('executionDuration', 'N/A')} 秒")
    else:
        print("❌ 获取报价失败")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_lifi()
