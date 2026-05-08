"""免费代理池管理器 - 自动抓取和验证代理"""
import requests
import random
import time
import logging
import threading
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProxyPool:
    """免费代理池管理器"""
    
    def __init__(self, auto_refresh: bool = True):
        self.proxies = []
        self.last_refresh = 0
        self.refresh_interval = 3600  # 1小时刷新一次
        self.test_url = "https://httpbin.org/ip"
        self.auto_refresh = auto_refresh
        self._refresh_lock = threading.Lock()
        
        # 启动后台自动刷新线程
        if auto_refresh:
            self._start_auto_refresh_thread()
    
    def _start_auto_refresh_thread(self):
        """启动后台自动刷新线程"""
        def refresh_worker():
            while True:
                try:
                    time.sleep(self.refresh_interval)
                    logger.info("后台自动刷新代理池...")
                    self.refresh_proxies(force=True)
                except Exception as e:
                    logger.error(f"后台刷新失败: {e}")
        
        thread = threading.Thread(target=refresh_worker, daemon=True)
        thread.start()
        logger.info("✅ 后台自动刷新线程已启动")
        
    def fetch_free_proxies(self) -> List[str]:
        """从多个源抓取免费代理"""
        all_proxies = []
        
        # 源1: proxy-list.download
        try:
            logger.info("抓取代理源1...")
            url = "https://www.proxy-list.download/api/v1/get?type=http"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                proxies = response.text.strip().split('\r\n')
                all_proxies.extend([f"http://{p}" for p in proxies if p])
                logger.info(f"  获取 {len(proxies)} 个代理")
        except Exception as e:
            logger.error(f"  源1失败: {e}")
        
        # 源2: free-proxy-list.net (需要解析HTML)
        try:
            logger.info("抓取代理源2...")
            url = "https://free-proxy-list.net/"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 简单解析 (实际应该用 BeautifulSoup)
                import re
                pattern = r'(\d+\.\d+\.\d+\.\d+):(\d+)'
                matches = re.findall(pattern, response.text)
                proxies = [f"http://{ip}:{port}" for ip, port in matches[:50]]
                all_proxies.extend(proxies)
                logger.info(f"  获取 {len(proxies)} 个代理")
        except Exception as e:
            logger.error(f"  源2失败: {e}")
        
        # 源3: pubproxy.com API
        try:
            logger.info("抓取代理源3...")
            url = "http://pubproxy.com/api/proxy?limit=20&format=txt&type=http"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                proxies = [f"http://{p.strip()}" for p in response.text.split('\n') if p.strip()]
                all_proxies.extend(proxies)
                logger.info(f"  获取 {len(proxies)} 个代理")
        except Exception as e:
            logger.error(f"  源3失败: {e}")
        
        # 源4: geonode.com API
        try:
            logger.info("抓取代理源4...")
            url = "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                proxies = [f"http://{p['ip']}:{p['port']}" for p in data.get('data', [])]
                all_proxies.extend(proxies)
                logger.info(f"  获取 {len(proxies)} 个代理")
        except Exception as e:
            logger.error(f"  源4失败: {e}")
        
        # 去重
        all_proxies = list(set(all_proxies))
        logger.info(f"总共抓取 {len(all_proxies)} 个代理（去重后）")
        
        return all_proxies
    
    def test_proxy(self, proxy: str, timeout: int = 5) -> Optional[Dict]:
        """测试单个代理是否可用"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            start_time = time.time()
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'proxy': proxy,
                    'response_time': response_time,
                    'working': True
                }
        except Exception:
            pass
        
        return None
    
    def validate_proxies(self, proxies: List[str], max_workers: int = 20) -> List[Dict]:
        """并发验证代理列表"""
        logger.info(f"开始验证 {len(proxies)} 个代理...")
        
        working_proxies = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in proxies
            }
            
            for future in as_completed(future_to_proxy):
                result = future.result()
                if result:
                    working_proxies.append(result)
                    logger.info(f"  ✅ {result['proxy']} ({result['response_time']:.2f}s)")
        
        # 按响应时间排序
        working_proxies.sort(key=lambda x: x['response_time'])
        
        logger.info(f"验证完成：{len(working_proxies)}/{len(proxies)} 可用")
        
        return working_proxies
    
    def refresh_proxies(self, force: bool = False):
        """刷新代理池（线程安全）"""
        with self._refresh_lock:
            current_time = time.time()
            
            # 检查是否需要刷新
            if not force and self.proxies and (current_time - self.last_refresh) < self.refresh_interval:
                logger.info(f"代理池还有 {len(self.proxies)} 个可用代理，无需刷新")
                return
            
            logger.info("=" * 60)
            logger.info("刷新代理池")
            logger.info("=" * 60)
            
            # 抓取代理
            raw_proxies = self.fetch_free_proxies()
            
            if not raw_proxies:
                logger.warning("未能抓取到任何代理")
                return
            
            # 验证代理
            working_proxies = self.validate_proxies(raw_proxies)
            
            if working_proxies:
                self.proxies = working_proxies
                self.last_refresh = current_time
                logger.info(f"✅ 代理池已更新：{len(self.proxies)} 个可用代理")
            else:
                logger.warning("没有可用的代理")
    
    def get_random_proxy(self) -> Optional[str]:
        """获取随机代理"""
        # 自动刷新
        self.refresh_proxies()
        
        if not self.proxies:
            logger.warning("代理池为空")
            return None
        
        # 随机选择
        proxy_info = random.choice(self.proxies)
        return proxy_info['proxy']
    
    def get_best_proxies(self, count: int = 5) -> List[str]:
        """获取最快的N个代理"""
        self.refresh_proxies()
        
        if not self.proxies:
            return []
        
        # 返回响应时间最短的N个
        best = self.proxies[:count]
        return [p['proxy'] for p in best]
    
    def remove_proxy(self, proxy: str):
        """移除失效的代理"""
        self.proxies = [p for p in self.proxies if p['proxy'] != proxy]
        logger.info(f"移除失效代理: {proxy}")


# 全局代理池实例
_proxy_pool = None

def get_proxy_pool() -> ProxyPool:
    """获取全局代理池实例"""
    global _proxy_pool
    if _proxy_pool is None:
        _proxy_pool = ProxyPool()
    return _proxy_pool


if __name__ == '__main__':
    # 测试
    pool = ProxyPool()
    pool.refresh_proxies(force=True)
    
    if pool.proxies:
        print(f"\n最快的5个代理:")
        for p in pool.get_best_proxies(5):
            print(f"  {p}")
        
        print(f"\n随机代理: {pool.get_random_proxy()}")
