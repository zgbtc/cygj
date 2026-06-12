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

    # ===== 第一步：先决定跨链路径参数（fees 计算依赖 cross_count） =====
    # 极致模式：在 relay 链上做几跳，把 cross_out 和 cross_back 时间窗拉开
    # 跨链段结构：cross_out → relay_inner_hops 同链跳 → cross_back（消耗 2 + relay_inner_hops 个 hop）
    cross_enabled = (mode == 'ultimate') and num_hops >= 5

    if cross_enabled:
        relay_inner_hops = random.randint(3, 5)
        cross_segment_size = 2 + relay_inner_hops
        max_segments_by_budget = max(0, (num_hops - 2) // cross_segment_size)
        if num_hops >= 16:
            cross_count = min(3, max_segments_by_budget)
        elif num_hops >= 10:
            cross_count = min(2, max_segments_by_budget)
        else:
            cross_count = min(1, max_segments_by_budget)

        if cross_count == 0:
            # num_hops 太小放不下任何跨链段，降级为纯 BSC 多跳
            cross_enabled = False
            relay_inner_hops = 0
            cross_segment_size = 0
            relays_for_segments = []
        else:
            relays_for_segments = random.sample(
                RELAY_CHAINS, min(cross_count, len(RELAY_CHAINS))
            )
            while len(relays_for_segments) < cross_count:
                relays_for_segments.append(random.choice(RELAY_CHAINS))
    else:
        relay_inner_hops = 0
        cross_segment_size = 0
        cross_count = 0
        relays_for_segments = []

    # ===== 第二步：计算费用 =====
    # 服务费
    if mode == 'ultimate':
        service_fee = total_amount * FEE_RATES['ultimate']
    else:
        service_fee = num_hops * FEE_RATES['fast']

    # Gas 估算：实际交易数 = num_hops + 3（捐赠 + src 隔离 + N hop + tgt 隔离 + final = N+4 含 donation）
    # bridge 步骤 gas 高（LiFi ~500k）但只占 cross_count*2 笔，其余是普通 send (21k)
    # 简化：用 BSC 5 gwei × 1.5 buffer 估，bridge 单独按 500k gas 估
    SEND_GAS_BNB = 0.00015          # 21000 * 5 gwei * 1.5x ≈ 0.000158
    BRIDGE_GAS_BNB = 0.003          # 500000 * 5 gwei * 1.2x ≈ 0.003
    send_count = num_hops + 3 - (cross_count * 2)   # 除去 cross 步骤的同链 send
    bridge_count = cross_count * 2                  # cross_out + cross_back per segment
    total_gas_estimate = send_count * SEND_GAS_BNB + bridge_count * BRIDGE_GAS_BNB

    # 跨链协议费（LiFi/Stargate 类抽 0.05-0.3% slippage 内含，每段保守 $1.5）
    # 按 BNB $600 估，每次 ≈ 0.0025 BNB；但用户实际是按金额抽，这里只做净额预估
    crosschain_fee = cross_count * 0.0025

    # LiFi 最小跨链金额（按 BNB $600 估约 $2.4）
    LIFI_MIN_BNB = 0.004

    total_fee = service_fee + total_gas_estimate + crosschain_fee
    net_amount = total_amount - total_fee

    if net_amount <= 0:
        raise ValueError(f"金额过小：扣除费用（{total_fee:.6f}）后为负")

    # ultimate 模式：检查跨链时余额是否满足 LiFi 最小值
    if cross_enabled:
        # 跨链时大约扣了：服务费 + 部分 gas + 第一段 BSC 跳的 gas
        estimated_at_bridge = total_amount - service_fee - SEND_GAS_BNB * (num_hops // 4 + 2)
        if estimated_at_bridge < LIFI_MIN_BNB:
            raise ValueError(
                f"金额过小：ultimate 模式跨链时预计余额 {estimated_at_bridge:.6f} BNB，"
                f"低于 LiFi 最小值 {LIFI_MIN_BNB} BNB（约 $2.4）。"
                f"请使用 fast 模式或增加转账金额至 ≥ 0.05 BNB"
            )

    # 生成中间地址：用随机派生索引打散链上派生路径，避免 0,1,2,3... 这种规律
    # 派生索引空间足够大（2^31），num_hops 最多 1000，碰撞概率忽略
    wallet = HDWallet(mnemonic)
    intermediate_count = num_hops + 2  # +2 给源/目标隔离
    relay_indices = random.sample(range(1, 2_000_000_000), intermediate_count)
    intermediate = wallet.generate_addresses_by_indices(relay_indices)

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
    # 金额用特殊值 'max'，执行时按实时余额计算
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

    # ===== 极致模式：多段跨链 + relay 链上多跳，破坏跨链 in/out 时间窗 =====
    # 跨链路径参数已在前面（fees 计算前）确定：
    #   cross_enabled, cross_count, relay_inner_hops, cross_segment_size, relays_for_segments

    # 计算 BSC 同链 hop 总数 = num_hops - 跨链段消耗的 hop 数
    bsc_hops_total = num_hops - cross_count * cross_segment_size
    if bsc_hops_total < 0:
        bsc_hops_total = 0

    # 把 BSC hop 分配到 cross_count + 1 个段（首段、各跨链段之间、末段）
    num_bsc_segments = cross_count + 1
    bsc_per_segment = [bsc_hops_total // num_bsc_segments] * num_bsc_segments
    for i in range(bsc_hops_total % num_bsc_segments):
        bsc_per_segment[i] += 1
    random.shuffle(bsc_per_segment)  # 随机化每段长度，避免规律

    # ── 构建 step 序列 ─────────────────────────────────────────
    current_key_idx = iso_src_idx          # 当前持有资金的中间地址索引
    next_key_idx = 1                       # intermediate 数组的下一个空闲槽位
    current_chain = chain

    def _emit_send(to_idx, on_chain, purpose, hop_label):
        """生成一笔同链 send 步骤"""
        nonlocal current_key_idx
        steps.append({
            'idx': len(steps),
            'type': 'send',
            'chain': on_chain,
            'from_key_idx': current_key_idx,
            'to_address': intermediate[to_idx]['address'],
            'amount': 'max',
            'purpose': purpose,
            'desc': f"🔀 跳转 {on_chain.upper()} {hop_label}"
        })
        current_key_idx = to_idx

    def _emit_bridge(to_idx, from_chain_name, to_chain_name, purpose, label):
        """生成一笔跨链步骤"""
        nonlocal current_key_idx, current_chain
        steps.append({
            'idx': len(steps),
            'type': 'bridge',
            'from_chain': from_chain_name,
            'to_chain': to_chain_name,
            'from_key_idx': current_key_idx,
            'to_address': intermediate[to_idx]['address'],
            'amount': 'max',
            'purpose': purpose,
            'desc': f"🌉 {label} {from_chain_name.upper()} → {to_chain_name.upper()}"
        })
        current_key_idx = to_idx
        current_chain = to_chain_name

    # 首段 BSC 跳转
    for h in range(bsc_per_segment[0]):
        _emit_send(next_key_idx, chain, 'hop', f"#bsc-pre-{h+1}")
        next_key_idx += 1

    # 跨链段
    for seg_i in range(cross_count):
        relay = relays_for_segments[seg_i]

        # cross_out: BSC → relay
        _emit_bridge(next_key_idx, chain, relay, 'cross_out', f"跨链出 #{seg_i+1}")
        next_key_idx += 1

        # relay 链上 3-5 跳同链，打散时间窗和地址直连关系
        for h in range(relay_inner_hops):
            _emit_send(next_key_idx, relay, 'relay_hop', f"#{relay}-{h+1}")
            next_key_idx += 1

        # cross_back: relay → BSC
        _emit_bridge(next_key_idx, relay, chain, 'cross_back', f"跨链回 #{seg_i+1}")
        next_key_idx += 1

        # 跨链后的 BSC 段
        seg_bsc_count = bsc_per_segment[seg_i + 1]
        for h in range(seg_bsc_count):
            _emit_send(next_key_idx, chain, 'hop', f"#bsc-mid-{seg_i+1}-{h+1}")
            next_key_idx += 1

    # 冗余保护：万一末态不在原链，强制桥回（理论上 cross_back 已经保证了）
    if current_chain != chain:
        _emit_bridge(next_key_idx, current_chain, chain, 'cross_back_final', "强制回链")
        next_key_idx += 1

    # 目标隔离入：当前 → 隔离地址
    iso_tgt_idx = num_hops + 1   # intermediate 最后一个槽
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
        # 兼容字段：前端读 relay_chain 显示"经过 X 链"。多段时取第一段，没跨链时为 None
        'relay_chain': relays_for_segments[0] if relays_for_segments else None,
        # 多段跨链元信息：前端可选展示
        'relay_chains': relays_for_segments,
        'cross_count': cross_count if cross_enabled else 0,
        'relay_inner_hops': relay_inner_hops if cross_enabled else 0,
        # 兼容字段（保留以防旧前端版本读取）
        'cross_out_hop': -1,
        'cross_back_hop': -1,
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
