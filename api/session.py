"""
会话查询端点
GET  /api/session?id=<plan_id>           查询单个会话（含中间地址 + 步骤）
POST /api/session                         用户保存加密后的 mnemonic
        { plan_id, mnemonic_enc }
GET  /api/session?user_address=<0x...>   查询用户的历史会话（按源地址）
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(__file__))


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            from db import get_session, list_sessions_by_user, DB_ENABLED

            if not DB_ENABLED:
                return self._send(503, {'success': False, 'error': '数据库未配置'})

            qs = parse_qs(urlparse(self.path).query)
            plan_id = qs.get('id', [None])[0]
            user_address = qs.get('user_address', [None])[0]

            if plan_id:
                data = get_session(plan_id)
                if not data:
                    return self._send(404, {'success': False, 'error': '会话不存在'})
                return self._send(200, {'success': True, 'data': data})

            if user_address:
                sessions = list_sessions_by_user(user_address, limit=100)
                return self._send(200, {'success': True, 'sessions': sessions})

            return self._send(400, {'success': False, 'error': '需要 id 或 user_address 参数'})

        except Exception as e:
            return self._send(500, {
                'success': False,
                'error': f'{type(e).__name__}: {str(e)}',
                'trace': traceback.format_exc()
            })

    def do_POST(self):
        """保存用户加密后的 mnemonic"""
        try:
            from db import update_session_mnemonic, DB_ENABLED
            if not DB_ENABLED:
                return self._send(503, {'success': False, 'error': '数据库未配置'})

            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length).decode('utf-8')) if content_length else {}

            plan_id = data.get('plan_id')
            mnemonic_enc = data.get('mnemonic_enc')

            if not plan_id or not mnemonic_enc:
                return self._send(400, {'success': False, 'error': '缺少 plan_id 或 mnemonic_enc'})

            ok = update_session_mnemonic(plan_id, mnemonic_enc)
            return self._send(200, {'success': ok})

        except Exception as e:
            return self._send(500, {
                'success': False,
                'error': f'{type(e).__name__}: {str(e)}'
            })

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send(self, status: int, body: dict):
        payload = json.dumps(body, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
