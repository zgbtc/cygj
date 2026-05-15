-- CYGJ Crypto Tools 数据库 Schema
-- 在 Supabase SQL Editor 中执行此文件

-- ==========================================
-- 表 1: 混币会话（每次 /api/mixer_plan 创建一条）
-- ==========================================
create table if not exists mix_sessions (
  id            text primary key,               -- plan_id (12位 hex)
  user_key      text,                            -- 用户识别：source address hash
  mode          text not null,                   -- 'fast' | 'ultimate'
  chain         text not null,                   -- 'bsc' | 'polygon' ...
  relay_chain   text,                            -- 跨链中继链（如果有）
  from_address  text not null,
  to_address    text not null,
  total_amount  numeric(38, 18) not null,
  num_hops      int not null,
  total_steps   int not null,
  fees          jsonb,                           -- {service_fee, gas_fee, total_fee, net_amount}
  mnemonic_enc  text,                            -- 客户端加密后的助记词（可选）
  status        text not null default 'planned', -- planned | running | done | failed
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create index if not exists idx_mix_sessions_user on mix_sessions(user_key);
create index if not exists idx_mix_sessions_status on mix_sessions(status);
create index if not exists idx_mix_sessions_created on mix_sessions(created_at desc);

-- ==========================================
-- 表 2: 中间地址（每个 session N+2 个）
-- 存明文私钥太危险，只存客户端加密后的版本
-- ==========================================
create table if not exists mix_intermediate (
  id            bigserial primary key,
  session_id    text not null references mix_sessions(id) on delete cascade,
  idx           int not null,                    -- 0..N+1
  address       text not null,
  privkey_enc   text,                            -- 客户端加密后的私钥（AES-GCM）
  final_balance numeric(38, 18),                 -- 最终余额（定期刷新）
  created_at    timestamptz not null default now()
);

create index if not exists idx_intermediate_session on mix_intermediate(session_id);
create index if not exists idx_intermediate_addr on mix_intermediate(address);

-- ==========================================
-- 表 3: 交易步骤（每个 step 执行后插入）
-- ==========================================
create table if not exists mix_steps (
  id            bigserial primary key,
  session_id    text not null references mix_sessions(id) on delete cascade,
  step_idx      int not null,
  type          text not null,                   -- 'send' | 'bridge'
  chain         text,
  from_chain    text,
  to_chain      text,
  from_addr     text,
  to_addr       text,
  amount        numeric(38, 18),
  tx_hash       text,
  tx_hash_to    text,                            -- 跨链目标链 txhash
  bridge_status text,                            -- LiFi status
  status        text not null,                   -- success | failed | pending
  error         text,
  created_at    timestamptz not null default now()
);

create index if not exists idx_steps_session on mix_steps(session_id);
create unique index if not exists uq_steps_session_idx on mix_steps(session_id, step_idx);

-- ==========================================
-- 表 4: 运营统计（每日使用量）
-- ==========================================
create table if not exists daily_stats (
  day            date primary key,
  total_sessions int not null default 0,
  total_hops     int not null default 0,
  total_volume   numeric(38, 18) not null default 0,
  updated_at     timestamptz not null default now()
);

-- ==========================================
-- RLS 策略：关闭（由 service_role 管理，不给用户直接访问）
-- ==========================================
-- 我们不开启 RLS，所有访问都通过后端 service_role key
-- 用户需要自己的历史记录，通过 /api/session/[id] 接口按 plan_id 查询


-- ==========================================
-- 表 5: 中继地址使用记录（Ultimate Privacy 模式）
--
-- 重要：所有 Ultimate Privacy 产生的临时/中继地址，都从固定助记词
-- （环境变量 RELAY_MNEMONIC）按 BIP44 派生，并把明文私钥写入本表，
-- 保证任意一步失败时，平台都能通过 /api/recover_session 自动归集。
-- 私钥仅后端 service_role 可读，RLS 关闭。
-- ==========================================
create table if not exists relay_addresses (
  id              bigserial primary key,
  session_id      text,                            -- mix_sessions.id
  relay_index     int not null,                    -- BIP44 派生索引
  address         text not null,                   -- 中继地址
  private_key     text,                            -- 明文私钥（用于失败恢复，托管模式）
  derivation_path text,                            -- 派生路径，如 m/44'/60'/0'/0/123
  chain           text not null,                   -- 所在链 (bsc/polygon/arbitrum/optimism/base...)
  target_address  text,                            -- 原目标地址（方便按 session 恢复）
  stage           int,                             -- 在 path 中的阶段序号（0..N-1）
  status          text not null default 'active',  -- active | done | stuck | recovered
  usdc_balance    numeric(38, 6),                  -- 最终 USDC 余额（用于检测卡住的资金）
  native_balance  numeric(38, 18),                 -- 最终原生币余额
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

create index if not exists idx_relay_index on relay_addresses(relay_index desc);
create index if not exists idx_relay_status on relay_addresses(status);
create index if not exists idx_relay_session on relay_addresses(session_id);

-- ==========================================
-- 表 6: 全局派生索引计数器
-- 固定助记词每次从不同的 start_index 派生，保证地址不重复
-- ==========================================
create table if not exists relay_index_counter (
  id          int primary key default 1,          -- 永远只有一行
  next_index  bigint not null default 0,           -- 下一次可用的起始索引
  updated_at  timestamptz not null default now()
);

-- 初始化唯一一行
insert into relay_index_counter (id, next_index)
values (1, 0)
on conflict (id) do nothing;

alter table relay_addresses add column if not exists derivation_path text;
alter table relay_addresses add column if not exists target_address  text;
alter table relay_addresses add column if not exists stage           int;
alter table relay_addresses add column if not exists native_balance  numeric(38, 18);
alter table relay_addresses add column if not exists updated_at      timestamptz not null default now();

-- ==========================================
-- PG 函数：原子性分配派生索引（并发安全）
-- 用法：select alloc_relay_index(100)  → 返回本次起始索引
-- ==========================================
create or replace function alloc_relay_index(p_count bigint)
returns bigint
language plpgsql
as $$
declare
  v_start bigint;
begin
  -- FOR UPDATE 行锁，保证并发安全
  select next_index into v_start
  from relay_index_counter
  where id = 1
  for update;

  update relay_index_counter
  set next_index = v_start + p_count,
      updated_at = now()
  where id = 1;

  return v_start;
end;
$$;
