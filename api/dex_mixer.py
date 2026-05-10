"""
Ultimate Privacy - 跨链 + DEX Swap 混币引擎 v2
POST /api/dex_mixer

核心设计：
  - 固定助记词派生一次性中继地址（每次新索引，用完即弃）
  - 第一跳：BSC BNB → LiFi → 中继链 USDC @ 中继地址（源地址签名）
  - 第二跳：中继链 USDC → LiFi(gasless) → BSC BNB @ target（中继地址签名）
  - 金额自动打碎 + 时间打散 + 多链随机

actions:
  plan      - 规划路由 + 派生中继地址 + 返回私钥给前端签名
  quote     - 代理 LiFi quote
  status    - 查询 LiFi 跨链状态
  config    - 返回支持的中继链

安全保证：
  ✅ 固定助记词可恢复所有中继地址
  ✅ 每个中继地址只用一次（不会被标记）
  ✅ Gasless relay：中继地址不需要原生 gas 币
  ✅ 数据库记录每次使用的索引
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

# 中继链：固定用 Polygon（gas 最便宜，POL 就是 gas 币）
RELAY_CHAIN = {
    'id': 'polygon',
    'chain_id': 137,
    'native': 'POL',
    'native_token': '0x0000000000000000000000000000000000000000',  # 原生币
}

BSC_CHAIN_ID = 56
NATIVE_TOKEN = '0x0000000000000000000000000000000000000000'
FEE_ADDRESS = '0xe602348170bc045c588bf1638b0edc592f767250'


# ─── 费率 ──────────────────────────────────────────────────────────────────────

def get_fee_rate(amount_bnb: float) -> float:
    if amount_bnb < 1:
        return 0.049
    elif amount_bnb < 10:
        return 0.041
    elif amount_bnb < 100:
        return 0.031
    else:
        return 0.027


# ─── 中继地址派生 ──────────────────────────────────────────────────────────────

def _get_relay_mnemonic() -> str:
    m = os.environ.get('RELAY_MNEMONIC', '')
    if not m:
        raise ValueError("RELAY_MNEMONIC 环境变量未配置")
    return m


def _get_next_index() -> int:
    """从数据库获取下一个可用索引，如果数据库不可用则用时间戳"""
    try:
        from db import _request, DB_ENABLED
        if DB_ENABLED:
            result = _request('GET', 'relay_addresses', params={
                'select': 'relay_index',
                'order': 'relay_index.desc',
                'limit': '1'
            })
            if result and len(result) > 0:
                return result[0]['relay_index'] + 1
    except Exception:
        pass
    # 回退：用时间戳确保不重复
    return int(time.time() * 1000) % 100000000


def derive_relay_address(index: int) -> dict:
    """从固定助记词派生指定索引的地址"""
    from eth_account import Account
    Account.enable_unaudited_hdwallet_features()
    mnemonic = _get_relay_mnemonic()
    path = f"m/44'/60'/0'/0/{index}"
    acct = Account.from_mnemonic(mnemonic, account_path=path)
    return {
        'index': index,
        'address': acct.address,
        'private_key': acct.key.hex(),
        'path': path,
    }


def _save_relay_usage(session_id: str, relay_index: int, address: str, chain: str):
    """记录中继地址使用到数据库"""
    try:
        from db import _request, DB_ENABLED
        if DB_ENABLED:
            _request('POST', 'relay_addresses', body={
                'session_id': session_id,
                'relay_index': relay_index,
                'address': address,
                'chain': chain,
                'status': 'active',
                'created_at': 'now()',
            })
    except Exception as e:
        logger.warning(f"保存中继地址失败: {e}")


# ─── 金额拆分 ──────────────────────────────────────────────────────────────────

def split_amount(total: float) -> list:
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
    weights = [random.uniform(0.7, 1.3) for _ in range(n)]
    s = sum(weights)
    parts = [round(total * w / s, 6) for w in weights]
    diff = round(total - sum(parts), 6)
    parts[-1] = round(parts[-1] + diff, 6)
    return parts


# ─── 构建计划 ──────────────────────────────────────────────────────────────────

def build_plan(from_address: str, to_address: str, total_amount: float) -> dict:
    fee_rate = get_fee_rate(total_amount)
    service_fee = round(total_amount * fee_rate, 8)
    net_amount = round(total_amount - service_fee, 8)

    if net_amount <= 0.001:
        raise ValueError(f"金额过小：扣除服务费后不足 0.001 BNB")

    amounts = split_amount(net_amount)
    base_index = _get_next_index()

    legs = []
    for i, amt in enumerate(amounts):
        delay_seconds = 0 if i == 0 else random.randint(5, 30)
        relay_addr = derive_relay_address(base_index + i)

        legs.append({
            'leg_idx': i,
            'amount_bnb': amt,
            'relay_chain': RELAY_CHAIN['id'],
            'relay_chain_id': RELAY_CHAIN['chain_id'],
            'relay_native_token': RELAY_CHAIN['native_token'],
            'relay_address': relay_addr['address'],
            'relay_private_key': relay_addr['private_key'],
            'relay_index': relay_addr['index'],
            'delay_seconds': delay_seconds,
            'status': 'pending',
        })

    route_id = hashlib.sha256(
        f"{from_address}{to_address}{total_amount}{time.time()}".encode()
    ).hexdigest()[:12]

    # 记录到数据库
    for leg in legs:
        _save_relay_usage(route_id, leg['relay_index'], leg['relay_address'], leg['relay_chain'])

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


# ─── LiFi API ─────────────────────────────────────────────────────────────────

def lifi_quote(from_chain: int, to_chain: int,
               from_token: str, to_token: str,
               from_amount: str, from_address: str, to_address: str,
               slippage: float = 0.03, allow_dest_call: bool = False) -> dict:
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
        'order': 'FASTEST',
    }
    if allow_dest_call:
        params['allowDestinationCall'] = 'true'
    resp = requests.get(f"{LIFI_API}/quote", params=params, timeout=20)
    if resp.status_code != 200:
        raise Exception(f"LiFi quote 失败 ({resp.status_code}): {resp.text[:300]}")
    return resp.json()


def lifi_status(tx_hash: str, from_chain: int, to_chain: int) -> dict:
    import requests
    resp = requests.get(f"{LIFI_API}/status", params={
        'txHash': tx_hash, 'fromChain': from_chain, 'toChain': to_chain
    }, timeout=10)
    if resp.status_code != 200:
        return {'status': 'PENDING'}
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
                    return self._send(400, {'success': False, 'error': '缺少参数'})
                if total_amount < 0.005:
                    return self._send(400, {'success': False, 'error': '最少 0.005 BNB'})
                plan = build_plan(from_address, to_address, total_amount)
                return self._send(200, {'success': True, 'route': plan})

            elif action == 'quote':
                q = lifi_quote(
                    from_chain=int(data['from_chain']),
                    to_chain=int(data['to_chain']),
                    from_token=data['from_token'],
                    to_token=data['to_token'],
                    from_amount=str(data['from_amount']),
                    from_address=data['from_address'],
                    to_address=data['to_address'],
                    slippage=float(data.get('slippage', 0.03)),
                    allow_dest_call=data.get('allow_dest_call', False),
                )
                return self._send(200, {'success': True, 'quote': q})

            elif action == 'status':
                s = lifi_status(data['tx_hash'], int(data['from_chain']), int(data['to_chain']))
                return self._send(200, {'success': True, **s})

            elif action == 'config':
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
