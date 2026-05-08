"""隐私转账命令行工具"""
import sys
from stealth_engine import StealthTransferEngine
from hd_wallet import HDWallet
from config import CHAINS


def main():
    print("=" * 60)
    print("隐私转账工具 - Stealth Transfer CLI")
    print("=" * 60)
    print("\n功能：从助记词生成多个地址，分散资金，保护隐私")
    
    # 选择链
    print("\n支持的链:")
    for i, (chain_id, config) in enumerate(CHAINS.items(), 1):
        print(f"{i}. {config['name']} ({config['native_token']})")
    
    chain_choice = input("\n选择链 (输入序号，默认 1): ").strip() or "1"
    chain_id = list(CHAINS.keys())[int(chain_choice) - 1]
    
    try:
        engine = StealthTransferEngine(chain_id)
        print(f"\n✓ 已连接到 {engine.transfer_engine.chain_config['name']}")
    except Exception as e:
        print(f"\n✗ 连接失败: {e}")
        return
    
    # 选择模式
    print("\n选择模式:")
    print("1. 生成地址（仅查看，不转账）")
    print("2. 执行隐私转账")
    
    mode = input("\n选择模式 (1 或 2): ").strip()
    
    if mode == "1":
        # 仅生成地址
        generate_addresses_mode()
    elif mode == "2":
        # 执行转账
        execute_transfer_mode(engine, chain_id)
    else:
        print("无效选择")


