"""
XMR 隐私路由引擎
POST /api/xmr_router

流程：
  BNB (源地址) → [服务商 A] → XMR (临时地址)
                → XMR 内部转账 N 跳（可选）
                → [服务商 B] → BNB (target 地址)

金额打碎：自动拆成 2–4 笔，每笔走不同服务商，随机时间间隔。

支持的服务商：
  - ChangeNOW  (需要 API key)
  - SimpleSwap (需要 API key)
  - eXch       (无需 API key，完全匿名)

环境变量：
  CHANGENOW_API_KEY   - ChangeNOW API key
  SIMPLESWAP_API_KEY  - SimpleSwap API key
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import time
import random
import hashlib
import traceback
import logging

sys.path.insert(0, os.path.dirname(__file__))
logger = logging.getLogger(__name__)

# ─── 服务商配置 ────────────────────────────────────────────────────────────────

PROVIDERS = {
    'changenow': {
        'name': 'ChangeNOW',
        'api_key_env': 'CHANGENOW_API_KEY',
        'base_url': 'https://api.changenow.io/v2',
        'min_bnb': 0.005,
    },
    'simpleswap': {
        'name': 'SimpleSwap',
        'api_key_env': 'SIMPLESWAP_API_KEY',
        'base_url': 'https://api.simpleswap.io',
        'min_bnb': 0.005,
    },
    'exch': {
        'name': 'eXch',
        'api_key_env': None,          # 无需 key
        'base_url': 'https://exch.cx/api',
        'min_bnb': 0.002,
    },
}

# ─── 工具函数 ──────────────────────────────────────────────────────────────────

def _get_available_providers() -> list:
    """返回当前环境中可用的服务商列表（有 API key 或不需要 key）"""
    available = []
    for pid, cfg in PROVIDERS.items():
        env = cfg['api_key_env']
        if env is None or os.environ.get(env):
            available.append(pid)
    return available


def _split_amount(total: float, n: int) -> list:
    """
    把 total 拆成 n 份，每份金额随机（不均等），
    最小份 >= 0.002 BNB，总和 = total。
    """
    if n <= 1:
        return [total]
    # 生成 n 个随机权重
    weights = [random.uniform(0.6, 1.4) for _ in range(n)]
    s = sum(weights)
    parts = [round(total * w / s, 6) for w in weights]
    # 修正舍入误差
    diff = round(total - sum(parts), 6)
    parts[-1] = round(parts[-1] + diff, 6)
    return parts


def _random_delay(min_s: float = 30, max_s: float = 180) -> float:
    """返回随机延迟秒数（用于打散时间关联）"""
    return random.uniform(min_s, max_s)


# ─── ChangeNOW ────────────────────────────────────────────────────────────────

def changenow_get_min_amount(from_currency: str, to_currency: str, api_key: str) -> float:
    import requests
    resp = requests.get(
        f"https://api.changenow.io/v2/exchange/min-amount",
        params={'fromCurrency': from_currency, 'toCurrency': to_currency,
                'fromNetwork': 'bsc' if from_currency == 'bnb' else '',
                'toNetwork': 'xmr' if to_currency == 'xmr' else 'bsc'},
        headers={'x-changenow-api-key': api_key},
        timeout=10
    )
    if resp.status_code == 200:
        return float(resp.json().get('minAmount', 0.005))
    return 0.005


def changenow_create_exchange(
    from_currency: str, to_currency: str,
    amount: float, address: str,
    api_key: str,
    from_network: str = 'bsc', to_network: str = ''
) -> dict:
    """创建 ChangeNOW 兑换订单，返回 {id, payinAddress, estimatedAmount}"""
    import requests
    payload = {
        'fromCurrency': from_currency,
        'toCurrency': to_currency,
        'fromNetwork': from_network,
        'toNetwork': to_network,
        'amount': str(amount),
        'address': address,
        'flow': 'standard',
        'type': 'direct',
    }
    resp = requests.post(
        'https://api.changenow.io/v2/exchange',
        json=payload,
        headers={'x-changenow-api-key': api_key, 'Content-Type': 'application/json'},
        timeout=15
    )
    if resp.status_code not in (200, 201):
        raise Exception(f"ChangeNOW 创建订单失败 ({resp.status_code}): {resp.text[:300]}")
    data = resp.json()
    return {
        'provider': 'changenow',
        'order_id': data['id'],
        'payin_address': data['payinAddress'],
        'estimated_amount': float(data.get('toAmount') or data.get('estimatedAmount') or 0),
        'status_url': f"https://api.changenow.io/v2/exchange/by-id?id={data['id']}",
    }


def changenow_get_status(order_id: str, api_key: str) -> dict:
    import requests
    resp = requests.get(
        f"https://api.changenow.io/v2/exchange/by-id",
        params={'id': order_id},
        headers={'x-changenow-api-key': api_key},
        timeout=10
    )
    if resp.status_code == 200:
        d = resp.json()
        return {'status': d.get('status', 'unknown'), 'raw': d}
    return {'status': 'unknown'}


# ─── SimpleSwap ───────────────────────────────────────────────────────────────

def simpleswap_create_exchange(
    from_currency: str, to_currency: str,
    amount: float, address: str,
    api_key: str
) -> dict:
    import requests
    payload = {
        'currency_from': from_currency,
        'currency_to': to_currency,
        'amount': str(amount),
        'address_to': address,
        'fixed': False,
    }
    resp = requests.post(
        f"https://api.simpleswap.io/create_exchange?api_key={api_key}",
        json=payload,
        timeout=15
    )
    if resp.status_code not in (200, 201):
        raise Exception(f"SimpleSwap 创建订单失败 ({resp.status_code}): {resp.text[:300]}")
    data = resp.json()
    return {
        'provider': 'simpleswap',
        'order_id': data['id'],
        'payin_address': data['address_from'],
        'estimated_amount': float(data.get('amount_to') or 0),
        'status_url': f"https://simpleswap.io/exchange?id={data['id']}",
    }


def simpleswap_get_status(order_id: str, api_key: str) -> dict:
    import requests
    resp = requests.get(
        f"https://api.simpleswap.io/get_exchange",
        params={'api_key': api_key, 'id': order_id},
        timeout=10
    )
    if resp.status_code == 200:
        d = resp.json()
        return {'status': d.get('status', 'unknown'), 'raw': d}
    return {'status': 'unknown'}


# ─── eXch ─────────────────────────────────────────────────────────────────────

def exch_create_exchange(
    from_currency: str, to_currency: str,
    amount: float, address: str
) -> dict:
    """
    eXch API：完全匿名，无需 API key。
    from/to 格式：BNB、XMR（大写）
    """
    import requests
    payload = {
        'from_currency': from_currency.upper(),
        'to_currency': to_currency.upper(),
        'to_address': address,
        'amount': str(amount),
        'refund_address': '',
    }
    resp = requests.post(
        'https://exch.cx/api/order',
        json=payload,
        timeout=15
    )
    if resp.status_code not in (200, 201):
        raise Exception(f"eXch 创建订单失败 ({resp.status_code}): {resp.text[:300]}")
    data = resp.json()
    if data.get('error'):
        raise Exception(f"eXch 错误: {data['error']}")
    return {
        'provider': 'exch',
        'order_id': data.get('orderid') or data.get('id', ''),
        'payin_address': data.get('from_address') or data.get('deposit_address', ''),
        'estimated_amount': float(data.get('to_amount') or data.get('amount_to') or 0),
        'status_url': f"https://exch.cx/order/{data.get('orderid', '')}",
    }


def exch_get_status(order_id: str) -> dict:
    import requests
    resp = requests.get(
        f"https://exch.cx/api/order/{order_id}",
        timeout=10
    )
    if resp.status_code == 200:
        d = resp.json()
        return {'status': d.get('status', 'unknown'), 'raw': d}
    return {'status': 'unknown'}


# ─── 统一创建接口 ──────────────────────────────────────────────────────────────

def create_exchange(
    provider_id: str,
    from_currency: str, to_currency: str,
    amount: float, address: str,
    from_network: str = 'bsc', to_network: str = ''
) -> dict:
    cfg = PROVIDERS[provider_id]
    api_key = os.environ.get(cfg['api_key_env']) if cfg['api_key_env'] else None

    if provider_id == 'changenow':
        return changenow_create_exchange(
            from_currency, to_currency, amount, address, api_key,
            from_network=from_network, to_network=to_network
        )
    elif provider_id == 'simpleswap':
        return simpleswap_create_exchange(from_currency, to_currency, amount, address, api_key)
    elif provider_id == 'exch':
        return exch_create_exchange(from_currency, to_currency, amount, address)
    else:
        raise ValueError(f"未知服务商: {provider_id}")


def get_order_status(provider_id: str, order_id: str) -> dict:
    cfg = PROVIDERS[provider_id]
    api_key = os.environ.get(cfg['api_key_env']) if cfg['api_key_env'] else None

    if provider_id == 'changenow':
        return changenow_get_status(order_id, api_key)
    elif provider_id == 'simpleswap':
        return simpleswap_get_status(order_id, api_key)
    elif provider_id == 'exch':
        return exch_get_status(order_id)
    return {'status': 'unknown'}


# ─── 核心路由逻辑 ──────────────────────────────────────────────────────────────

def build_xmr_route(
    from_address: str,
    to_address: str,
    total_amount: float,
    num_splits: int = 0,       # 0 = 自动决定
    xmr_hops: int = 1,         # XMR 内部跳数（暂时保留，后续实现）
) -> dict:
    """
    构建 XMR 路由计划，返回每笔子订单的详情。
    不实际发起交易，只规划。
    """
    available = _get_available_providers()
    if not available:
        raise ValueError("没有可用的交换服务商，请配置 CHANGENOW_API_KEY 或 SIMPLESWAP_API_KEY")

    # 自动决定拆分数量
    if num_splits <= 0:
        if total_amount < 0.05:
            num_splits = 2
        elif total_amount < 0.5:
            num_splits = 3
        else:
            num_splits = 4

    amounts = _split_amount(total_amount, num_splits)

    # 为每笔分配服务商（尽量不重复）
    legs = []
    for i, amt in enumerate(amounts):
        # 入腿：BNB → XMR，随机选服务商
        in_provider = random.choice(available)
        # 出腿：XMR → BNB，选不同的服务商（如果可能）
        out_candidates = [p for p in available if p != in_provider] or available
        out_provider = random.choice(out_candidates)

        # 随机延迟（打散时间关联）
        delay_seconds = 0 if i == 0 else int(_random_delay(60, 300))

        legs.append({
            'leg_idx': i,
            'amount_bnb': amt,
            'in_provider': in_provider,
            'out_provider': out_provider,
            'delay_seconds': delay_seconds,
            'status': 'pending',
            'in_order': None,
            'out_order': None,
        })

    route_id = hashlib.sha256(
        f"{from_address}{to_address}{total_amount}{time.time()}".encode()
    ).hexdigest()[:12]

    return {
        'route_id': route_id,
        'from_address': from_address,
        'to_address': to_address,
        'total_amount': total_amount,
        'num_splits': num_splits,
        'xmr_hops': xmr_hops,
        'legs': legs,
        'available_providers': available,
        'created_at': int(time.time()),
    }


# ─── HTTP Handler ──────────────────────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length)) if content_length else {}

            action = data.get('action', 'plan')

            if action == 'plan':
                # 只规划，不执行
                from_address = data.get('from_address', '')
                to_address = data.get('to_address', '')
                total_amount = float(data.get('total_amount', 0))
                num_splits = int(data.get('num_splits', 0))

                if not to_address or total_amount <= 0:
                    return self._send(400, {'success': False, 'error': '缺少 to_address 或 total_amount'})

                route = build_xmr_route(
                    from_address=from_address,
                    to_address=to_address,
                    total_amount=total_amount,
                    num_splits=num_splits,
                )
                return self._send(200, {'success': True, 'route': route})

            elif action == 'create_leg':
                # 创建单条腿的交换订单
                provider_id = data.get('provider_id')
                from_currency = data.get('from_currency', 'bnb')
                to_currency = data.get('to_currency', 'xmr')
                amount = float(data.get('amount', 0))
                address = data.get('address', '')
                from_network = data.get('from_network', 'bsc')
                to_network = data.get('to_network', '')

                if not provider_id or not address or amount <= 0:
                    return self._send(400, {'success': False, 'error': '缺少必要参数'})

                order = create_exchange(
                    provider_id=provider_id,
                    from_currency=from_currency,
                    to_currency=to_currency,
                    amount=amount,
                    address=address,
                    from_network=from_network,
                    to_network=to_network,
                )
                return self._send(200, {'success': True, 'order': order})

            elif action == 'status':
                # 查询订单状态
                provider_id = data.get('provider_id')
                order_id = data.get('order_id')
                if not provider_id or not order_id:
                    return self._send(400, {'success': False, 'error': '缺少 provider_id 或 order_id'})
                status = get_order_status(provider_id, order_id)
                return self._send(200, {'success': True, **status})

            elif action == 'providers':
                # 返回可用服务商列表
                available = _get_available_providers()
                return self._send(200, {
                    'success': True,
                    'available': available,
                    'all': list(PROVIDERS.keys()),
                    'details': {
                        pid: {
                            'name': cfg['name'],
                            'needs_key': cfg['api_key_env'] is not None,
                            'configured': bool(
                                cfg['api_key_env'] is None or
                                os.environ.get(cfg['api_key_env'])
                            ),
                            'min_bnb': cfg['min_bnb'],
                        }
                        for pid, cfg in PROVIDERS.items()
                    }
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
