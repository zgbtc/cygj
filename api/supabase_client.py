"""
Supabase 客户端 - 用于混币数据持久化
"""
import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from datetime import datetime
import json

class SupabaseClient:
    def __init__(self):
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # 使用 service_role key，绕过 RLS
        
        if not url or not key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        # 创建客户端
        self.client: Client = create_client(url, key)
    
    # ==========================================
    # 混币会话 (mix_sessions)
    # ==========================================
    
    async def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的混币会话"""
        result = self.client.table("mix_sessions").insert(session_data).execute()
        return result.data[0] if result.data else {}
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新会话状态"""
        updates["updated_at"] = datetime.utcnow().isoformat()
        result = self.client.table("mix_sessions").update(updates).eq("id", session_id).execute()
        return result.data[0] if result.data else {}
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话详情"""
        result = self.client.table("mix_sessions").select("*").eq("id", session_id).execute()
        return result.data[0] if result.data else None
    
    async def get_user_sessions(self, user_key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的历史会话"""
        result = (
            self.client.table("mix_sessions")
            .select("*")
            .eq("user_key", user_key)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    
    # ==========================================
    # 中间地址 (mix_intermediate)
    # ==========================================
    
    async def save_intermediate_addresses(self, addresses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量保存中间地址"""
        result = self.client.table("mix_intermediate").insert(addresses).execute()
        return result.data or []
    
    async def get_intermediate_addresses(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话的所有中间地址"""
        result = (
            self.client.table("mix_intermediate")
            .select("*")
            .eq("session_id", session_id)
            .order("idx")
            .execute()
        )
        return result.data or []
    
    async def update_address_balance(self, address: str, balance: float):
        """更新地址余额"""
        self.client.table("mix_intermediate").update({
            "final_balance": balance
        }).eq("address", address).execute()
    
    # ==========================================
    # 交易步骤 (mix_steps)
    # ==========================================
    
    async def save_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存单个交易步骤"""
        result = self.client.table("mix_steps").insert(step_data).execute()
        return result.data[0] if result.data else {}
    
    async def update_step(self, session_id: str, step_idx: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新交易步骤状态"""
        result = (
            self.client.table("mix_steps")
            .update(updates)
            .eq("session_id", session_id)
            .eq("step_idx", step_idx)
            .execute()
        )
        return result.data[0] if result.data else {}
    
    async def get_session_steps(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话的所有交易步骤"""
        result = (
            self.client.table("mix_steps")
            .select("*")
            .eq("session_id", session_id)
            .order("step_idx")
            .execute()
        )
        return result.data or []
    
    # ==========================================
    # 每日统计 (daily_stats)
    # ==========================================
    
    async def update_daily_stats(self, date: str, sessions: int, hops: int, volume: float):
        """更新每日统计"""
        # 尝试插入，如果存在则更新
        result = self.client.table("daily_stats").select("*").eq("day", date).execute()
        
        if result.data:
            # 更新现有记录
            current = result.data[0]
            self.client.table("daily_stats").update({
                "total_sessions": current["total_sessions"] + sessions,
                "total_hops": current["total_hops"] + hops,
                "total_volume": float(current["total_volume"]) + volume,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("day", date).execute()
        else:
            # 插入新记录
            self.client.table("daily_stats").insert({
                "day": date,
                "total_sessions": sessions,
                "total_hops": hops,
                "total_volume": volume
            }).execute()
    
    async def get_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近 N 天的统计"""
        result = (
            self.client.table("daily_stats")
            .select("*")
            .order("day", desc=True)
            .limit(days)
            .execute()
        )
        return result.data or []


# 全局单例
_supabase_client: Optional[SupabaseClient] = None

def get_supabase_client() -> SupabaseClient:
    """获取 Supabase 客户端单例"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
