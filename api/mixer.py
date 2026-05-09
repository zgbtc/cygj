from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

MIXER_AVAILABLE = False
IMPORT_ERROR = None

try:
    from advanced_mixer_engine import AdvancedMixerEngine, MIXING_MODES
    MIXER_AVAILABLE = True
except Exception as e:
    IMPORT_ERROR = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.execute_mixer()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json(self, status: int, body: dict):
        """安全发送 JSON 响应"""
        try:
            payload = json.dumps(body).encode('utf-8')
        except Exception:
            payload = json.dumps({
                'success': False,
                'error': 'Response serialization failed'
            }).encode('utf-8')

        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def execute_mixer(self):
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}

            # 检查隐私转账引擎是否可用
            if not MIXER_AVAILABLE:
                self._send_json(500, {
                    'success': False,
                    'error': f"隐私转账引擎加载失败: {IMPORT_ERROR}"
                })
                return

            # 获取参数
            chain = data.get('chain', 'bsc_testnet')
            mode = data.get('mode', 'fast')
            input_type = data.get('input_type', 'private_key')
            from_private_key = data.get('from_private_key')
            from_mnemonic = data.get('from_mnemonic')
            to_address = data.get('to_address')
            total_amount = data.get('total_amount')
            num_hops = data.get('num_hops', 100)
            mnemonic = data.get('mnemonic')
            gas_level = data.get('gas_level', 'standard')

            # 处理输入：助记词或私钥
            if input_type == 'mnemonic':
                if not from_mnemonic:
                    self._send_json(400, {'success': False, 'error': '缺少助记词'})
                    return
                from hd_wallet import HDWallet
                from_private_key = HDWallet.from_mnemonic_to_private_key(from_mnemonic, index=0)
            else:
                if not from_private_key:
                    self._send_json(400, {'success': False, 'error': '缺少源地址私钥'})
                    return

            # 验证必填参数
            if not to_address:
                self._send_json(400, {'success': False, 'error': '缺少目标地址'})
                return
            if not total_amount:
                self._send_json(400, {'success': False, 'error': '缺少总金额'})
                return

            # Serverless 环境警告：长时间运行任务不适合在此运行
            # 这里仅做前置验证与计划创建。真实执行应由后端任务队列或本地节点完成。
            try:
                mixer = AdvancedMixerEngine(chain, mode=mode)
            except Exception as e:
                self._send_json(500, {
                    'success': False,
                    'error': f"引擎初始化失败: {type(e).__name__}: {str(e)}",
                    'trace': traceback.format_exc(),
                    'hint': 'Serverless 环境无法长时间连接外部 RPC/代理，建议本地部署或使用自建后端'
                })
                return

            try:
                plan = mixer.create_mixing_plan(
                    from_private_key=from_private_key,
                    to_address=to_address,
                    total_amount=float(total_amount),
                    num_hops=int(num_hops),
                    mnemonic=mnemonic
                )
            except Exception as e:
                self._send_json(500, {
                    'success': False,
                    'error': f"计划创建失败: {type(e).__name__}: {str(e)}",
                    'trace': traceback.format_exc()
                })
                return

            try:
                result = mixer.execute_mixing(plan, gas_level=gas_level)
            except Exception as e:
                self._send_json(500, {
                    'success': False,
                    'error': f"执行失败: {type(e).__name__}: {str(e)}",
                    'trace': traceback.format_exc()
                })
                return

            self._send_json(200, result)

        except Exception as e:
            # 兜底错误处理
            self._send_json(500, {
                'success': False,
                'error': f"{type(e).__name__}: {str(e)}",
                'trace': traceback.format_exc()
            })
