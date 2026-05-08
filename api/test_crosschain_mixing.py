"""测试跨链混币完整流程"""
from lifi_bridge import LiFiBridge
from web3 import Web3

def test_crosschain_mixing_flow():
    """
    测试跨链混币流程（不执行真实交易）
    
    流程：
    1. 在Polygon上混币（50跳）
    2. 跨链到BSC（使用LiFi）
    3. 在BSC上继续混币（50跳）
    4. 汇总到目标地址
    """
    print("=" * 60)
    print("跨链混币流程测试")
    print("=" * 60)
    
    # 初始化LiFi桥接
    bridge = LiFiBridge(use_proxy=False)
    
    # 测试地址
    test_address = "0x1234567890123456789012345678901234567890"
    amount = 0.1  # 0.1 MATIC
    
    print("\n📋 混币计划:")
    print("  1. Polygon混币（50跳）")
    print("  2. 跨链 Polygon → BSC")
    print("  3. BSC混币（50跳）")
    print("  4. 汇总到目标地址")
    
    # 步骤1: 模拟Polygon混币
    print("\n" + "=" * 60)
    print("步骤1: Polygon混币")
    print("=" * 60)
    print("  ✅ 完成50跳混币")
    print("  💰 剩余: 0.095 MATIC（扣除Gas）")
    
    # 步骤2: 获取跨链报价
    print("\n" + "=" * 60)
    print("步骤2: 跨链 Polygon → BSC")
    print("=" * 60)
    
    amount_wei = Web3.to_wei(0.095, 'ether')
    quote = bridge.get_quote(
        from_chain='polygon',
        to_chain='bsc',
        from_token='0x0000000000000000000000000000000000000000',
        to_token='0x0000000000000000000000000000000000000000',
        amount=amount_wei,
        from_address=test_address
    )
    
    if quote and 'estimate' in quote:
        estimate = quote['estimate']
        to_amount = Web3.from_wei(int(estimate['toAmount']), 'ether')
        print(f"  ✅ 跨链报价获取成功")
        print(f"  💰 预计收到: {to_amount} BNB")
        print(f"  ⏱️ 预计时间: {estimate.get('executionDuration', 'N/A')} 秒")
        
        # 步骤3: 模拟BSC混币
        print("\n" + "=" * 60)
        print("步骤3: BSC混币")
        print("=" * 60)
        print(f"  ✅ 完成50跳混币")
        print(f"  💰 剩余: {float(to_amount) - 0.005:.6f} BNB（扣除Gas）")
        
        # 步骤4: 汇总
        print("\n" + "=" * 60)
        print("步骤4: 汇总到目标地址")
        print("=" * 60)
        print(f"  ✅ 汇总完成")
        print(f"  🎉 目标地址收到: {float(to_amount) - 0.005:.6f} BNB")
        
        print("\n" + "=" * 60)
        print("✅ 跨链混币流程测试完成")
        print("=" * 60)
        print("\n💡 说明:")
        print("  - 此测试仅模拟流程，未执行真实交易")
        print("  - 实际使用需要提供真实私钥和足够的Gas费")
        print("  - LiFi API已验证可用，可以执行真实跨链")
        
    else:
        print("  ❌ 获取跨链报价失败")
        print("  💡 可能原因:")
        print("     - API限流")
        print("     - 网络问题")
        print("     - 链不支持")

if __name__ == '__main__':
    test_crosschain_mixing_flow()
