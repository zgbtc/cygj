"""
资金恢复工具 - 通过 session_id 从数据库取回助记词，扫描并归集所有中间地址的资金

使用场景：
1. 跨链后目标链 gas 不足，资金卡在中间地址
2. 执行中途服务器崩溃，资金分散在中间地址
3. 任何 status=running/failed 的 session

用法：
  python recover_session.py <session_id> <destination_address>
  python recover_session.py <session_id> <destination_address> --chain arbitrum
"""
import sys
import os
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载 .env.local
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
if os.path.exists(env_path):
    for line in open(env_path, encoding='utf-8'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

from web3 import Web3
from eth_account import Account
from hd_wallet import HDWallet
from supabase_client import get_supabase_client

# 各链的 RPC 和 gas 配置
CHAIN_CONFIG = {
    'bsc': {
        'rpc': 'https://bsc.publicnode.com',
        'chain_id': 56,
        'gas_price_gwei': 5,
        'explorer': 'https://bscscan.com/tx/'
    },
    'bsc_testnet': {
        'rpc': 'https://bsc-testnet.publicnode.com',
        'chain_id': 97,
        'gas_price_gwei': 10,
        'explorer': 'https://testnet.bscscan.com/tx/'
    },
    'polygon': {
        'rpc': 'https://polygon-rpc.com',
        'chain_id': 137,
        'gas_price_gwei': 30,
        'explorer': 'https://polygonscan.com/tx/'
    },
    'arbitrum': {
        'rpc': 'https://arb1.arbitrum.io/rpc',
        'chain_id': 42161,
        'gas_price_gwei': 0.1,
        'explorer': 'https://arbiscan.io/tx/'
    },
    'optimism': {
        'rpc': 'https://mainnet.optimism.io',
        'chain_id': 10,
        'gas_price_gwei': 0.001,
        'explorer': 'https://optimistic.etherscan.io/tx/'
    },
    'base': {
        'rpc': 'https://mainnet.base.org',
        'chain_id': 8453,
        'gas_price_gwei': 0.001,
        'explorer': 'https://basescan.org/tx/'
    },
}


def get_w3(chain: str) -> Web3:
    cfg = CHAIN_CONFIG.get(chain)
    if not cfg:
        raise ValueError(f"不支持的链: {chain}，可选: {list(CHAIN_CONFIG.keys())}")
    w3 = Web3(Web3.HTTPProvider(cfg['rpc'], request_kwargs={'timeout': 15}))
    if not w3.is_connected():
        raise ConnectionError(f"无法连接到 {chain}")
    return w3


def scan_and_recover(
    mnemonic: str,
    num_hops: int,
    destination: str,
    chain: str,
    dry_run: bool = False
) -> dict:
    """
    扫描助记词派生的所有地址，把有余额的资金归集到 destination

    Args:
        mnemonic: 助记词
        num_hops: 跳数（扫描 num_hops + 10 个地址，多扫一些防遗漏）
        destination: 归集目标地址
        chain: 链名称
        dry_run: True=只扫描不发交易

    Returns:
        {'found': int, 'recovered': float, 'txs': list}
    """
    cfg = CHAIN_CONFIG[chain]
    w3 = get_w3(chain)
    destination = Web3.to_checksum_address(destination)

    wallet = HDWallet(mnemonic)
    # 多扫 20 个地址，防止 start_index 偏移导致遗漏
    addresses = wallet.generate_addresses(num_hops + 20, start_index=0)

    gas_price_wei = w3.to_wei(cfg['gas_price_gwei'], 'gwei')
    gas_cost = 21000 * gas_price_wei
    gas_cost_ether = float(w3.from_wei(gas_cost, 'ether'))

    print(f"\n🔍 扫描 {len(addresses)} 个地址 on {chain}...")
    print(f"   gas 费用/笔: {gas_cost_ether:.8f}")

    found_count = 0
    total_recovered = 0.0
    txs = []

    for addr_info in addresses:
        addr = Web3.to_checksum_address(addr_info['address'])
        pk = addr_info['private_key']

        try:
            bal_wei = w3.eth.get_balance(addr)
            bal = float(w3.from_wei(bal_wei, 'ether'))
        except Exception as e:
            print(f"  ⚠️ 查询 {addr[:10]}... 失败: {e}")
            continue

        if bal <= gas_cost_ether * 1.5:
            continue  # 余额不够付 gas，跳过

        found_count += 1
        send_amount = bal - gas_cost_ether * 1.2  # 留 1.2x gas buffer
        send_amount = round(send_amount, 8)

        print(f"  💰 发现余额: {addr[:10]}... = {bal:.8f}  可归集: {send_amount:.8f}")

        if dry_run:
            print(f"     [dry_run] 跳过发送")
            total_recovered += send_amount
            continue

        try:
            nonce = w3.eth.get_transaction_count(addr, 'pending')
            tx = {
                'nonce': nonce,
                'to': destination,
                'value': w3.to_wei(send_amount, 'ether'),
                'gas': 21000,
                'gasPrice': gas_price_wei,
                'chainId': cfg['chain_id']
            }
            signed = w3.eth.account.sign_transaction(tx, pk)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            tx_hex = tx_hash.hex()

            print(f"  ✅ 已发送: {tx_hex[:16]}...  {cfg['explorer']}{tx_hex}")
            txs.append({'address': addr, 'amount': send_amount, 'tx_hash': tx_hex})
            total_recovered += send_amount
            time.sleep(0.3)

        except Exception as e:
            print(f"  ❌ 发送失败: {e}")

    return {
        'found': found_count,
        'recovered': total_recovered,
        'txs': txs
    }


def main():
    parser = argparse.ArgumentParser(description='从 session 恢复卡住的资金')
    parser.add_argument('session_id', help='session ID（12位 hex）')
    parser.add_argument('destination', help='归集目标地址')
    parser.add_argument('--chain', default=None,
                        help='指定链（默认从 session 读取，跨链时可指定 arbitrum/polygon 等）')
    parser.add_argument('--dry-run', action='store_true',
                        help='只扫描不发交易')
    args = parser.parse_args()

    print(f"{'='*60}")
    print(f"资金恢复工具")
    print(f"{'='*60}")
    print(f"session_id: {args.session_id}")
    print(f"destination: {args.destination}")
    print(f"dry_run: {args.dry_run}")

    # 从数据库读取 session
    db = get_supabase_client()
    row = db.client.table('mix_sessions').select('*').eq('id', args.session_id).execute()

    if not row.data:
        print(f"\n❌ 找不到 session: {args.session_id}")
        sys.exit(1)

    session = row.data[0]
    print(f"\n📋 Session 信息:")
    print(f"  mode:         {session['mode']}")
    print(f"  chain:        {session['chain']}")
    print(f"  from_address: {session['from_address']}")
    print(f"  to_address:   {session['to_address']}")
    print(f"  total_amount: {session['total_amount']}")
    print(f"  num_hops:     {session['num_hops']}")
    print(f"  status:       {session['status']}")
    print(f"  mnemonic:     {session['mnemonic_enc'][:30]}...")

    mnemonic = session['mnemonic_enc']
    num_hops = int(session['num_hops'])

    if not mnemonic:
        print(f"\n❌ 数据库中没有助记词，无法恢复")
        sys.exit(1)

    # 确定要扫描的链
    chains_to_scan = []
    if args.chain:
        chains_to_scan = [args.chain]
    else:
        # 默认扫描 session 的链
        session_chain = session['chain']
        chains_to_scan = [session_chain]
        # 如果是 ultimate 模式，也扫描可能的跨链目标链
        if session['mode'] == 'ultimate':
            extra_chains = ['arbitrum', 'polygon', 'optimism', 'base']
            print(f"\n⚠️ Ultimate 模式，同时扫描跨链目标链: {extra_chains}")
            chains_to_scan += extra_chains

    print(f"\n🔍 将扫描的链: {chains_to_scan}")

    total_found = 0
    total_recovered = 0.0
    all_txs = []

    for chain in chains_to_scan:
        print(f"\n{'─'*50}")
        print(f"扫描链: {chain}")
        try:
            result = scan_and_recover(
                mnemonic=mnemonic,
                num_hops=num_hops,
                destination=args.destination,
                chain=chain,
                dry_run=args.dry_run
            )
            total_found += result['found']
            total_recovered += result['recovered']
            all_txs.extend(result['txs'])
        except Exception as e:
            print(f"  ⚠️ 扫描 {chain} 失败: {e}")

    print(f"\n{'='*60}")
    print(f"恢复完成")
    print(f"  发现有余额地址: {total_found}")
    print(f"  {'预计' if args.dry_run else '已'}归集金额: {total_recovered:.8f}")
    print(f"  交易数: {len(all_txs)}")
    if all_txs:
        print(f"\n交易列表:")
        for tx in all_txs:
            print(f"  {tx['address'][:10]}... → {tx['amount']:.8f}  {tx['tx_hash'][:16]}...")


if __name__ == '__main__':
    main()
