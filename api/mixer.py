from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# 添加 stealth_transfer 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'stealth_transfer'))

try:
    from mixer_engine import MixerEngine
except ImportError:
    # 如果导入失败，返回错误信息
    MixerEngine = None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/mixer/execute':
            self.execute_mixer()
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def execute_mixer(self):
        try:
            # 读取请求数据
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if MixerEngine is None:
                raise Exception("混币引擎未正确加载")
            
            chain = data.get('chain', 'bsc_testnet')
            from_private_key = data.get('from_private_key')
            to_address = data.get('to_address')
            total_amount = data.get('total_amount')
            num_hops = data.get('num_hops', 100)
            mnemonic = data.get('mnemonic')
            gas_level = data.get('gas_level', 'standard')
            
            if not from_private_key:
                raise Exception('缺少源地址私钥')
            
            if not to_address:
                raise Exception('缺少目标地址')
            
            if not total_amount:
                raise Exception('缺少总金额')
            
            # 创建混币器引擎
            mixer = MixerEngine(chain)
            
            # 创建混币计划
            plan = mixer.create_mixing_plan(
                from_private_key=from_private_key,
                to_address=to_address,
                total_amount=total_amount,
                num_hops=num_hops,
                mnemonic=mnemonic
            )
            
            # 执行混币
            result = mixer.execute_mixing(plan, gas_level=gas_level)
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            # 发送错误响应
            error_response = {
                'success': False,
                'error': str(e)
            }
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))