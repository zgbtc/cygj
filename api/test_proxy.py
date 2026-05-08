"""测试代理池功能"""
from proxy_pool import ProxyPool

def test_proxy_pool():
    print("=" * 60)
    print("测试代理池")
    print("=" * 60)
    
    # 创建代理池
    pool = ProxyPool()
    
    # 强制刷新
    pool.refresh_proxies(force=True)
    
    if pool.proxies:
        print(f"\n✅ 成功获取 {len(pool.proxies)} 个可用代理")
        
        print(f"\n最快的5个代理:")
        for p in pool.get_best_proxies(5):
            print(f"  {p}")
        
        print(f"\n随机代理测试:")
        for i in range(3):
            proxy = pool.get_random_proxy()
            print(f"  {i+1}. {proxy}")
    else:
        print("\n❌ 未能获取可用代理")

if __name__ == '__main__':
    test_proxy_pool()
