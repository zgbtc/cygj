from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback
import asyncio
from datetime import datetime
import hashlib

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

MIXER_AVAILABLE = False
ULTIMATE_MIXER_AVAILABLE = False
SUPABASE_AVAILABLE = False
IMPORT_ERROR = None

try:
    from advanced_mixer_engine import AdvancedMixerEngine, MIXING_MODES
    MIXER_AVAILABLE = True
except Exception as e:
    IMPORT_ERROR = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"

try:
    from ultimate_privacy_mixer import UltimatePrivacyMixer
    ULTIMATE_MIXER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ 极致隐私混币器不可用: {e}")

try:
    from supabase_client import get_supabase_client
    SUPABASE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Supabase 不可用: {e}")


def generate_session_id() -> str:
    """生成 12 位 hex session ID"""
    import secrets
    return secrets.token_hex(6)


def hash_address(address: str) -> str:
    """对地址进行 hash，用作用户标识"""
    return hashlib.sha256(address.encode()).hexdigest()[:16]


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
            # 中间地址派生：每次随机生成助记词，先存库再执行
            # - 随机助记词：每次地址完全不同，链上无规律可循
            # - 先存库：助记词持久化后才执行，资金绝不会丢
            gas_level = data.get('gas_level', 'standard')

            # 安全检查：Supabase 不可用时，fast 模式仍可执行（私钥在用户本地）
            # ultimate 模式需要数据库持久化助记词，不可用时拒绝
            if not SUPABASE_AVAILABLE and mode == 'ultimate':
                self._send_json(503, {
                    'success': False,
                    'error': '数据库不可用，极致隐私模式无法安全执行（助记词无法持久化）。请使用快速模式或稍后重试。'
                })
                return
            # 极致隐私模式的路径类型：simple(2跨链) / standard(3跨链) / complex(4跨链)
            path_type = data.get('path_type', 'standard')

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

            # 生成 session ID
            session_id = generate_session_id()
            
            # 获取源地址（用于用户标识）
            from web3 import Account
            from_address = Account.from_key(from_private_key).address
            user_key = hash_address(from_address)

            # ==========================================
            # 极致隐私模式旧引擎（已废弃，现在统一走 AdvancedMixerEngine）
            # ==========================================
            # if mode == 'ultimate': ... （已移除，下方统一处理）

            # ==========================================
            # 快速模式 / 极致隐私模式：统一走 AdvancedMixerEngine
            # ==========================================
            try:
                mixer = AdvancedMixerEngine(chain, mode=mode)
            except Exception as e:
                self._send_json(500, {
                    'success': False,
                    'error': f"引擎初始化失败: {type(e).__name__}: {str(e)}",
                    'trace': traceback.format_exc(),
                })
                return

            try:
                # ── 第一步：随机生成助记词 ──────────────────────────────
                # 每次全新随机，链上地址无规律可循，隐私性最强
                from hd_wallet import HDWallet as _HDW
                relay_mnemonic = _HDW.generate_random_mnemonic(12)

                # ── 第二步：先存库，存库失败则拒绝执行 ──────────────────
                # 原则：助记词必须持久化后才能动用户的钱，绝不反过来
                session_id = generate_session_id()
                try:
                    asyncio.run(self._save_mnemonic_session(
                        session_id=session_id,
                        user_key=user_key,
                        mode=mode,
                        chain=chain,
                        from_address=from_address,
                        to_address=to_address,
                        total_amount=float(total_amount),
                        num_hops=int(num_hops),
                        relay_mnemonic=relay_mnemonic,
                    ))
                except Exception as e:
                    self._send_json(503, {
                        'success': False,
                        'error': f'助记词存库失败，拒绝执行混币以防资金丢失: {e}'
                    })
                    return

                # ── 第三步：创建计划（助记词已安全落库）────────────────
                plan = mixer.create_mixing_plan(
                    from_private_key=from_private_key,
                    to_address=to_address,
                    total_amount=float(total_amount),
                    num_hops=int(num_hops),
                    mnemonic=relay_mnemonic,
                    start_index=0   # 随机助记词每次从 0 开始即可，本身就不重复
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
                
                # 更新会话状态为 running（执行开始）→ done/failed
                if SUPABASE_AVAILABLE:
                    try:
                        asyncio.run(get_supabase_client().update_session(
                            session_id, {'status': 'running', 'fees': plan.get('fees', {})}
                        ))
                    except Exception:
                        pass  # 状态更新失败不影响执行

                # 更新会话状态
                if SUPABASE_AVAILABLE and result.get('success'):
                    try:
                        asyncio.run(self._update_session_complete(
                            session_id=session_id,
                            result=result
                        ))
                    except Exception as e:
                        print(f"⚠️ 更新会话失败: {e}")
                
                # 添加 session_id 到返回结果
                result['session_id'] = session_id
                
            except Exception as e:
                # 标记会话失败
                if SUPABASE_AVAILABLE:
                    try:
                        asyncio.run(self._update_session_failed(
                            session_id=session_id,
                            error=str(e)
                        ))
                    except:
                        pass
                
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
    
    async def _save_mnemonic_session(self, session_id, user_key, mode, chain,
                                     from_address, to_address, total_amount,
                                     num_hops, relay_mnemonic):
        """
        第一步存库：把随机助记词持久化到数据库。
        这个方法必须成功，才能继续执行混币。
        助记词明文存储（service_role 权限，RLS 关闭，外部无法直接读取）。
        """
        db = get_supabase_client()
        session_data = {
            "id": session_id,
            "user_key": user_key,
            "mode": mode,
            "chain": chain,
            "from_address": from_address,
            "to_address": to_address,
            "total_amount": total_amount,
            "num_hops": num_hops,
            "total_steps": 0,
            "fees": {},
            "mnemonic_enc": relay_mnemonic,   # 随机助记词明文，用于资金恢复
            "status": "pending"               # pending → running → done/failed
        }
        await db.create_session(session_data)

    async def _save_session(self, session_id, user_key, mode, chain, from_address, 
                           to_address, total_amount, num_hops, plan):
        """保存会话到数据库（含 start_index，用于资金恢复）"""
        db = get_supabase_client()
        
        fees = plan.get('fees', {})
        # 把 start_index 存进 fees jsonb，方便恢复时定位地址段
        fees['relay_start_index'] = plan.get('start_index', 0)
        fees['relay_num_hops'] = num_hops

        session_data = {
            "id": session_id,
            "user_key": user_key,
            "mode": mode,
            "chain": chain,
            "from_address": from_address,
            "to_address": to_address,
            "total_amount": total_amount,
            "num_hops": num_hops,
            "total_steps": len(plan.get('steps', [])),
            "fees": fees,
            # mnemonic_enc 存 "RELAY:{start_index}" 标记，表示用固定助记词从该索引派生
            # 真正的助记词在服务器环境变量 RELAY_MNEMONIC 里，不落库
            "mnemonic_enc": f"RELAY:{plan.get('start_index', 0)}",
            "status": "running"
        }
        
        await db.create_session(session_data)
    
    async def _update_session_complete(self, session_id, result):
        """更新会话为完成状态"""
        db = get_supabase_client()
        
        # 保存所有交易步骤
        steps = result.get('steps', [])
        for i, step in enumerate(steps):
            step_data = {
                "session_id": session_id,
                "step_idx": i + 1,
                "type": step.get('type', 'send'),
                "chain": step.get('chain'),
                "from_addr": step.get('from'),
                "to_addr": step.get('to'),
                "amount": step.get('amount'),
                "tx_hash": step.get('tx_hash'),
                "status": step.get('status', 'success')
            }
            try:
                await db.save_step(step_data)
            except Exception as e:
                print(f"⚠️ 保存步骤 {i+1} 失败: {e}")
        
        # 更新会话状态
        await db.update_session(session_id, {"status": "done"})
        
        # 更新每日统计
        today = datetime.now().strftime("%Y-%m-%d")
        await db.update_daily_stats(
            date=today,
            sessions=1,
            hops=result.get('total_hops', 0),
            volume=result.get('total_amount', 0)
        )
    
    async def _update_session_failed(self, session_id, error):
        """更新会话为失败状态"""
        db = get_supabase_client()
        await db.update_session(session_id, {
            "status": "failed"
        })
    
    async def _save_ultimate_session(self, session_id, user_key, chain, 
                                     from_address, to_address, total_amount,
                                     path, path_type):
        """保存极致隐私模式的会话"""
        db = get_supabase_client()
        
        session_data = {
            "id": session_id,
            "user_key": user_key,
            "mode": "ultimate",
            "chain": chain,
            "relay_chain": ",".join(path[1:-1]) if len(path) > 2 else None,
            "from_address": from_address,
            "to_address": to_address,
            "total_amount": total_amount,
            "num_hops": len(path) - 1,
            "total_steps": len(path) - 1,
            "fees": {"path_type": path_type, "path": path},
            "status": "running"
        }
        
        await db.create_session(session_data)
    
    def _format_ultimate_response(self, result: dict, session_id: str) -> dict:
        """将极致隐私模式的结果转换为前端期望的格式"""
        steps = []
        step_idx = 1
        
        # 跨链步骤
        for cc_step in result.get('cross_chain_steps', []):
            br = cc_step.get('result', {})
            from_chain = cc_step.get('from_chain', '')
            to_chain = cc_step.get('to_chain', '')
            steps.append({
                'step': step_idx,
                'type': 'bridge',
                'from_chain': from_chain,
                'to_chain': to_chain,
                'from': br.get('from_address', ''),
                'to': br.get('to_address', ''),
                'amount': br.get('from_amount', 0),
                'amount_received': br.get('to_amount_estimated', 0),
                'tx_hash': br.get('tx_hash', ''),
                'tool': br.get('tool', ''),
                'duration': br.get('duration', 0),
                'status': 'success' if br.get('success') else 'failed',
                'error': br.get('error')
            })
            step_idx += 1
        
        return {
            'success': result.get('success', False),
            'mode': 'ultimate',
            'session_id': session_id,
            'path': result.get('path', []),
            'hops_per_chain': result.get('hops_per_chain', 0),
            'total_hops': len(result.get('cross_chain_steps', [])),
            'final_amount': result.get('final_amount', 0),
            'target_address': result.get('target_address', ''),
            'steps': steps,
            'success_count': sum(1 for s in steps if s['status'] == 'success'),
            'failed_count': sum(1 for s in steps if s['status'] == 'failed'),
            'error': result.get('error')
        }
