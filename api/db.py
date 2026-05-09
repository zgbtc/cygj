"""
Supabase 数据库封装
通过 PostgREST API 操作数据库，无需 supabase-py 依赖

环境变量：
  SUPABASE_URL           - 项目 URL, 如 https://xxx.supabase.co
  SUPABASE_SERVICE_KEY   - service_role key（后端专用，切勿泄露）

Vercel 环境变量配置：
  Settings → Environment Variables → 添加上述两个变量
"""
import os
import json
import logging
import hashlib
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

DB_ENABLED = bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)


def _headers():
    return {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }


def _request(method: str, path: str, body: dict = None, params: dict = None) -> Optional[dict]:
    """统一请求 Supabase REST API。失败只记日志，不抛异常（不影响主流程）"""
    if not DB_ENABLED:
        return None

    try:
        import requests
        url = f"{SUPABASE_URL}/rest/v1/{path.lstrip('/')}"
        resp = requests.request(
            method,
            url,
            headers=_headers(),
            json=body,
            params=params,
            timeout=5
        )
        if resp.status_code >= 400:
            logger.warning(f"DB {method} {path} -> {resp.status_code}: {resp.text[:200]}")
            return None
        return resp.json() if resp.content else {}
    except Exception as e:
        logger.warning(f"DB {method} {path} error: {e}")
        return None


def hash_address(addr: str) -> str:
    """地址哈希，用于用户识别（不存原始地址）"""
    if not addr:
        return ''
    return hashlib.sha256(addr.lower().encode()).hexdigest()[:16]


# ==========================================
# Session 操作
# ==========================================

def save_session(plan: dict, mnemonic_enc: Optional[str] = None) -> bool:
    """保存会话（plan 创建时调用）"""
    if not DB_ENABLED:
        return False

    intermediate = plan.get('intermediate_keys', [])
    from_address = plan.get('from_address', '')

    session_row = {
        'id': plan['plan_id'],
        'user_key': hash_address(from_address),
        'mode': plan['mode'],
        'chain': plan['chain'],
        'relay_chain': plan.get('relay_chain'),
        'from_address': from_address,
        'to_address': plan['to_address'],
        'total_amount': plan['total_amount'],
        'num_hops': plan['num_hops'],
        'total_steps': plan['total_steps'],
        'fees': plan.get('fees'),
        'mnemonic_enc': mnemonic_enc,
        'status': 'planned'
    }

    result = _request('POST', 'mix_sessions', body=session_row)
    if result is None:
        return False

    # 批量插入中间地址
    if intermediate:
        rows = [
            {
                'session_id': plan['plan_id'],
                'idx': i,
                'address': item['address'],
                # 私钥只有客户端加密后才存，默认不存明文
                'privkey_enc': None
            }
            for i, item in enumerate(intermediate)
        ]
        _request('POST', 'mix_intermediate', body=rows)

    logger.info(f"✅ DB: 会话 {plan['plan_id']} 已保存 ({len(intermediate)} 个中间地址)")
    return True


def update_session_status(plan_id: str, status: str) -> bool:
    """更新会话状态"""
    if not DB_ENABLED:
        return False
    result = _request(
        'PATCH',
        'mix_sessions',
        body={'status': status, 'updated_at': 'now()'},
        params={'id': f'eq.{plan_id}'}
    )
    return result is not None


def update_session_mnemonic(plan_id: str, mnemonic_enc: str) -> bool:
    """更新加密后的助记词（客户端提供）"""
    if not DB_ENABLED:
        return False
    result = _request(
        'PATCH',
        'mix_sessions',
        body={'mnemonic_enc': mnemonic_enc},
        params={'id': f'eq.{plan_id}'}
    )
    return result is not None


# ==========================================
# Step 操作
# ==========================================

def save_step(session_id: str, step_idx: int, step_type: str, result: dict, status: str, error: str = None) -> bool:
    """保存单步执行结果"""
    if not DB_ENABLED:
        return False

    row = {
        'session_id': session_id,
        'step_idx': step_idx,
        'type': step_type,
        'chain': result.get('chain'),
        'from_chain': result.get('from_chain'),
        'to_chain': result.get('to_chain'),
        'from_addr': result.get('from'),
        'to_addr': result.get('to'),
        'amount': result.get('amount'),
        'tx_hash': result.get('tx_hash'),
        'tx_hash_to': result.get('tx_hash_to_chain'),
        'bridge_status': result.get('bridge_status'),
        'status': status,
        'error': error
    }

    r = _request('POST', 'mix_steps', body=row)
    return r is not None


# ==========================================
# 查询
# ==========================================

def get_session(plan_id: str) -> Optional[dict]:
    """查询会话（含中间地址和步骤）"""
    if not DB_ENABLED:
        return None

    session = _request('GET', 'mix_sessions', params={'id': f'eq.{plan_id}', 'select': '*'})
    if not session:
        return None

    session = session[0] if isinstance(session, list) and session else None
    if not session:
        return None

    # 中间地址
    intermediate = _request(
        'GET', 'mix_intermediate',
        params={'session_id': f'eq.{plan_id}', 'select': '*', 'order': 'idx.asc'}
    ) or []

    # 步骤
    steps = _request(
        'GET', 'mix_steps',
        params={'session_id': f'eq.{plan_id}', 'select': '*', 'order': 'step_idx.asc'}
    ) or []

    return {
        'session': session,
        'intermediate': intermediate,
        'steps': steps
    }


def list_sessions_by_user(from_address: str, limit: int = 50) -> List[dict]:
    """按源地址查历史会话"""
    if not DB_ENABLED:
        return []

    user_key = hash_address(from_address)
    result = _request(
        'GET', 'mix_sessions',
        params={
            'user_key': f'eq.{user_key}',
            'select': '*',
            'order': 'created_at.desc',
            'limit': str(limit)
        }
    )
    return result or []


# ==========================================
# 统计
# ==========================================

def incr_daily_stats(num_hops: int, volume: float):
    """增加当日统计（upsert）"""
    if not DB_ENABLED:
        return
    from datetime import date
    today = date.today().isoformat()

    # 先读
    existing = _request('GET', 'daily_stats', params={'day': f'eq.{today}'})
    if existing:
        current = existing[0]
        _request(
            'PATCH', 'daily_stats',
            body={
                'total_sessions': current['total_sessions'] + 1,
                'total_hops': current['total_hops'] + num_hops,
                'total_volume': float(current['total_volume']) + volume,
                'updated_at': 'now()'
            },
            params={'day': f'eq.{today}'}
        )
    else:
        _request(
            'POST', 'daily_stats',
            body={
                'day': today,
                'total_sessions': 1,
                'total_hops': num_hops,
                'total_volume': volume
            }
        )
