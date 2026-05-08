"""测试高级混币引擎"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from advanced_mixer_engine import AdvancedMixerEngine, MIXING_MODES
from crosschain_bridge import CrossChainBridge

def test_modes():
    """测试混币模式"""
    print("=" * 60)
    print("测试混币模式")
    print("=" * 60)
    
    for mode, config in MIXING_MODES.items():
        print(f"\n{mode}:")
        print(f"  名称: {config['name']}")
        print(f"  隐私等级: {config['privacy_level']}")
        print(f"  预计时间: {config['estimated_time']}")
        print(f"  延迟范围: {config['delay_range']}")
        print(f"  跨链: {'是' if config['use_crosschain'] else '否'}")
        print(f"  Tor: {'是' if config['use_tor'] else '否'}")

def test_crosschain_bridge():
    """测试跨链桥接"""
    print("\n" + "=" * 60)
    print("测试跨链桥接引擎")
    print("=" * 60)
    
    try:
        bridge = CrossChainBridge(use_tor=False)
        print(f"\n✅ 跨链桥接引擎初始化成功")
        print(f"可用链: {list(bridge.chains.keys())}")
        
        # 生成跨链路径
        if 'bsc_testnet' in bridge.chains:
            path = bridge.multi_chain_mixing_path('bsc_testnet', 100)
            print(f"\n跨链混币路径 (100 跳):")
            for i, step in enumerate(path):
                print(f"  {i+1}. {step}")
        
    except Exception as e:
        print(f"\n❌ 跨链桥接引擎初始化失败: {e}")

def test_mixer_engine():
    """测试混币引擎"""
    print("\n" + "=" * 60)
    print("测试混币引擎")
    print("=" * 60)
    
    for mode in ['fast', 'privacy', 'ultimate']:
        print(f"\n测试 {mode} 模式:")
        try:
            mixer = AdvancedMixerEngine('bsc_testnet', mode=mode)
            print(f"  ✅ {mode} 模式初始化成功")
            
            # 测试费用计算
            fees = mixer.calculate_fees(100, 0.1)
            print(f"  费用计算:")
            print(f"    总金额: {fees['total_amount']} BNB")
            print(f"    服务费: {fees['service_fee']} BNB")
            print(f"    Gas 费: {fees['gas_fee']} BNB")
            print(f"    跨链费: {fees['crosschain_fee']} BNB")
            print(f"    总费用: {fees['total_fee']} BNB")
            print(f"    净金额: {fees['net_amount']} BNB")
            
            # 测试随机金额生成
            amounts = mixer.generate_random_amounts(1.0, 10, use_round_numbers=True)
            print(f"  随机金额分配 (10份):")
            print(f"    {[f'{a:.4f}' for a in amounts]}")
            print(f"    总和: {sum(amounts):.4f}")
            
        except Exception as e:
            print(f"  ❌ {mode} 模式初始化失败: {e}")

def test_tor_connection():
    """测试 Tor 连接"""
    print("\n" + "=" * 60)
    print("测试 Tor 连接")
    print("=" * 60)
    
    try:
        import requests
        
        # 测试直接连接
        print("\n1. 测试直接连接:")
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        direct_ip = response.json()['ip']
        print(f"   直接 IP: {direct_ip}")
        
        # 测试 Tor 连接
        print("\n2. 测试 Tor 连接:")
        session = requests.Session()
        session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        try:
            response = session.get('https://api.ipify.org?format=json', timeout=10)
            tor_ip = response.json()['ip']
            print(f"   Tor IP: {tor_ip}")
            
            if direct_ip != tor_ip:
                print(f"   ✅ Tor 连接成功！IP 已改变")
            else:
                print(f"   ⚠️ Tor 可能未生效，IP 未改变")
                
        except Exception as e:
            print(f"   ❌ Tor 连接失败: {e}")
            print(f"   提示: 请确保 Tor 已安装并运行在 127.0.0.1:9050")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("高级混币引擎测试套件")
    print("=" * 60)
    
    # 运行所有测试
    test_modes()
    test_crosschain_bridge()
    test_mixer_engine()
    test_tor_connection()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
