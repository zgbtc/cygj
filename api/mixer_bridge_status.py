"""
跨链状态查询端点 - 前端在 bridge step 返回 PENDING 时轮询
POST /api/mixer_bridge_status
输入: { tx_hash, from_chain, to_chain }
输出: { status, tx_hash_to, explorer_to }
"""
from http.server import BaseHTTPRequestHandler
import json
import traceback

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

LIFI_API = "https://li.quest/v1"


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
            import requests
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length).decode('utf-8')) if content_length else {}

            tx_hash = data.get('tx_hash')
            from_chain = data.get('from_chain')
            to_chain = data.get('to_chain')

            if not all([tx_hash, from_chain, to_chain]):
                return self._send(400, {'success': False, 'error': '缺少参数'})

            resp = requests.get(
                f"{LIFI_API}/status",
                params={
                    'txHash': tx_hash,
                    'fromChain': CHAIN_ID_MAP.get(from_chain, from_chain),
                    'toChain': CHAIN_ID_MAP.get(to_chain, to_chain)
                },
                timeout=10
            )
            if resp.status_code != 200:
                return self._send(200, {
                    'success': True,
                    'status': 'PENDING',
                    'message': f'LiFi API {resp.status_code}'
                })

            sd = resp.json()
            status = sd.get('status', 'PENDING')
            receiving = sd.get('receiving', {})
            tx_hash_to = receiving.get('txHash')

            return self._send(200, {
                'success': True,
                'status': status,
                'tx_hash_to': tx_hash_to,
                'explorer_to': explorer_url(to_chain, tx_hash_to) if tx_hash_to else None
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
        payload = json.dumps(body, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
