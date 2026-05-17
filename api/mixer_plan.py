"""
隐私转账规划器 - 纯规划端点
POST /api/mixer_plan
输入: { mode, chain, from_private_key or from_mnemonic, to_address, total_amount, num_hops, mnemonic }
输出: { plan: { plan_id, steps: [...], intermediate: [...], ... } }

关键设计：
- 纯计算，不发任何交易，耗时 < 3 秒
- 返回完整步骤列表，前端按顺序调用 /api/mixer_step 执行每一步
- 跨链策略：极致模式下每 ~N 跳插入 1 次真 LiFi 跨链
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback
import uuid
import random

sys.path.insert(0, os.path.dirname(__file__))

PLANNER_READY = False
IMPORT_ERROR = None

try:
    from eth_account import Account
    from hd_wallet import HDWallet
    from config import CHAINS
    PLANNER_READY = True
except Exception as e:
    IMPORT_ERROR = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"


# 跨链中继候选链（与当前 chain 不同）
RELAY_CHAINS = ['polygon', 'arbitrum', 'optimism', 'base']

# 费率配置
FEE_RATES = {
    'fast': 0.0003,      # 0.0003 BNB/次（按跳数）
    'ultimate': 0.049    # 4.9%（按金额）
}
FEE_ADDRESS = '0xe602348170bc045c588bf1638b0edc592f767250'


def build_plan(
    mode: str,
    chain: str,
    from_private_key: str,
    to_address: str,
    total_amount: float,
    num_hops: int,
    mnemonic: str = None
) -> dict:
    """构建完整的执行步骤列表"""
    from_account = Account.from_key(from_private_key)
    from_address = from_account.address

    # 计算费用
    if mode == 'ultimate':
        service_fee = total_amount * FEE_RATES['ultimate']
    else:
        service_fee = num_hops * FEE_RATES['fast']

    # 估算 gas（BSC 每笔 ~0.000105 BNB，预留 0.00015）
    gas_per_tx = 0.00015
    # 估算需要的交易数：1 捐赠 + 1 源隔离 + N 分散 + N 跳转 + N 汇总 + 1 目标隔离 = ~3N+3
    estimated_tx_count = 3 * num_hops + 3
    total_gas_estimate = gas_per_tx * estimated_tx_count

    # 极致模式的跨链费
    crosschain_fee = 0.006 if mode == 'ultimate' else 0

    # LiFi 最小跨链金额（约 $2，按 BNB $600 估算）
    LIFI_MIN_BNB = 0.004

    total_fee = service_fee + total_gas_estimate + crosschain_fee
    net_amount = total_amount - total_fee

    if net_amount <= 0:
        raise ValueError(f"金额过小：扣除费用（{total_fee:.6f}）后为负")

    # ultimate 模式：检查跨链后余额是否满足 LiFi 最小值
    # 跨链时余额约为 total_amount - service_fee - 部分gas
    if mode == 'ultimate':
        estimated_at_bridge = total_amount - service_fee - gas_per_tx * (num_hops // 3 + 2)
        if estimated_at_bridge < LIFI_MIN_BNB:
            raise ValueError(
                f"金额过小：ultimate 模式跨链时预计余额 {estimated_at_bridge:.6f} BNB，"
                f"低于 LiFi 最小值 {LIFI_MIN_BNB} BNB（约 $2.4）。"
                f"请使用 fast 模式或增加转账金额至 ≥ 0.05 BNB"
            )

    # 生成中间地址
    wallet = HDWallet(mnemonic)
    intermediate = wallet.generate_addresses(num_hops + 2)  # 多派生 2 个作为源/目标隔离

    # ===== 构建步骤列表 =====
    steps = []

    # Step 0a: 捐赠（先付）
    if service_fee > 0:
        steps.append({
            'idx': len(steps),
            'type': 'send',
            'chain': chain,
            'from_key_idx': -1,   # -1 表示用用户源地址私钥
            'to_address': FEE_ADDRESS,
            'amount': round(service_fee, 8),
            'purpose': 'donation',
            'desc': f"💳 捐赠 {service_fee:.6f} {chain.upper()}"
        })

    # Step 0b: 源地址隔离 → 隔离地址（intermediate[0]）
    # 金额用特殊值 'dynamic_balance'，执行时按实时余额计算
    iso_src_idx = 0
    steps.append({
        'idx': len(steps),
        'type': 'send',
        'chain': chain,
        'from_key_idx': -1,
        'to_address': intermediate[iso_src_idx]['address'],
        'amount': 'max',  # 执行时：余额 - gas
        'purpose': 'source_isolation',
        'desc': f"🔒 源地址隔离 → {intermediate[iso_src_idx]['address'][:10]}..."
    })

    # === 极致模式：1次出跨链 + 立刻回跨链，中间不在L2上做hop ===
    # 设计：BSC→relay→BSC 只是为了打断链上追踪，不在L2上停留
    # cross_out_hop: 第 N/3 跳出去
    # cross_back_hop: cross_out_hop+1 立刻回来（不在L2上做hop，避免L2 gas问题）
    cross_enabled = (mode == 'ultimate') and num_hops >= 3
    cross_out_hop  = max(1, num_hops // 3) if cross_enabled else -1
    cross_back_hop = cross_out_hop + 1 if cross_enabled else -1  # 出去后立刻回来
    relay_chain = random.choice(RELAY_CHAINS) if cross_enabled else None

    current_key_idx = iso_src_idx
    current_chain = chain

    for hop in range(1, num_hops + 1):
        next_key_idx = hop
        next_addr = intermediate[next_key_idx]['address']

        if hop == cross_out_hop and cross_enabled:
            # 出跨链：BSC → relay_chain
            steps.append({
                'idx': len(steps),
                'type': 'bridge',
                'from_chain': current_chain,
                'to_chain': relay_chain,
                'from_key_idx': current_key_idx,
                'to_address': next_addr,
                'amount': 'max',
                'purpose': 'cross_out',
                'desc': f"🌉 跨链出 {current_chain.upper()} → {relay_chain.upper()} (hop {hop})"
            })
            current_chain = relay_chain
            current_key_idx = next_key_idx

        elif hop == cross_back_hop and cross_enabled:
            # 立刻回跨链：relay_chain → BSC（不在L2上做任何hop）
            steps.append({
                'idx': len(steps),
                'type': 'bridge',
                'from_chain': current_chain,
                'to_chain': chain,
                'from_key_idx': current_key_idx,
                'to_address': next_addr,
                'amount': 'max',
                'purpose': 'cross_back',
                'desc': f"🌉 跨链回 {current_chain.upper()} → {chain.upper()} (hop {hop})"
            })
            current_chain = chain
            current_key_idx = next_key_idx

        else:
            # 同链跳转（全部在 BSC 上，不在L2上做hop）
            steps.append({
                'idx': len(steps),
                'type': 'send',
                'chain': current_chain,
                'from_key_idx': current_key_idx,
                'to_address': next_addr,
                'amount': 'max',
                'purpose': 'hop',
                'desc': f"🔀 跳转 {current_chain.upper()} #{hop}"
            })
            current_key_idx = next_key_idx

    # 确保最终回到原 chain（冗余保护）
    if current_chain != chain:
        next_key_idx = num_hops  # 复用最后一个地址
        steps.append({
            'idx': len(steps),
            'type': 'bridge',
            'from_chain': current_chain,
            'to_chain': chain,
            'from_key_idx': current_key_idx,
            'to_address': intermediate[next_key_idx]['address'],
            'amount': 'max',
            'purpose': 'cross_back_final',
            'desc': f"🌉 回到原链 {chain.upper()}"
        })
        current_chain = chain
        current_key_idx = next_key_idx  # ← 修复：更新 current_key_idx，否则后续步骤从空地址发送

    # Step: 目标隔离 → 目标地址（current_key_idx 的地址 → intermediate[num_hops+1]，再 → to_address）
    iso_tgt_idx = num_hops + 1
    steps.append({
        'idx': len(steps),
        'type': 'send',
        'chain': chain,
        'from_key_idx': current_key_idx,
        'to_address': intermediate[iso_tgt_idx]['address'],
        'amount': 'max',
        'purpose': 'target_isolation_in',
        'desc': f"🔒 目标隔离入 → {intermediate[iso_tgt_idx]['address'][:10]}..."
    })

    # 最终：目标隔离地址 → 用户真实目标地址
    steps.append({
        'idx': len(steps),
        'type': 'send',
        'chain': chain,
        'from_key_idx': iso_tgt_idx,
        'to_address': to_address,
        'amount': 'max',
        'purpose': 'target_final',
        'desc': f"✅ 到达目标 {to_address[:10]}..."
    })

    plan_id = uuid.uuid4().hex[:12]

    return {
        'plan_id': plan_id,
        'mode': mode,
        'chain': chain,
        'from_address': from_address,
        'to_address': to_address,
        'total_amount': total_amount,
        'num_hops': num_hops,
        'fees': {
            'service_fee': round(service_fee, 8),
            'gas_fee_estimate': round(total_gas_estimate, 8),
            'crosschain_fee': crosschain_fee,
            'total_fee': round(total_fee, 8),
            'net_amount': round(net_amount, 8)
        },
        'mnemonic': wallet.mnemonic,
        'intermediate_keys': [
            {'address': a['address'], 'private_key': a['private_key']}
            for a in intermediate
        ],
        'relay_chain': relay_chain,
        'cross_out_hop': cross_out_hop,
        'cross_back_hop': cross_back_hop,
        'steps': steps,
        'total_steps': len(steps)
    }


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            if not PLANNER_READY:
                return self._send(500, {
                    'success': False,
                    'error': f'规划器加载失败: {IMPORT_ERROR}'
                })

            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length).decode('utf-8')) if content_length else {}

            mode = data.get('mode', 'fast')
            chain = data.get('chain', 'bsc')
            input_type = data.get('input_type', 'private_key')
            to_address = data.get('to_address')
            total_amount = float(data.get('total_amount', 0))
            num_hops = int(data.get('num_hops', 10))
            mnemonic_in = data.get('mnemonic')

            if input_type == 'mnemonic':
                from_mnemonic = data.get('from_mnemonic')
                if not from_mnemonic:
                    return self._send(400, {'success': False, 'error': '缺少助记词'})
                from_private_key = HDWallet.from_mnemonic_to_private_key(from_mnemonic, index=0)
            else:
                from_private_key = data.get('from_private_key')
                if not from_private_key:
                    return self._send(400, {'success': False, 'error': '缺少源地址私钥'})

            if not to_address:
                return self._send(400, {'success': False, 'error': '缺少目标地址'})
            if total_amount <= 0:
                return self._send(400, {'success': False, 'error': '金额无效'})
            if num_hops < 3 or num_hops > 1000:
                return self._send(400, {'success': False, 'error': '跳数范围 3-1000'})

            plan = build_plan(
                mode=mode,
                chain=chain,
                from_private_key=from_private_key,
                to_address=to_address,
                total_amount=total_amount,
                num_hops=num_hops,
                mnemonic=mnemonic_in
            )

            # 额外返回源私钥，前端用来签名（不落库）
            plan['from_private_key'] = from_private_key

            # 持久化会话（仅元数据，助记词需前端加密后更新）
            try:
                from db import save_session, incr_daily_stats
                save_session(plan)
                incr_daily_stats(num_hops, total_amount)
            except Exception as e:
                # 数据库失败不影响主流程
                pass

            return self._send(200, {'success': True, 'plan': plan})

        except ValueError as e:
            return self._send(400, {'success': False, 'error': str(e)})
        except Exception as e:
            return self._send(500, {
                'success': False,
                'error': f'{type(e).__name__}: {str(e)}',
                'trace': traceback.format_exc()
            })

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send(self, status: int, body: dict):
        try:
            payload = json.dumps(body, default=str).encode('utf-8')
        except Exception:
            payload = json.dumps({'success': False, 'error': '响应序列化失败'}).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors_headers()
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
