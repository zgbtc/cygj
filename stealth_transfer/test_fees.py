"""测试费率"""
from mixer_engine import MixerEngine

engine = MixerEngine('bsc')

print("费率测试（按照 ct.app 标准）:\n")

test_cases = [
    (10, 1.0),
    (50, 1.0),
    (100, 1.0),
    (500, 1.0),
    (1000, 1.0),
]

for num_hops, amount in test_cases:
    fees = engine.calculate_fees(num_hops, amount)
    print(f"{num_hops} 次转账，总金额 {amount} BNB:")
    print(f"  服务费: {fees['service_fee']} BNB")
    print(f"  Gas 费: {fees['gas_fee']} BNB")
    print(f"  总费用: {fees['total_fee']} BNB")
    print(f"  净收入: {fees['net_amount']} BNB")
    print()
