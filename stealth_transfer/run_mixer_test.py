"""完整混币测试 - 使用目标地址的余额"""
from mixer_engine import MixerEngine, FEE_CONFIG
from hd_wallet import HDWallet

# 测试助记词
mnemonic = "decline cluster album give brief scrap apart onion dust donor figure primary"

def main():
    print("=" * 60)
    print("混币器完整测试")
    print("=" * 60)
    
    wallet = HDWallet(mnemonic)
    engine = MixerEngine('bsc_testnet')
    
    # 使用地址 10 作为源（有余额）
    source_account = wallet.get_account(10)
    # 使用地址 20 作为目标
    target_account = wallet.get_account(20)
    
    print(f"\n源地址 [10]: {source_account['address']}")
    source_balance = engine.transfer_engine.get_balance(source_account['address'])
    print(f"余额: {source_balance} tBNB")
    
    print(f"\n目标地址 [20]: {target_account['address']}")
    target_balance_before = engine.transfer_engine.get_balance(target_account['address'])
    print(f"余额: {target_balance_before} tBNB")
    
    print(f"\n服务费地址: {FEE_CONFIG['fee_address']}")
    fee_balance_before = engine.transfer_engine.get_balance(FEE_CONFIG['fee_address'])
    print(f"余额: {fee_balance_before} tBNB")
    
    if source_balance < 0.01:
        print("\n⚠️  源地址余额不足")
        return
    
    # 使用 0.1 tBNB 进行测试
    test_amount = min(0.1, source_balance * 0.8)
    
    print(f"\n" + "=" * 60)
    print(f"开始混币测试")
    print(f"=" * 60)
    print(f"金额: {test_amount} tBNB")
    print(f"跳数: 10")
    
    confirm = input("\n确认执行? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消")
        return
    
    try:
        # 创建计划
        plan = engine.create_mixing_plan(
            from_private_key=source_account['private_key'],
            to_address=target_account['address'],
            total_amount=test_amount,
            num_hops=10,
            mnemonic=mnemonic
        )
        
        print(f"\n计划创建成功:")
        print(f"  服务费: {plan['fees']['service_fee']} tBNB")
        print(f"  Gas 费: {plan['fees']['gas_fee']} tBNB")
        print(f"  净收入: {plan['fees']['net_amount']} tBNB")
        print(f"  路径数: {len(plan['paths'])}")
        
        # 执行混币
        result = engine.execute_mixing(
            plan=plan,
            gas_level='standard',
            delay_range=(1, 2)
        )
        
        print(f"\n" + "=" * 60)
        print("混币完成")
        print(f"=" * 60)
        print(f"总交易: {result['total_transactions']}")
        print(f"成功: {result['success_count']}")
        print(f"失败: {result['failed_count']}")
        
        # 检查最终余额
        print(f"\n最终余额:")
        source_balance_after = engine.transfer_engine.get_balance(source_account['address'])
        target_balance_after = engine.transfer_engine.get_balance(target_account['address'])
        fee_balance_after = engine.transfer_engine.get_balance(FEE_CONFIG['fee_address'])
        
        print(f"  源地址: {source_balance_after} tBNB (变化: {source_balance_after - source_balance:+.8f})")
        print(f"  目标地址: {target_balance_after} tBNB (变化: {target_balance_after - target_balance_before:+.8f})")
        print(f"  服务费地址: {fee_balance_after} tBNB (变化: {fee_balance_after - fee_balance_before:+.8f})")
        
        print(f"\n✅ 混币测试完成！")
        
        # 显示交易链接
        print(f"\n查看交易:")
        for i, tx in enumerate(result['results'][:5]):
            if tx['status'] == 'success':
                print(f"  {i+1}. {tx.get('explorer_url', '')}")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
