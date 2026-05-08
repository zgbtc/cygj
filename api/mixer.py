from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from mixer_engine import MixerEngine
    MIXER_AVAILABLE = True
except ImportError as e:
    MIXER_AVAILABLE = False
    IMPORT_ERROR = str(e)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.execute_mixer()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def execute_mixer(self):
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            # 检查混币引擎是否可用
            if not MIXER_AVAILABLE:
                raise Exception(f"混币引擎加载失败: {IMPORT_ERROR}")
            
            # 获取参数
            chain = data.get('chain', 'bsc_testnet')
            from_private_key = data.get('from_private_key')
            to_address = data.get('to_address')
            total_amount = data.get('total_amount')
            num_hops = data.get('num_hops', 100)
            mnemonic = data.get('mnemonic')
            gas_level = data.get('gas_level', 'standard')
            
            # 验证必填参数
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
                total_amount=float(total_amount),
                num_hops=int(num_hops),
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