"""检查余额"""
from mixer_engine import MixerEngine
from hd_wallet import HDWallet

mnemonic = "decline cluster album give brief scrap apart onion dust donor figure primary"
wallet = HDWallet(mnemonic)
engine = MixerEngine('bsc_testnet')

print("检查各地址余额:\n")

for i in range(15):
    account = wallet.get_account(i)
    balance = engine.transfer_engine.get_balance(account['address'])
    if balance > 0:
        print(f"[{i:2d}] {account['address']}: {balance} tBNB")

print("\n服务费地址:")
from mixer_engine import FEE_CONFIG
fee_balance = engine.transfer_engine.get_balance(FEE_CONFIG['fee_address'])
print(f"{FEE_CONFIG['fee_address']}: {fee_balance} tBNB")
