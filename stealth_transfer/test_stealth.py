"""测试隐私转账功能"""
from hd_wallet import HDWallet
from stealth_engine import StealthTransferEngine

def test_hd_wallet():
    """测试 HD 钱包"""
    print("=" * 60)
    print("测试 1: HD 钱包生成地址")
    print("=" * 60)
    
    # 生成新钱包
    wallet = HDWallet()
    print(f"\n✓ 生成新助记词:")
    print(f"  {wallet.mnemonic}")
    
    # 生成 10 个地址
    addresses = wallet.generate_addresses(10)
    print(f"\n✓ 生成 10 个地址:")
    for addr in addresses:
        print(f"  [{addr['index']}] {addr['address']}")
    
    # 从助记词恢复
    print(f"\n✓ 从助记词恢复:")
    wallet2 = HDWallet(wallet.mnemonic)
    addresses2 = wallet2.generate_addresses(3)
    for addr in addresses2:
        print(f"  [{addr['index']}] {addr['address']}")
    
    # 验证地址一致
    assert addresses[0]['address'] == addresses2[0]['address']
    print(f"\n✓ 地址验证通过！")


def test_stealth_plan():
    """测试隐私转账计划"""
    print("\n" + "=" * 60)
    print("测试 2: 创建隐私转账计划")
    print("=" * 60)
    
    engine = StealthTransferEngine('bsc_testnet')
    
    # 创建计划 - 随机分配
    print("\n✓ 创建随机分配计划:")
    plan = engine.create_stealth_transfer_plan(
        total_amount=1.0,
        num_addresses=10,
        distribution='random'
    )
    
    print(f"  助记词: {plan['mnemonic']}")
    print(f"  总金额: {plan['total_amount']}")
    print(f"  地址数量: {plan['num_addresses']}")
    print(f"  分配方式: {plan['distribution']}")
    
    print(f"\n  前 5 个地址:")
    for r in plan['recipients'][:5]:
        print(f"    [{r['index']}] {r['address']}: {r['amount']}")
    
    # 验证总金额
    total = sum(r['amount'] for r in plan['recipients'])
    print(f"\n  总金额验证: {total:.8f} (应为 {plan['total_amount']})")
    assert abs(total - plan['total_amount']) < 0.00000001
    print(f"  ✓ 金额验证通过！")
    
    # 创建计划 - 平均分配
    print("\n✓ 创建平均分配计划:")
    plan2 = engine.create_stealth_transfer_plan(
        total_amount=1.0,
        num_addresses=10,
        distribution='equal'
    )
    
    amounts = [r['amount'] for r in plan2['recipients']]
    print(f"  每个地址金额: {amounts[0]}")
    assert all(amt == amounts[0] for amt in amounts)
    print(f"  ✓ 平均分配验证通过！")


def test_estimate():
    """测试费用估算"""
    print("\n" + "=" * 60)
    print("测试 3: 费用估算")
    print("=" * 60)
    
    engine = StealthTransferEngine('bsc')
    
    test_cases = [10, 50, 100, 500, 1000]
    
    print("\n不同地址数量的费用估算:")
    for num in test_cases:
        estimate = engine.estimate_stealth_transfer_cost(num, 'standard')
        print(f"  {num:4d} 个地址 -> {estimate['total_cost']:.6f} BNB")


def test_address_generation_speed():
    """测试地址生成速度"""
    print("\n" + "=" * 60)
    print("测试 4: 地址生成速度")
    print("=" * 60)
    
    import time
    
    wallet = HDWallet()
    
    test_counts = [10, 100, 1000]
    
    for count in test_counts:
        start = time.time()
        addresses = wallet.generate_addresses(count)
        elapsed = time.time() - start
        
        print(f"\n  生成 {count:4d} 个地址: {elapsed:.3f} 秒 ({count/elapsed:.0f} 地址/秒)")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("隐私转账功能测试")
    print("=" * 60)
    
    try:
        test_hd_wallet()
        test_stealth_plan()
        test_estimate()
        test_address_generation_speed()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
