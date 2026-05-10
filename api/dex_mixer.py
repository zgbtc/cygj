"""
Ultimate Privacy - 跨链 + DEX Swap 混币引擎
POST /api/dex_mixer

流程（每笔）：
  BSC BNB → [LiFi swap+bridge] → Arbitrum/Polygon/Base USDC → [LiFi swap+bridge] → BSC BNB → target

actions:
  plan      - 规划金额拆分和中继路径
  quote     - 代理 LiFi quote 请求
  status    - 查询 LiFi 跨链状态

优势：
  ✅ 无第三方托管（LiFi 是去中心化聚合器）
  ✅ 无 KYC 风险
  ✅ 2-3 分钟完成
  ✅ 三维混淆：币种 + 链 + 地址
  ✅ 大额自动拆分（金额打碎）
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import random
import hashlib
import time
import traceback
import logging

sys.path.insert(0, os.path.dirname(__file__))
logger = logging.getLogger(__name__)

LIFI_API = "https://li.quest/v1"

# 中继链候选（从源链 BSC 出发的可选中继）
# 选流动性最好的 4 条链
RELAY_CHAINS = [
    {'id': 'arbitrum', 'chain_id': 42161, 'native': 'ETH',  'stable': 'USDC',
     'usdc_addr': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831'},
    {'id': 'polygon',  'chain_id': 137,    'native': 'MATIC', 'stable': 'USDC',
     'usdc_addr': '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359'},
    {'id': 'base',     'chain_id': 8453,   'native': 'ETH',  'stable': 'USDC',
     'usdc_addr': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'},
    {'id': 'optimism', 'chain_id': 10,     'native': 'ETH',  'stable': 'USDC',
     'usdc_addr': '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85'},
]

BSC_CHAIN_ID = 56
NATIVE_TOKEN = '0x0000000000000000000000000000000000000000'  # LiFi 用 0x0 表示原生代币

# 服务费收款地址
FEE_ADDRESS = '0xe602348170bc045c588bf1638b0edc592f767250'

# Ultimate Privacy 阶梯费率
def get_fee_rate(amount_bnb: float) -> float:
    """根据金额返回费率（小数形式）"""
    if amount_bnb < 1:
        return 0.039
    elif amount_bnb < 10:
        return 0.029
    elif amount_bnb < 100:
        return 0.019
    else:
        return 0.009


# ─── 金额拆分 ──────────────────────────────────────────────────────────────

def split_amount(total: float) -> list:
    """
    根据金额自动决定拆分数量。
    返回每笔金额列表，总和 = total。

    规则：
      ≤ 5 BNB   → 1 笔
      5–25      → 2 笔
      25–100    → 3 笔
      100–500   → 4 笔
      > 500     → 5 笔
    """
    if total <= 5:
        return [total]
    elif total <= 25:
        n = 2
    elif total <= 100:
        n = 3
    elif total <= 500:
        n = 4
    else:
        n = 5

    # 按随机权重拆分
    weights = [random.uniform(0.7, 1.3) for _ in range(n)]
    s = sum(weights)
    parts = [round(total * w / s, 6) for w in weights]
    diff = round(total - sum(parts), 6)
    parts[-1] = round(parts[-1] + diff, 6)
    return parts


def build_plan(from_address: str, to_address: str, total_amount: float) -> dict:
    """构建完整的混币计划。"""
    # 计算服务费
    fee_rate = get_fee_rate(total_amount)
    service_fee = round(total_amount * fee_rate, 8)
    net_amount = round(total_amount - service_fee, 8)

    if net_amount <= 0.001:
        raise ValueError(f"金额过小：扣除服务费 {service_fee} 后不足 0.001 BNB")

    amounts = split_amount(net_amount)
    legs = []

    for i, amt in enumerate(amounts):
        # 每笔随机选中继链（尽量不同）
        relay = random.choice(RELAY_CHAINS)
        # 每笔之间随机延迟 0–30 秒（第一笔无延迟）
        delay_seconds = 0 if i == 0 else random.randint(5, 30)

        legs.append({
            'leg_idx': i,
            'amount_bnb': amt,
            'relay_chain': relay['id'],
            'relay_chain_id': relay['chain_id'],
            'relay_stable': relay['stable'],
            'relay_stable_addr': relay['usdc_addr'],
            'delay_seconds': delay_seconds,
            'status': 'pending',
        })

    route_id = hashlib.sha256(
        f"{from_address}{to_address}{total_amount}{time.time()}".encode()
    ).hexdigest()[:12]

    return {
        'route_id': route_id,
        'from_address': from_address,
        'to_address': to_address,
        'total_amount': total_amount,
        'service_fee': service_fee,
        'fee_rate': fee_rate,
        'fee_rate_percent': round(fee_rate * 100, 1),
        'fee_address': FEE_ADDRESS,
        'net_amount': net_amount,
        'num_legs': len(amounts),
        'legs': legs,
        'created_at': int(time.time()),
    }


# ─── LiFi Quote 代理 ──────────────────────────────────────────────────────────

def lifi_quote(from_chain: int, to_chain: int,
               from_token: str, to_token: str,
               from_amount: str, from_address: str, to_address: str,
               slippage: float = 0.03) -> dict:
    """
    向 LiFi 请求跨链+swap 报价。
    from_amount: 单位是 wei (字符串)
    """
    import requests
    params = {
        'fromChain': from_chain,
        'toChain': to_chain,
        'fromToken': from_token,
        'toToken': to_token,
        'fromAmount': from_amount,
        'fromAddress': from_address,
        'toAddress': to_address,
        'slippage': slippage,
        'order': 'FASTEST',  # 优先最快路由
    }
    resp = requests.get(f"{LIFI_API}/quote", params=params, timeout=20)
    if resp.status_code != 200:
        raise Exception(f"LiFi quote 失败 ({resp.status_code}): {resp.text[:300]}")
    return resp.json()


def lifi_status(tx_hash: str, from_chain: int, to_chain: int) -> dict:
    """查询 LiFi 跨链状态"""
    import requests
    params = {
        'txHash': tx_hash,
        'fromChain': from_chain,
        'toChain': to_chain,
    }
    resp = requests.get(f"{LIFI_API}/status", params=params, timeout=10)
    if resp.status_code != 200:
        return {'status': 'PENDING', 'raw': resp.text[:200]}
    return resp.json()


# ─── HTTP Handler ──────────────────────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length)) if content_length else {}
            action = data.get('action', 'plan')

            if action == 'plan':
                from_address = data.get('from_address', '')
                to_address = data.get('to_address', '')
                total_amount = float(data.get('total_amount', 0))

                if not to_address or total_amount <= 0:
                    return self._send(400, {'success': False, 'error': '缺少 to_address 或 total_amount'})
                if total_amount < 0.005:
                    return self._send(400, {'success': False, 'error': '金额过小：最少 0.005 BNB'})

                plan = build_plan(from_address, to_address, total_amount)

                # 存 Supabase（可选）
                try:
                    from db import save_session, DB_ENABLED
                    if DB_ENABLED:
                        # 构造兼容 save_session 的 plan 结构
                        compat = {
                            'plan_id': plan['route_id'],
                            'mode': 'ultimate',
                            'chain': 'bsc',
                            'relay_chain': ','.join(sorted(set(l['relay_chain'] for l in plan['legs']))),
                            'from_address': from_address,
                            'to_address': to_address,
                            'total_amount': total_amount,
                            'num_hops': len(plan['legs']) * 2,  # 每笔 2 跳
                            'total_steps': len(plan['legs']) * 2,
                            'fees': {'estimated': '1-2%'},
                            'intermediate_keys': [],
                            'mnemonic': None,
                        }
                        save_session(compat)
                except Exception as e:
                    logger.warning(f"DB save failed: {e}")

                return self._send(200, {'success': True, 'route': plan})

            elif action == 'quote':
                # 代理 LiFi quote
                from_chain = int(data.get('from_chain', 0))
                to_chain = int(data.get('to_chain', 0))
                from_token = data.get('from_token', NATIVE_TOKEN)
                to_token = data.get('to_token', NATIVE_TOKEN)
                from_amount = str(data.get('from_amount', '0'))
                from_address = data.get('from_address', '')
                to_address = data.get('to_address', '')
                slippage = float(data.get('slippage', 0.03))

                if not all([from_chain, to_chain, from_amount, from_address, to_address]):
                    return self._send(400, {'success': False, 'error': '缺少 quote 参数'})

                quote = lifi_quote(
                    from_chain, to_chain, from_token, to_token,
                    from_amount, from_address, to_address, slippage
                )
                return self._send(200, {'success': True, 'quote': quote})

            elif action == 'status':
                tx_hash = data.get('tx_hash', '')
                from_chain = int(data.get('from_chain', 0))
                to_chain = int(data.get('to_chain', 0))
                if not all([tx_hash, from_chain, to_chain]):
                    return self._send(400, {'success': False, 'error': '缺少 status 参数'})
                status = lifi_status(tx_hash, from_chain, to_chain)
                return self._send(200, {'success': True, **status})

            elif action == 'config':
                # 返回支持的中继链配置
                return self._send(200, {
                    'success': True,
                    'bsc_chain_id': BSC_CHAIN_ID,
                    'relay_chains': RELAY_CHAINS,
                    'native_token': NATIVE_TOKEN,
                })

            else:
                return self._send(400, {'success': False, 'error': f'未知 action: {action}'})

        except Exception as e:
            return self._send(500, {
                'success': False,
                'error': f'{type(e).__name__}: {str(e)}',
                'trace': traceback.format_exc()
            })

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send(self, status: int, body: dict):
        payload = json.dumps(body, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
