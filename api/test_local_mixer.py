"""本地测试混币器 - 使用测试网"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from advanced_mixer_engine import AdvancedMixerEngine
from eth_account import Account

def test_local_mixing():
    """本地测试混币流程"""
    print("=" * 60)
    print("本地混币测试")
    print("=" * 60)
    
    # 生成测试账户
    print("\n1. 生成测试账户...")
    source_account = Account.create()
    target_account = Account.create()
    
    print(f"   源地址: {source_account.address}")
    print(f"   目标地址: {target_account.address}")
    print(f"   源私钥: {source_account.key.hex()}")
    
    # 创建混币引擎（快速模式）
    print("\n2. 初始化混币引擎（快速模式）...")
    mixer = AdvancedMixerEngine('bsc_testnet', mode='fast')
    
    # 检查余额
    print("\n3. 检查源地址余额...")
    balance = mixer.transfer_engine.get_balance(source_account.address)
    print(f"   余额: {balance} BNB")
    
    if balance < 0.01:
        print("\n⚠️ 余额不足，无法执行混币")
        print(f"   请向源地址充值至少 0.01 BNB")
        print(f"   源地址: {source_account.address}")
        print(f"\n   获取测试币:")
        print(f"   https://testnet.binance.org/faucet-smart")
        return
    
    # 创建混币计划
    print("\n4. 创建混币计划...")
    try:
        plan = mixer.create_mixing_plan(
            from_private_key=source_account.key.hex(),
            to_address=target_account.address,
            total_amount=0.01,
            num_hops=10,
            mnemonic=None
        )
        
        print(f"   ✅ 混币计划创建成功")
        print(f"   总金额: {plan['total_amount']} BNB")
        print(f"   跳数: {plan['num_hops']}")
        print(f"   服务费: {plan['fees']['service_fee']} BNB")
        print(f"   Gas 费: {plan['fees']['gas_fee']} BNB")
        print(f"   净金额: {plan['fees']['net_amount']} BNB")
        print(f"   中间地址数: {len(plan['intermediate_addresses'])}")
        
        # 询问是否执行
        print("\n5. 是否执行混币？")
        print("   注意: 这将消耗真实的测试网 BNB")
        confirm = input("   输入 'yes' 继续: ")
        
        if confirm.lower() != 'yes':
            print("\n   ❌ 已取消")
            return
        
        # 执行混币
        print("\n6. 执行混币...")
        result = mixer.execute_mixing(plan, gas_level='standard')
        
        # 显示结果
        print("\n" + "=" * 60)
        print("混币结果")
        print("=" * 60)
        print(f"成功: {result['success']}")
        print(f"总交易数: {result['total_transactions']}")
        print(f"成功数: {result['success_count']}")
        print(f"失败数: {result['failed_count']}")
        print(f"目标地址收到: {result['total_collected']} BNB")
        print(f"服务费: {result['service_fee']} BNB")
        
        # 验证目标地址余额
        print("\n7. 验证目标地址余额...")
        target_balance = mixer.transfer_engine.get_balance(target_account.address)
        print(f"   目标地址余额: {target_balance} BNB")
        
        if target_balance > 0:
            print(f"   ✅ 混币成功！")
        else:
            print(f"   ⚠️ 目标地址余额为 0，请检查交易")
        
    except Exception as e:
        print(f"\n   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def test_fee_calculation():
    """测试费用计算"""
    print("\n" + "=" * 60)
    print("费用计算测试")
    print("=" * 60)
    
    mixer = AdvancedMixerEngine('bsc_testnet', mode='fast')
    
    test_cases = [
        (10, 0.01),
        (50, 0.1),
        (100, 0.5),
        (500, 1.0),
        (1000, 10.0)
    ]
    
    print("\n跳数 | 总金额 | 服务费 | Gas费 | 总费用 | 净金额")
    print("-" * 60)
    
    for num_hops, amount in test_cases:
        fees = mixer.calculate_fees(num_hops, amount)
        print(f"{num_hops:4d} | {amount:6.2f} | {fees['service_fee']:6.3f} | {fees['gas_fee']:5.3f} | {fees['total_fee']:6.3f} | {fees['net_amount']:6.3f}")

if __name__ == '__main__':
    print("\n选择测试:")
    print("1. 费用计算测试（无需余额）")
    print("2. 完整混币测试（需要测试网 BNB）")
    
    choice = input("\n输入选项 (1 或 2): ")
    
    if choice == '1':
        test_fee_calculation()
    elif choice == '2':
        test_local_mixing()
    else:
        print("无效选项")
