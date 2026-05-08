"""测试混币器功能"""
from mixer_engine import MixerEngine, FEE_CONFIG
from hd_wallet import HDWallet
from eth_account import Account

# 测试助记词
TEST_MNEMONIC = "decline cluster album give brief scrap apart onion dust donor figure primary"

def test_generate_addresses():
    """测试地址生成"""
    print("=" * 60)
    print("测试 1: 生成地址")
    print("=" * 60)
    
    wallet = HDWallet(TEST_MNEMONIC)
    print(f"\n助记词: {wallet.mnemonic}")
    
    # 生成 10 个地址
    addresses = wallet.generate_addresses(10)
    print(f"\n生成 10 个地址:")
    for addr in addresses:
        print(f"  [{addr['index']}] {addr['address']}")
    
    # 检查第一个地址的余额
    engine = MixerEngine('bsc_testnet')
    balance = engine.transfer_engine.get_balance(addresses[0]['address'])
    print(f"\n第一个地址余额: {balance} tBNB")
    
    return addresses


def test_fee_calculation():
    """测试费用计算"""
    print("\n" + "=" * 60)
    print("测试 2: 费用计算")
    print("=" * 60)
    
    engine = MixerEngine('bsc_testnet')
    
    test_cases = [
        (10, 0.1),
        (50, 0.5),
        (100, 1.0),
    ]
    
    for num_hops, amount in test_cases:
        fees = engine.calculate_fees(num_hops, amount)
        print(f"\n{num_hops} 跳，总金额 {amount} tBNB:")
        print(f"  服务费: {fees['service_fee']} tBNB ({fees['service_fee_rate']*100}%)")
        print(f"  Gas 费: {fees['gas_fee']} tBNB")
        print(f"  总费用: {fees['total_fee']} tBNB")
        print(f"  净收入: {fees['net_amount']} tBNB")


def test_mixing_plan():
    """测试混币计划"""
    print("\n" + "=" * 60)
    print("测试 3: 创建混币计划")
    print("=" * 60)
    
    engine = MixerEngine('bsc_testnet')
    
    # 使用测试助记词生成源地址
    wallet = HDWallet(TEST_MNEMONIC)
    source_account = wallet.get_account(0)
    
    print(f"\n源地址: {source_account['address']}")
    print(f"私钥: {source_account['private_key'][:20]}...")
    
    # 检查余额
    balance = engine.transfer_engine.get_balance(source_account['address'])
    print(f"余额: {balance} tBNB")
    
    if balance < 0.01:
        print("\n⚠️  余额不足，无法测试。请先充值测试币。")
        print(f"充值地址: {source_account['address']}")
        return None
    
    # 目标地址（使用第 10 个地址）
    target_account = wallet.get_account(10)
    target_address = target_account['address']
    
    print(f"\n目标地址: {target_address}")
    
    # 创建计划
    try:
        plan = engine.create_mixing_plan(
            from_private_key=source_account['private_key'],
            to_address=target_address,
            total_amount=0.01,  # 0.01 tBNB
            num_hops=10,  # 10 跳
            mnemonic=TEST_MNEMONIC
        )
        
        print(f"\n✓ 混币计划创建成功")
        print(f"  总金额: {plan['total_amount']} tBNB")
        print(f"  服务费: {plan['fees']['service_fee']} tBNB")
        print(f"  Gas 费: {plan['fees']['gas_fee']} tBNB")
        print(f"  净收入: {plan['fees']['net_amount']} tBNB")
        print(f"  跳数: {plan['num_hops']}")
        print(f"  路径数: {len(plan['paths'])}")
        
        print(f"\n前 3 条路径:")
        for i, path in enumerate(plan['paths'][:3]):
            print(f"  路径 {i+1}: {' → '.join(map(str, path))}")
        
        return plan
        
    except Exception as e:
        print(f"\n✗ 创建计划失败: {e}")
        return None


def test_execute_mixing():
    """测试执行混币"""
    print("\n" + "=" * 60)
    print("测试 4: 执行混币（实际转账）")
    print("=" * 60)
    
    engine = MixerEngine('bsc_testnet')
    
    # 使用测试助记词
    wallet = HDWallet(TEST_MNEMONIC)
    source_account = wallet.get_account(0)
    target_account = wallet.get_account(10)
    
    # 检查余额
    balance = engine.transfer_engine.get_balance(source_account['address'])
    print(f"\n源地址余额: {balance} tBNB")
    
    if balance < 0.01:
        print("\n⚠️  余额不足，无法执行混币。")
        print(f"请先给地址充值: {source_account['address']}")
        print("\n获取测试币:")
        print("  1. 访问 https://testnet.binance.org/faucet-smart")
        print(f"  2. 输入地址: {source_account['address']}")
        print("  3. 领取测试币")
        return
    
    # 确认
    print(f"\n准备执行混币:")
    print(f"  源地址: {source_account['address']}")
    print(f"  目标地址: {target_account['address']}")
    print(f"  金额: 0.01 tBNB")
    print(f"  跳数: 10")
    
    confirm = input("\n确认执行? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消")
        return
    
    try:
        # 创建计划
        plan = engine.create_mixing_plan(
            from_private_key=source_account['private_key'],
            to_address=target_account['address'],
            total_amount=0.01,
            num_hops=10,
            mnemonic=TEST_MNEMONIC
        )
        
        # 执行混币
        result = engine.execute_mixing(
            plan=plan,
            gas_level='standard',
            delay_range=(1, 2)  # 1-2 秒延迟
        )
        
        print("\n" + "=" * 60)
        print("混币结果")
        print("=" * 60)
        print(f"成功: {result['success']}")
        print(f"总交易: {result['total_transactions']}")
        print(f"成功: {result['success_count']}")
        print(f"失败: {result['failed_count']}")
        print(f"目标地址收到: {result['total_collected']} tBNB")
        print(f"服务费: {result['service_fee']} tBNB")
        
        # 显示前 10 笔交易
        print(f"\n前 10 笔交易:")
        for i, tx in enumerate(result['results'][:10]):
            status = "✓" if tx['status'] == 'success' else "✗"
            print(f"  {status} 步骤 {tx['step']}: {tx['from'][:10]}... → {tx['to'][:10]}... ({tx.get('amount', 0)} tBNB)")
            if tx['status'] == 'success':
                print(f"     交易: {tx.get('tx_hash', '')[:20]}...")
        
        # 检查最终余额
        print(f"\n最终余额:")
        source_balance = engine.transfer_engine.get_balance(source_account['address'])
        target_balance = engine.transfer_engine.get_balance(target_account['address'])
        print(f"  源地址: {source_balance} tBNB")
        print(f"  目标地址: {target_balance} tBNB")
        
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("混币器测试")
    print("=" * 60)
    print(f"\n测试助记词: {TEST_MNEMONIC}")
    print(f"服务费地址: {FEE_CONFIG['fee_address']}")
    
    # 运行测试
    test_generate_addresses()
    test_fee_calculation()
    plan = test_mixing_plan()
    
    if plan:
        print("\n" + "=" * 60)
        print("准备执行实际混币测试")
        print("=" * 60)
        test_execute_mixing()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
