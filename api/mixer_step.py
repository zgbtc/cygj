"""
隐私转账单步执行器
POST /api/mixer_step
输入: { plan, step_idx }
输出: { success, tx_hash, next_idx, done }

特点：
- 无状态，plan 由前端持有
- 每次只执行 1 步（同链发送 或 LiFi 跨链），耗时 < 30 秒
- 跨链时等待到达目标链（或返回 pending，让前端继续 poll）
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback
import time

sys.path.insert(0, os.path.dirname(__file__))

STEP_READY = False
IMPORT_ERROR = None

try:
    from web3 import Web3
    from eth_account import Account
    from config import CHAINS
    STEP_READY = True
except Exception as e:
    IMPORT_ERROR = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"


# LiFi API
LIFI_API = "https://li.quest/v1"

CHAIN_ID_MAP = {
    'bsc': 56,
    'polygon': 137,
    'arbitrum': 42161,
    'optimism': 10,
    'avalanche': 43114,
    'base': 8453,
    'ethereum': 1,
    'bsc_testnet': 97
}

# 各链原生代币 gas 预留（ether 单位）
GAS_RESERVE = {
    'bsc': 0.00015,
    'polygon': 0.02,      # POL gas 很便宜但为 buffer 多留点
    'arbitrum': 0.0001,   # ETH L2
    'optimism': 0.0001,
    'base': 0.0001,
    'avalanche': 0.003,
    'ethereum': 0.002,
    'bsc_testnet': 0.00015
}


def connect_chain(chain: str):
    """并发选最快的 RPC 连接指定链"""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    chain_cfg = CHAINS.get(chain)
    # 如果是 relay chain（polygon/arbitrum 等），用 lifi_bridge 里的 RPC
    if not chain_cfg:
        # fallback RPC（同 lifi_bridge）
        fallback_rpcs = {
            'polygon': ['https://polygon-rpc.com', 'https://polygon.llamarpc.com', 'https://polygon.drpc.org'],
            'arbitrum': ['https://arb1.arbitrum.io/rpc', 'https://arbitrum.llamarpc.com', 'https://arbitrum.drpc.org'],
            'optimism': ['https://mainnet.optimism.io', 'https://optimism.llamarpc.com'],
            'base': ['https://mainnet.base.org', 'https://base.llamarpc.com'],
            'avalanche': ['https://api.avax.network/ext/bc/C/rpc'],
            'ethereum': ['https://eth.llamarpc.com', 'https://ethereum.publicnode.com']
        }
        rpc_urls = fallback_rpcs.get(chain, [])
    else:
        rpc_urls = chain_cfg.get('rpc_urls') or [chain_cfg.get('rpc_url')]
        rpc_urls = [u for u in rpc_urls if u]

    if not rpc_urls:
        raise ConnectionError(f"未配置 {chain} 的 RPC")

    def try_rpc(url):
        try:
            w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 3}))
            _ = w3.eth.block_number
            return (url, w3)
        except Exception:
            return (url, None)

    with ThreadPoolExecutor(max_workers=min(6, len(rpc_urls))) as executor:
        futures = {executor.submit(try_rpc, url): url for url in rpc_urls}
        for future in as_completed(futures, timeout=10):
            try:
                url, w3 = future.result()
                if w3 is not None:
                    for f in futures:
                        if f is not future:
                            f.cancel()
                    return w3
            except Exception:
                continue

    raise ConnectionError(f"所有 {chain} RPC 不可用")


def get_private_key(plan: dict, key_idx: int) -> str:
    """根据 key_idx 找到对应的私钥"""
    if key_idx == -1:
        return plan['from_private_key']
    return plan['intermediate_keys'][key_idx]['private_key']


def execute_send(plan: dict, step: dict) -> dict:
    """执行同链发送"""
    chain = step['chain']
    w3 = connect_chain(chain)
    chain_id = CHAIN_ID_MAP.get(chain, 56)

    pk = get_private_key(plan, step['from_key_idx'])
    account = Account.from_key(pk)
    from_address = account.address
    to_address = Web3.to_checksum_address(step['to_address'])

    # 计算金额
    balance_wei = w3.eth.get_balance(from_address)
    balance = float(w3.from_wei(balance_wei, 'ether'))
    gas_reserve = GAS_RESERVE.get(chain, 0.0002)

    if step['amount'] == 'max':
        amount = balance - gas_reserve
    else:
        amount = float(step['amount'])

    if amount <= 0:
        raise ValueError(
            f"余额不足：当前 {balance:.8f}, 需预留 gas {gas_reserve}, 可用 {amount}"
        )

    amount_wei = w3.to_wei(amount, 'ether')

    # Gas price
    try:
        gas_price = w3.eth.gas_price
    except Exception:
        gas_price = w3.to_wei(5, 'gwei')

    nonce = w3.eth.get_transaction_count(from_address, 'pending')
    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': amount_wei,
        'gas': 21000,
        'gasPrice': gas_price,
        'chainId': chain_id
    }

    signed = w3.eth.account.sign_transaction(tx, pk)
    raw = getattr(signed, 'rawTransaction', None) or getattr(signed, 'raw_transaction', None)
    tx_hash = w3.eth.send_raw_transaction(raw)

    return {
        'tx_hash': tx_hash.hex(),
        'from': from_address,
        'to': to_address,
        'amount': amount,
        'chain': chain,
        'type': 'send',
        'explorer': explorer_url(chain, tx_hash.hex())
    }


def execute_bridge(plan: dict, step: dict, poll_timeout: int = 35) -> dict:
    """执行 LiFi 跨链（发起交易 + 短时间轮询）"""
    import requests

    from_chain = step['from_chain']
    to_chain = step['to_chain']
    w3_from = connect_chain(from_chain)

    pk = get_private_key(plan, step['from_key_idx'])
    account = Account.from_key(pk)
    from_address = account.address
    to_address = Web3.to_checksum_address(step['to_address'])

    balance_wei = w3_from.eth.get_balance(from_address)
    balance = float(w3_from.from_wei(balance_wei, 'ether'))
    gas_reserve = GAS_RESERVE.get(from_chain, 0.0002) * 3  # 跨链 gas 更高

    if step['amount'] == 'max':
        amount = balance - gas_reserve
    else:
        amount = float(step['amount'])

    if amount <= 0:
        raise ValueError(
            f"余额不足：{balance:.8f}, 预留 gas {gas_reserve}, 可用 {amount}"
        )

    amount_wei = w3_from.to_wei(amount, 'ether')

    # 1. 获取 LiFi 报价
    quote_params = {
        'fromChain': CHAIN_ID_MAP[from_chain],
        'toChain': CHAIN_ID_MAP[to_chain],
        'fromToken': '0x0000000000000000000000000000000000000000',
        'toToken': '0x0000000000000000000000000000000000000000',
        'fromAmount': str(amount_wei),
        'fromAddress': from_address,
        'toAddress': to_address,
        'slippage': 0.03,
        'allowExchanges': 'lifi',
    }
    resp = requests.get(f"{LIFI_API}/quote", params=quote_params, timeout=15)
    if resp.status_code != 200:
        raise Exception(f"LiFi 报价失败 ({resp.status_code}): {resp.text[:200]}")
    quote = resp.json()

    if 'transactionRequest' not in quote:
        raise Exception(f"报价缺少 transactionRequest: {quote.get('message', quote)}")

    tx_req = quote['transactionRequest']
    nonce = w3_from.eth.get_transaction_count(from_address, 'pending')

    tx = {
        'from': from_address,
        'to': Web3.to_checksum_address(tx_req['to']),
        'value': int(tx_req.get('value', 0), 16) if isinstance(tx_req.get('value'), str) else int(tx_req.get('value', 0)),
        'data': tx_req.get('data', '0x'),
        'gas': int(tx_req.get('gasLimit', 500000), 16) if isinstance(tx_req.get('gasLimit'), str) else int(tx_req.get('gasLimit', 500000)),
        'gasPrice': w3_from.eth.gas_price,
        'nonce': nonce,
        'chainId': CHAIN_ID_MAP[from_chain]
    }

    signed = w3_from.eth.account.sign_transaction(tx, pk)
    raw = getattr(signed, 'rawTransaction', None) or getattr(signed, 'raw_transaction', None)
    tx_hash = w3_from.eth.send_raw_transaction(raw)
    tx_hash_hex = tx_hash.hex()

    # 2. 等待源链上链确认（快，一般 3-5 秒）
    try:
        w3_from.eth.wait_for_transaction_receipt(tx_hash_hex, timeout=15)
    except Exception:
        pass  # 即使超时也继续，依赖 LiFi status

    # 3. 短时间 poll LiFi status（超时交给前端继续轮询）
    bridge_status = 'PENDING'
    tx_hash_to = None
    deadline = time.time() + poll_timeout
    while time.time() < deadline:
        try:
            status_resp = requests.get(
                f"{LIFI_API}/status",
                params={
                    'txHash': tx_hash_hex,
                    'fromChain': CHAIN_ID_MAP[from_chain],
                    'toChain': CHAIN_ID_MAP[to_chain]
                },
                timeout=8
            )
            if status_resp.status_code == 200:
                sd = status_resp.json()
                bridge_status = sd.get('status', 'PENDING')
                receiving = sd.get('receiving', {})
                tx_hash_to = receiving.get('txHash')
                if bridge_status in ('DONE', 'FAILED'):
                    break
        except Exception:
            pass
        time.sleep(3)

    return {
        'tx_hash': tx_hash_hex,
        'tx_hash_to_chain': tx_hash_to,
        'from': from_address,
        'to': to_address,
        'from_chain': from_chain,
        'to_chain': to_chain,
        'amount': amount,
        'type': 'bridge',
        'bridge_status': bridge_status,  # PENDING / DONE / FAILED
        'explorer_from': explorer_url(from_chain, tx_hash_hex),
        'explorer_to': explorer_url(to_chain, tx_hash_to) if tx_hash_to else None,
        'requires_polling': bridge_status == 'PENDING'
    }


def explorer_url(chain: str, tx_hash: str) -> str:
    if not tx_hash:
        return ''
    explorers = {
        'bsc': 'https://bscscan.com/tx/',
        'bsc_testnet': 'https://testnet.bscscan.com/tx/',
        'polygon': 'https://polygonscan.com/tx/',
        'arbitrum': 'https://arbiscan.io/tx/',
        'optimism': 'https://optimistic.etherscan.io/tx/',
        'base': 'https://basescan.org/tx/',
        'ethereum': 'https://etherscan.io/tx/',
        'avalanche': 'https://snowtrace.io/tx/'
    }
    return explorers.get(chain, '') + tx_hash


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            if not STEP_READY:
                return self._send(500, {'success': False, 'error': f'加载失败: {IMPORT_ERROR}'})

            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length).decode('utf-8')) if content_length else {}

            plan = data.get('plan')
            step_idx = data.get('step_idx')

            if not plan or step_idx is None:
                return self._send(400, {'success': False, 'error': '缺少 plan 或 step_idx'})

            steps = plan.get('steps', [])
            if step_idx < 0 or step_idx >= len(steps):
                return self._send(400, {'success': False, 'error': f'step_idx 越界: {step_idx}'})

            step = steps[step_idx]

            # 执行
            if step['type'] == 'send':
                result = execute_send(plan, step)
            elif step['type'] == 'bridge':
                result = execute_bridge(plan, step)
            else:
                return self._send(400, {'success': False, 'error': f'未知步骤类型: {step["type"]}'})

            next_idx = step_idx + 1
            done = next_idx >= len(steps)

            return self._send(200, {
                'success': True,
                'step_idx': step_idx,
                'next_idx': next_idx,
                'done': done,
                'total_steps': len(steps),
                'step': step,
                'result': result
            })

        except ValueError as e:
            return self._send(400, {
                'success': False,
                'error': str(e),
                'step_idx': data.get('step_idx') if 'data' in dir() else None
            })
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
        try:
            payload = json.dumps(body, default=str).encode('utf-8')
        except Exception:
            payload = json.dumps({'success': False, 'error': '序列化失败'}).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
