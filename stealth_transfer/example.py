"""使用示例"""
from transfer_engine import TransferEngine

def example_batch_transfer():
    """批量转账示例"""
    
    # 1. 初始化引擎 (使用 BSC 测试网)
    engine = TransferEngine('bsc_testnet')
    print(f"已连接到: {engine.chain_config['name']}")
    
    # 2. 准备发送方私钥 (请替换为你的测试网私钥)
    private_key = '0x你的私钥'
    
    # 3. 准备接收地址列表 (至少 10 个地址)
    recipients = [
        {'address': '0x接收地址1', 'amount': 0.001},
        {'address': '0x接收地址2', 'amount': 0.001},
        {'address': '0x接收地址3', 'amount': 0.001},
        {'address': '0x接收地址4', 'amount': 0.001},
        {'address': '0x接收地址5', 'amount': 0.001},
        {'address': '0x接收地址6', 'amount': 0.001},
        {'address': '0x接收地址7', 'amount': 0.001},
        {'address': '0x接收地址8', 'amount': 0.001},
        {'address': '0x接收地址9', 'amount': 0.001},
        {'address': '0x接收地址10', 'amount': 0.001},
    ]
    
    # 4. 估算费用
    estimate = engine.estimate_gas_cost(len(recipients), 'standard')
    print(f"\n费用估算:")
    print(f"  地址数量: {estimate['num_addresses']}")
    print(f"  Gas 价格: {estimate['gas_price_gwei']} Gwei")
    print(f"  总费用: {estimate['total_cost']} {estimate['token']}")
    
    # 5. 检查余额
    from eth_account import Account
    account = Account.from_key(private_key)
    balance = engine.get_balance(account.address)
    print(f"\n当前余额: {balance} {engine.chain_config['native_token']}")
    
    total_amount = sum(r['amount'] for r in recipients)
    required = total_amount + estimate['total_cost']
    print(f"需要余额: {required} {engine.chain_config['native_token']}")
    
    if balance < required:
        print("\n❌ 余额不足！")
        return
    
    # 6. 执行批量转账
    print("\n开始批量转账...")
    try:
        results = engine.send_batch_transfers(
            private_key=private_key,
            recipients=recipients,
            gas_price_level='standard'
        )
        
        # 7. 显示结果
        print("\n转账结果:")
        success_count = 0
        for result in results:
            if result['status'] == 'pending':
                print(f"✅ [{result['index']}] {result['to']}: {result['amount']}")
                print(f"   交易: {result['explorer_url']}")
                success_count += 1
            else:
                print(f"❌ [{result['index']}] {result['to']}: {result.get('error', '失败')}")
        
        print(f"\n总计: {len(results)} | 成功: {success_count} | 失败: {len(results) - success_count}")
        
    except Exception as e:
        print(f"\n❌ 批量转账失败: {e}")


def example_estimate_only():
    """仅估算费用示例"""
    engine = TransferEngine('bsc')
    
    # 估算不同数量地址的费用
    for num in [10, 50, 100, 500, 1000]:
        estimate = engine.estimate_gas_cost(num, 'standard')
        print(f"{num:4d} 个地址 -> {estimate['total_cost']:.6f} BNB")


if __name__ == '__main__':
    print("=" * 60)
    print("隐私批量转账工具 - 使用示例")
    print("=" * 60)
    
    # 运行费用估算示例
    print("\n费用估算示例:")
    example_estimate_only()
    
    # 如果要运行实际转账，请取消下面的注释并配置好私钥和地址
    # print("\n批量转账示例:")
    # example_batch_transfer()
