"""命令行工具"""
import sys
from transfer_engine import TransferEngine
from config import CHAINS


def main():
    print("=" * 60)
    print("隐私批量转账工具 - Stealth Transfer")
    print("=" * 60)
    
    # 选择链
    print("\n支持的链:")
    for i, (chain_id, config) in enumerate(CHAINS.items(), 1):
        print(f"{i}. {config['name']} ({config['native_token']})")
    
    chain_choice = input("\n选择链 (输入序号，默认 1): ").strip() or "1"
    chain_id = list(CHAINS.keys())[int(chain_choice) - 1]
    
    try:
        engine = TransferEngine(chain_id)
        print(f"\n✓ 已连接到 {engine.chain_config['name']}")
    except Exception as e:
        print(f"\n✗ 连接失败: {e}")
        return
    
    # 输入私钥
    private_key = input("\n输入发送方私钥 (0x...): ").strip()
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    
    try:
        from eth_account import Account
        account = Account.from_key(private_key)
        from_address = account.address
        balance = engine.get_balance(from_address)
        print(f"\n发送地址: {from_address}")
        print(f"当前余额: {balance} {engine.chain_config['native_token']}")
    except Exception as e:
        print(f"\n✗ 私钥无效: {e}")
        return
    
    # 输入接收地址
    print("\n输入接收地址列表 (每行一个地址，格式: 地址,金额)")
    print("示例: 0x1234...,0.01")
    print("输入完成后，输入空行结束:")
    
    recipients = []
    while True:
        line = input().strip()
        if not line:
            break
        
        try:
            addr, amount = line.split(',')
            recipients.append({
                'address': addr.strip(),
                'amount': float(amount.strip())
            })
        except:
            print(f"✗ 格式错误，跳过: {line}")
    
    if not recipients:
        print("\n✗ 没有有效的接收地址")
        return
    
    print(f"\n共 {len(recipients)} 个接收地址")
    
    # 选择 Gas 等级
    print("\nGas 价格等级:")
    gas_levels = list(engine.chain_config['gas_price_gwei'].keys())
    for i, level in enumerate(gas_levels, 1):
        gwei = engine.chain_config['gas_price_gwei'][level]
        print(f"{i}. {level.capitalize()} - {gwei} Gwei")
    
    gas_choice = input("\n选择 Gas 等级 (输入序号，默认 2): ").strip() or "2"
    gas_level = gas_levels[int(gas_choice) - 1]
    
    # 估算费用
    estimate = engine.estimate_gas_cost(len(recipients), gas_level)
    total_amount = sum(r['amount'] for r in recipients)
    
    print("\n" + "=" * 60)
    print("转账预览")
    print("=" * 60)
    print(f"接收地址数量: {len(recipients)}")
    print(f"转账总额: {total_amount} {engine.chain_config['native_token']}")
    print(f"Gas 费用: {estimate['total_cost']} {engine.chain_config['native_token']}")
    print(f"总计需要: {total_amount + estimate['total_cost']} {engine.chain_config['native_token']}")
    print(f"当前余额: {balance} {engine.chain_config['native_token']}")
    
    if balance < total_amount + estimate['total_cost']:
        print("\n✗ 余额不足！")
        return
    
    # 确认执行
    confirm = input("\n确认执行转账? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消")
        return
    
    # 执行转账
    print("\n开始批量转账...")
    try:
        results = engine.send_batch_transfers(private_key, recipients, gas_level)
        
        print("\n" + "=" * 60)
        print("转账结果")
        print("=" * 60)
        
        success_count = 0
        failed_count = 0
        
        for result in results:
            if result['status'] == 'pending':
                print(f"✓ [{result['index']}] {result['to']}: {result['amount']} {engine.chain_config['native_token']}")
                print(f"  交易哈希: {result['tx_hash']}")
                print(f"  浏览器: {result['explorer_url']}")
                success_count += 1
            else:
                print(f"✗ [{result['index']}] {result['to']}: 失败 - {result.get('error', '未知错误')}")
                failed_count += 1
        
        print(f"\n总计: {len(results)} | 成功: {success_count} | 失败: {failed_count}")
        
    except Exception as e:
        print(f"\n✗ 批量转账失败: {e}")


if __name__ == '__main__':
    main()
