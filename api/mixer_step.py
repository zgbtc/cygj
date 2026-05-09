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
    """顺序尝试 RPC，选第一个可用的（短超时，快失败）"""
    chain_cfg = CHAINS.get(chain)
    if not chain_cfg:
        # relay chain RPCs
        fallback_rpcs = {
            'polygon': ['https://polygon.llamarpc.com', 'https://polygon-rpc.com', 'https://polygon.drpc.org', 'https://polygon-bor-rpc.publicnode.com'],
            'arbitrum': ['https://arbitrum.llamarpc.com', 'https://arb1.arbitrum.io/rpc', 'https://arbitrum.drpc.org', 'https://arbitrum-one.publicnode.com'],
            'optimism': ['https://optimism.llamarpc.com', 'https://mainnet.optimism.io', 'https://optimism.drpc.org'],
            'base': ['https://base.llamarpc.com', 'https://mainnet.base.org', 'https://base.drpc.org'],
            'avalanche': ['https://api.avax.network/ext/bc/C/rpc', 'https://avalanche.drpc.org'],
            'ethereum': ['https://eth.llamarpc.com', 'https://ethereum.publicnode.com', 'https://eth.drpc.org']
        }
        rpc_urls = fallback_rpcs.get(chain, [])
    else:
        rpc_urls = chain_cfg.get('rpc_urls') or [chain_cfg.get('rpc_url')]
        rpc_urls = [u for u in rpc_urls if u]

    if not rpc_urls:
        raise ConnectionError(f"未配置 {chain} 的 RPC")

    expected_chain_id = CHAIN_ID_MAP.get(chain)

    for url in rpc_urls[:8]:
        try:
            w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 2.5}))
            cid = w3.eth.chain_id
            if expected_chain_id and cid != expected_chain_id:
                continue
            return w3
        except Exception:
            continue

    raise ConnectionError(f"{chain} 所有 RPC 不可用")


def get_private_key(plan: dict, key_idx: int) -> str:
    """根据 key_idx 找到对应的私钥"""
    if key_idx == -1:
        return plan['from_private_key']
    return plan['intermediate_keys'][key_idx]['private_key']


def _wait_balance(w3_init, chain: str, address: str, timeout: int = 35) -> tuple:
    """
    读余额，如果为 0 则轮询重试（换 RPC 节点），最多 timeout 秒。
    返回 (balance_wei, w3) - 若成功拿到非 0 余额，w3 是最后查到余额的连接。
    """
    try:
        balance_wei = w3_init.eth.get_balance(address)
    except Exception:
        balance_wei = 0

    if balance_wei > 0:
        return balance_wei, w3_init

    # 余额为 0，可能是 RPC 节点滞后或上一步 tx 还没到达该节点视图
    deadline = time.time() + timeout
    attempt = 0
    w3 = w3_init
    while time.time() < deadline:
        attempt += 1
        try:
            time.sleep(min(1.5 + attempt * 0.3, 3.5))
            # 每 3 次换一个新 RPC 节点
            if attempt % 3 == 0:
                try:
                    w3 = connect_chain(chain)
                except Exception:
                    pass
            balance_wei = w3.eth.get_balance(address)
            if balance_wei > 0:
                return balance_wei, w3
        except Exception:
            continue
    return balance_wei, w3


def execute_send(plan: dict, step: dict) -> dict:
    """执行同链发送"""
    chain = step['chain']
    w3 = connect_chain(chain)
    chain_id = CHAIN_ID_MAP.get(chain, 56)

    pk = get_private_key(plan, step['from_key_idx'])
    account = Account.from_key(pk)
    from_address = account.address
    to_address = Web3.to_checksum_address(step['to_address'])

    # Gas price（动态，加 20% buffer 防止波动）
    try:
        gas_price = int(w3.eth.gas_price * 1.2)
    except Exception:
        gas_price = w3.to_wei(5, 'gwei')
    gas_cost_wei = 21000 * gas_price

    # 读余额；若是 max 模式且暂时为 0（RPC 滞后），轮询重试
    if step['amount'] == 'max':
        balance_wei, w3 = _wait_balance(w3, chain, from_address, timeout=35)
    else:
        balance_wei = w3.eth.get_balance(from_address)

    # 计算发送金额（精确到 wei，避免浮点误差）
    if step['amount'] == 'max':
        # 扣除 gas + 多留 1000 wei 防舍入
        amount_wei = balance_wei - gas_cost_wei - 1000
    else:
        amount_wei = w3.to_wei(float(step['amount']), 'ether')

    if amount_wei <= 0:
        balance = float(w3.from_wei(balance_wei, 'ether'))
        gas_buffer = float(w3.from_wei(gas_cost_wei, 'ether'))
        raise ValueError(
            f"余额不足：balance={balance:.8f}, need gas={gas_buffer:.8f}, amount_wei={amount_wei}"
        )

    # 防御：确保 value + gas <= balance
    if amount_wei + gas_cost_wei > balance_wei:
        amount_wei = balance_wei - gas_cost_wei - 1000
        if amount_wei <= 0:
            raise ValueError(f"扣 gas 后余额为负")

    amount = float(w3.from_wei(amount_wei, 'ether'))

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
    tx_hash_hex = tx_hash.hex()

    # 等待本笔 tx 上链（关键：保证下一步读 to_address 余额时链上已确认）
    try:
        w3.eth.wait_for_transaction_receipt(tx_hash_hex, timeout=45, poll_latency=1.0)
    except Exception:
        pass  # 超时不致命，下一步会用 _wait_balance 兜底

    return {
        'tx_hash': tx_hash_hex,
        'from': from_address,
        'to': to_address,
        'amount': amount,
        'chain': chain,
        'type': 'send',
        'explorer': explorer_url(chain, tx_hash_hex)
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
    # max 模式下余额为 0 很可能是 RPC 滞后
    if step['amount'] == 'max' and balance_wei == 0:
        balance_wei, w3_from = _wait_balance(w3_from, from_chain, from_address, timeout=35)
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
            step_type = step['type']
            error_msg = None
            result = None
            try:
                if step_type == 'send':
                    result = execute_send(plan, step)
                elif step_type == 'bridge':
                    result = execute_bridge(plan, step)
                else:
                    return self._send(400, {'success': False, 'error': f'未知步骤类型: {step_type}'})
            except Exception as step_err:
                error_msg = str(step_err)
                # 记录失败
                try:
                    from db import save_step, update_session_status
                    save_step(plan['plan_id'], step_idx, step_type, {}, 'failed', error_msg)
                except Exception:
                    pass
                raise

            # 持久化成功结果
            try:
                from db import save_step, update_session_status
                save_step(plan['plan_id'], step_idx, step_type, result, 'success')
                next_idx = step_idx + 1
                if next_idx >= len(steps):
                    update_session_status(plan['plan_id'], 'done')
                elif step_idx == 0:
                    update_session_status(plan['plan_id'], 'running')
            except Exception:
                pass

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
