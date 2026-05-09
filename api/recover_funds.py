"""
紧急资金回收脚本
=================
用途：根据助记词派生所有中间地址，查询 BSC 主网余额，把所有有余额的地址一键归集到目标地址。

使用方法：
    1. 填下面的 MNEMONIC 和 TARGET_ADDRESS
    2. 运行：python api/recover_funds.py
    3. 脚本会先只查余额（只读，不动钱），显示有余额的地址
    4. 确认无误后，回 y 进行归集

依赖：
    pip install web3 mnemonic eth_account
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from web3 import Web3
from eth_account import Account

Account.enable_unaudited_hdwallet_features()

# ============ 配置 ============
MNEMONIC = "patch napkin manual fit hazard cotton surge enforce yellow chimney able cricket"
TARGET_ADDRESS = "0x7a64c34cd249be108c01c2cef5193b189795f0c4"
NUM_ADDRESSES = 14           # 派生多少个地址，10 跳 + 2 隔离 = 12，多查几个保险
BSC_RPC = "https://bsc-dataseed.binance.org"
GAS_LIMIT = 21000            # 普通转账
# ==============================


def derive_account(mnemonic: str, index: int):
    path = f"m/44'/60'/0'/0/{index}"
    return Account.from_mnemonic(mnemonic, account_path=path)


def main():
    w3 = Web3(Web3.HTTPProvider(BSC_RPC))
    if not w3.is_connected():
        print("❌ 无法连接 BSC RPC")
        return

    print(f"✅ 已连接 BSC 主网，当前区块: {w3.eth.block_number}")
    print(f"📬 归集目标: {TARGET_ADDRESS}")
    print(f"🔍 扫描 {NUM_ADDRESSES} 个中间地址...\n")

    have_balance = []  # [(index, account, balance_wei)]
    for i in range(NUM_ADDRESSES):
        acct = derive_account(MNEMONIC, i)
        bal_wei = w3.eth.get_balance(acct.address)
        bal_bnb = w3.from_wei(bal_wei, 'ether')
        mark = "💰" if bal_wei > 0 else "  "
        print(f"{mark} [#{i:02d}] {acct.address}  balance = {bal_bnb:.8f} BNB")
        if bal_wei > 0:
            have_balance.append((i, acct, bal_wei))

    if not have_balance:
        print("\n🤷 所有中间地址余额为 0，没什么可归集的")
        return

    total = sum(b for _, _, b in have_balance)
    print(f"\n💎 总计 {len(have_balance)} 个地址有余额，合计 {w3.from_wei(total, 'ether'):.8f} BNB")

    gas_price = w3.eth.gas_price
    cost_per_tx = gas_price * GAS_LIMIT
    print(f"⛽ 当前 gas 价: {w3.from_wei(gas_price, 'gwei'):.2f} gwei，每笔转账需 {w3.from_wei(cost_per_tx, 'ether'):.8f} BNB")

    # 过滤掉余额不够付 gas 的地址
    recoverable = [(i, a, b) for i, a, b in have_balance if b > cost_per_tx]
    skipped = len(have_balance) - len(recoverable)
    if skipped > 0:
        print(f"⚠️  {skipped} 个地址余额不足以支付 gas，将跳过")

    if not recoverable:
        print("😞 没有足够余额付 gas 的地址，无法归集")
        return

    net_total = sum(b - cost_per_tx for _, _, b in recoverable)
    print(f"📥 预计到账 {TARGET_ADDRESS}: {w3.from_wei(net_total, 'ether'):.8f} BNB")

    confirm = input("\n⚠️ 确认归集？输入 y 继续，其它任意键取消: ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return

    print("\n🚀 开始归集...")
    success = 0
    for idx, acct, bal in recoverable:
        send_wei = bal - cost_per_tx
        try:
            nonce = w3.eth.get_transaction_count(acct.address)
            tx = {
                'from': acct.address,
                'to': Web3.to_checksum_address(TARGET_ADDRESS),
                'value': send_wei,
                'gas': GAS_LIMIT,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': 56
            }
            signed = w3.eth.account.sign_transaction(tx, acct.key)
            raw = getattr(signed, 'raw_transaction', None) or signed.rawTransaction
            tx_hash = w3.eth.send_raw_transaction(raw)
            print(f"✅ [#{idx:02d}] {acct.address[:10]}... → {w3.from_wei(send_wei, 'ether'):.8f} BNB  tx={tx_hash.hex()}")
            success += 1
            time.sleep(0.3)  # 避免 RPC 限流
        except Exception as e:
            print(f"❌ [#{idx:02d}] {acct.address[:10]}... 归集失败: {e}")

    print(f"\n🎉 完成！成功 {success}/{len(recoverable)}")
    print(f"   稍等 1-2 个区块后，去 https://bscscan.com/address/{TARGET_ADDRESS} 查看到账")


if __name__ == '__main__':
    main()
