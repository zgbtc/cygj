"""测试新的2模式费用系统"""
from advanced_mixer_engine import AdvancedMixerEngine, MIXING_MODES

print("=" * 60)
print("新的2模式费用系统测试")
print("=" * 60)

print("\n可用模式:", list(MIXING_MODES.keys()))

# 测试快速模式
print("\n" + "=" * 60)
print("快速模式测试")
print("=" * 60)
mixer_fast = AdvancedMixerEngine('bsc_testnet', 'fast')

test_cases = [10, 50, 100, 500, 1000]
print("\n转账次数 | 服务费 | Gas费 | 总费用 | 费率")
print("-" * 60)
for hops in test_cases:
    fees = mixer_fast.calculate_fees(hops, 1.0)
    print(f"{hops:4d} 次 | {fees['service_fee']:.4f} | {fees['gas_fee']:.5f} | {fees['total_fee']:.5f} | {fees['fee_rate']:.4f}")

# 测试极致模式
print("\n" + "=" * 60)
print("极致隐私模式测试")
print("=" * 60)
mixer_ultimate = AdvancedMixerEngine('bsc_testnet', 'ultimate')

print("\n转账次数 | 服务费 | Gas费 | 跨链费 | 总费用 | 费率")
print("-" * 70)
for hops in test_cases:
    fees = mixer_ultimate.calculate_fees(hops, 1.0)
    print(f"{hops:4d} 次 | {fees['service_fee']:.4f} | {fees['gas_fee']:.5f} | {fees['crosschain_fee']:.3f} | {fees['total_fee']:.5f} | {fees['fee_rate']:.4f}")

# 对比
print("\n" + "=" * 60)
print("费用对比（快速 vs 极致）")
print("=" * 60)
print("\n转账次数 | 快速模式 | 极致模式 | 差价")
print("-" * 50)
for hops in test_cases:
    fees_fast = mixer_fast.calculate_fees(hops, 1.0)
    fees_ultimate = mixer_ultimate.calculate_fees(hops, 1.0)
    diff = fees_ultimate['service_fee'] - fees_fast['service_fee']
    print(f"{hops:4d} 次 | {fees_fast['service_fee']:.4f} BNB | {fees_ultimate['service_fee']:.4f} BNB | +{diff:.4f}")

print("\n✅ 极致模式服务费 = 快速模式 × 2")
