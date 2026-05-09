import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export const runtime = "nodejs";

export async function GET() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const publishableKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  const result: Record<string, unknown> = {
    timestamp: new Date().toISOString(),
    env: {
      NEXT_PUBLIC_SUPABASE_URL: url ? `✅ ${url}` : "❌ 未设置",
      NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: publishableKey
        ? `✅ ${publishableKey.slice(0, 20)}...`
        : "❌ 未设置",
      SUPABASE_SERVICE_ROLE_KEY: serviceRoleKey
        ? `✅ ${serviceRoleKey.slice(0, 20)}...`
        : "❌ 未设置",
    },
    tests: {} as Record<string, unknown>,
  };

  // 测试 1：用 publishable key 查询（匿名访问）
  if (url && publishableKey) {
    try {
      const client = createClient(url, publishableKey);
      const { data, error } = await client
        .from("mix_sessions")
        .select("count", { count: "exact", head: true });

      if (error) {
        (result.tests as Record<string, unknown>)["publishable_key_query"] = {
          status: "❌ 失败",
          error: error.message,
          code: error.code,
        };
      } else {
        (result.tests as Record<string, unknown>)["publishable_key_query"] = {
          status: "✅ 成功",
          note: "mix_sessions 表可访问",
        };
      }
    } catch (e) {
      (result.tests as Record<string, unknown>)["publishable_key_query"] = {
        status: "❌ 异常",
        error: String(e),
      };
    }
  }

  // 测试 2：用 service_role key 查询（绕过 RLS）
  if (url && serviceRoleKey) {
    try {
      const adminClient = createClient(url, serviceRoleKey);
      const { count, error } = await adminClient
        .from("mix_sessions")
        .select("*", { count: "exact", head: true });

      if (error) {
        (result.tests as Record<string, unknown>)["service_role_query"] = {
          status: "❌ 失败",
          error: error.message,
          code: error.code,
        };
      } else {
        (result.tests as Record<string, unknown>)["service_role_query"] = {
          status: "✅ 成功",
          total_sessions: count ?? 0,
          note: "service_role 权限正常，mix_sessions 表存在",
        };
      }
    } catch (e) {
      (result.tests as Record<string, unknown>)["service_role_query"] = {
        status: "❌ 异常",
        error: String(e),
      };
    }
  }

  // 测试 3：检查所有表是否存在
  if (url && serviceRoleKey) {
    try {
      const adminClient = createClient(url, serviceRoleKey);
      const tables = ["mix_sessions", "mix_intermediate", "mix_steps", "daily_stats"];
      const tableStatus: Record<string, string> = {};

      for (const table of tables) {
        const { error } = await adminClient
          .from(table)
          .select("*", { count: "exact", head: true });
        tableStatus[table] = error
          ? `❌ ${error.message}`
          : "✅ 存在";
      }

      (result.tests as Record<string, unknown>)["tables"] = tableStatus;
    } catch (e) {
      (result.tests as Record<string, unknown>)["tables"] = {
        status: "❌ 异常",
        error: String(e),
      };
    }
  }

  return NextResponse.json(result, { status: 200 });
}