def generate_addresses_mode():
    """生成地址模式"""
    print("\n" + "=" * 60)
    print("生成地址模式")
    print("=" * 60)
    
    # 助记词
    use_existing = input("\n使用已有助记词? (y/n，默认 n): ").strip().lower()
    
    if use_existing == 'y':
        mnemonic = input("输入助记词: ").strip()
        wallet = HDWallet(mnemonic)
    else:
        wallet = HDWallet()
        print(f"\n✓ 已生成新助记词")
    
    print(f"\n助记词: {wallet.mnemonic}")
    print("\n⚠️  请妥善保管助记词，不要泄露给任何人！")
    
    # 生成数量
    count = int(input("\n生成地址数量 (10-10000): ").strip() or "10")
    
    if count < 10 or count > 10000:
        print("✗ 数量必须在 10-10000 之间")
        return
    
    print(f"\n正在生成 {count} 个地址...")
    addresses = wallet.generate_addresses(count)
    
    # 显示前 20 个
    print(f"\n前 20 个地址:")
    for addr in addresses[:20]:
        print(f"[{addr['index']:4d}] {addr['address']}")
    
    if count > 20:
        print(f"\n... 还有 {count - 20} 个地址")
    
    # 保存到文件
    save = input("\n保存到文件? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"stealth_addresses_{count}.txt"
        with open(filename, 'w') as f:
            f.write(f"助记词: {wallet.mnemonic}\n\n")
            f.write(f"地址列表 ({count} 个):\n")
            for addr in addresses:
                f.write(f"[{addr['index']}] {addr['address']}\n")
        print(f"\n✓ 已保存到 {filename}")


def execute_transfer_mode(engine, chain_id):
    """执行转账模式"""
    print("\n" + "=" * 60)
    print("执行隐私转账")
    print("=" * 60)
    
    # 输入源地址私钥
    from_private_key = input("\n输入源地址私钥 (0x...): ").strip()
    if not from_private_key.startswith('0x'):
        from_private_key = '0x' + from_private_key
    
    try:
        from eth_account import Account
        account = Account.from_key(from_private_key)
        from_address = account.address
        balance = engine.transfer_engine.get_balance(from_address)
        print(f"\n源地址: {from_address}")
        print(f"当前余额: {balance} {engine.transfer_engine.chain_config['native_token']}")
    except Exception as e:
        print(f"\n✗ 私钥无效: {e}")
        return
    
    # 转账金额
    total_amount = float(input("\n转账总金额: ").strip())
    
    # 地址数量
    num_addresses = int(input("目标地址数量 (10-10000): ").strip())
    
    if num_addresses < 10 or num_addresses > 10000:
        print("✗ 数量必须在 10-10000 之间")
        return
    
    # 分配方式
    print("\n分配方式:")
    print("1. 随机分配（推荐，更隐私）")
    print("2. 平均分配")
    dist_choice = input("选择 (1 或 2，默认 1): ").strip() or "1"
    distribution = 'random' if dist_choice == '1' else 'equal'
    
    # 助记词
    use_existing = input("\n使用已有助记词? (y/n，默认 n): ").strip().lower()
    mnemonic = None
    if use_existing == 'y':
        mnemonic = input("输入助记词: ").strip()
    
    # Gas 等级
    print("\nGas 价格等级:")
    gas_levels = list(engine.transfer_engine.chain_config['gas_price_gwei'].keys())
    for i, level in enumerate(gas_levels, 1):
        gwei = engine.transfer_engine.chain_config['gas_price_gwei'][level]
        print(f"{i}. {level.capitalize()} - {gwei} Gwei")
    
    gas_choice = input("\n选择 Gas 等级 (输入序号，默认 2): ").strip() or "2"
    gas_level = gas_levels[int(gas_choice) - 1]
    
    # 创建计划
    print("\n正在创建转账计划...")
    try:
        plan = engine.create_stealth_transfer_plan(
            total_amount=total_amount,
            num_addresses=num_addresses,
            mnemonic=mnemonic,
            distribution=distribution
        )
    except Exception as e:
        print(f"\n✗ 创建计划失败: {e}")
        return
    
    # 估算费用
    estimate = engine.estimate_stealth_transfer_cost(num_addresses, gas_level)
    
    # 显示计划
    print("\n" + "=" * 60)
    print("转账计划")
    print("=" * 60)
    print(f"助记词: {plan['mnemonic']}")
    print(f"\n总金额: {plan['total_amount']} {engine.transfer_engine.chain_config['native_token']}")
    print(f"地址数量: {plan['num_addresses']}")
    print(f"分配方式: {'随机' if distribution == 'random' else '平均'}")
    print(f"Gas 费用: {estimate['total_cost']} {estimate['token']}")
    print(f"总计需要: {total_amount + estimate['total_cost']} {estimate['token']}")
    
    print(f"\n前 10 个接收地址:")
    for r in plan['recipients'][:10]:
        print(f"  [{r['index']:4d}] {r['address']}: {r['amount']}")
    
    if balance < total_amount + estimate['total_cost']:
        print("\n✗ 余额不足！")
        return
    
    # 确认执行
    print("\n⚠️  请仔细核对以上信息！")
    confirm = input("\n确认执行转账? (输入 'YES' 确认): ").strip()
    if confirm != 'YES':
        print("已取消")
        return
    
    # 执行转账
    print("\n开始执行隐私转账...")
    try:
        result = engine.execute_stealth_transfer(
            from_private_key=from_private_key,
            plan=plan,
            gas_level=gas_level
        )
        
        print("\n" + "=" * 60)
        print("转账结果")
        print("=" * 60)
        print(f"助记词: {result['mnemonic']}")
        print(f"\n总计: {result['total']} | 成功: {result['success_count']} | 失败: {result['failed_count']}")
        
        # 显示前 20 条
        print(f"\n前 20 条记录:")
        for r in result['results'][:20]:
            if r['status'] == 'pending':
                print(f"✓ [{r['index']:4d}] {r['to']}: {r['amount']}")
                print(f"   交易: {r['explorer_url']}")
            else:
                print(f"✗ [{r['index']:4d}] {r['to']}: {r.get('error', '失败')}")
        
        if result['total'] > 20:
            print(f"\n... 还有 {result['total'] - 20} 条记录")
        
        # 保存结果
        filename = f"stealth_transfer_result_{num_addresses}.txt"
        with open(filename, 'w') as f:
            f.write(f"助记词: {result['mnemonic']}\n\n")
            f.write(f"转账结果:\n")
            f.write(f"总计: {result['total']} | 成功: {result['success_count']} | 失败: {result['failed_count']}\n\n")
            for r in result['results']:
                f.write(f"[{r['index']}] {r['to']}: {r['amount']} - {r['status']}\n")
                if r['status'] == 'pending':
                    f.write(f"  交易: {r['explorer_url']}\n")
        
        print(f"\n✓ 结果已保存到 {filename}")
        
    except Exception as e:
        print(f"\n✗ 转账失败: {e}")


if __name__ == '__main__':
    main()
