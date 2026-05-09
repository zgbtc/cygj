"use client";

import { useState } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/config";

type Intermediate = {
  idx: number;
  address: string;
  privkey_enc?: string | null; // 后端字段名保留，内容实为明文私钥
};

type SessionData = {
  session: {
    id: string;
    mode: string;
    chain: string;
    relay_chain?: string;
    from_address: string;
    to_address: string;
    total_amount: number;
    num_hops: number;
    mnemonic_enc?: string; // 后端字段名保留，内容实为明文助记词
    status: string;
    created_at: string;
  };
  intermediate: Intermediate[];
  steps: Array<any>;
};

export default function RecoverPage() {
  const [lang, setLang] = useState<"en" | "zh">("en");
  const [planId, setPlanId] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [session, setSession] = useState<SessionData | null>(null);
  const [showKeys, setShowKeys] = useState(false);
  const [copied, setCopied] = useState<string>("");

  const t = {
    en: {
      title: "Recover Mixing Session",
      subtitle:
        "Enter your Plan ID to retrieve the mnemonic and intermediate address private keys.",
      planId: "Plan ID",
      planIdPh: "12-character hex string",
      submit: "Recover",
      loading: "Loading...",
      sessionInfo: "Session Info",
      from: "From",
      to: "To",
      amount: "Amount",
      hops: "Hops",
      mode: "Mode",
      chain: "Chain",
      status: "Status",
      created: "Created",
      mnemonicTitle: "Mnemonic",
      copy: "Copy",
      copied: "Copied",
      intermediateTitle: "Intermediate Addresses",
      showKeys: "Show Private Keys",
      hideKeys: "Hide Private Keys",
      intermediateHint:
        "Import any of these private keys into MetaMask / imToken / TokenPocket to check and collect residual balance.",
      back: "Back to Home",
      errFetch: "Failed to fetch session",
      errNoData:
        "This session has no mnemonic stored (created before feature enabled)",
      warning:
        "⚠️ Mnemonics and private keys are sensitive. Do not share this page or screenshots with anyone."
    },
    zh: {
      title: "恢复混币会话",
      subtitle: "输入 Plan ID 即可取回助记词和中间地址私钥。",
      planId: "Plan ID",
      planIdPh: "12 位十六进制字符",
      submit: "恢复",
      loading: "加载中...",
      sessionInfo: "会话信息",
      from: "源地址",
      to: "目标地址",
      amount: "金额",
      hops: "跳数",
      mode: "模式",
      chain: "链",
      status: "状态",
      created: "创建时间",
      mnemonicTitle: "助记词",
      copy: "复制",
      copied: "已复制",
      intermediateTitle: "中间地址列表",
      showKeys: "显示私钥",
      hideKeys: "隐藏私钥",
      intermediateHint:
        "任意中间地址私钥导入 MetaMask / imToken / TokenPocket 即可查询和归集残留余额。",
      back: "返回首页",
      errFetch: "会话查询失败",
      errNoData: "该会话没有存储助记词（功能启用前创建）",
      warning: "⚠️ 助记词和私钥是敏感信息，请勿将本页截图或分享给任何人。"
    }
  }[lang];

  const handleRecover = async () => {
    setErr("");
    setSession(null);
    if (!planId.trim()) return;
    setLoading(true);
    try {
      const resp = await fetch(
        `${API_URL}/api/session?id=${encodeURIComponent(planId.trim())}`
      );
      const data = await resp.json();
      if (!data.success) {
        setErr(`${t.errFetch}: ${data.error || resp.status}`);
        return;
      }
      const s = data.data as SessionData;
      setSession(s);
      if (!s.session.mnemonic_enc) {
        setErr(t.errNoData);
      }
    } catch (e) {
      setErr(`${t.errFetch}: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (v: string, tag: string) => {
    await navigator.clipboard.writeText(v);
    setCopied(tag);
    setTimeout(() => setCopied(""), 1500);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <div className="max-w-3xl mx-auto px-4 py-10">
        <div className="flex items-center justify-between mb-8">
          <Link href="/" className="text-[#d4af37] hover:text-[#ffd700] transition">
            ← {t.back}
          </Link>
          <button
            onClick={() => setLang(lang === "en" ? "zh" : "en")}
            className="px-3 py-1 border border-[#d4af37]/40 rounded text-sm text-[#d4af37] hover:bg-[#d4af37]/10"
          >
            {lang === "en" ? "中文" : "English"}
          </button>
        </div>

        <h1 className="text-3xl font-bold text-[#d4af37] mb-2">{t.title}</h1>
        <p className="text-gray-400 mb-4 leading-relaxed">{t.subtitle}</p>
        <p className="text-yellow-400 text-sm mb-8">{t.warning}</p>

        <div className="bg-[#1a1a1a] border border-[#d4af37]/20 rounded-xl p-6 mb-6">
          <label className="block text-sm text-gray-300 mb-2">{t.planId}</label>
          <input
            value={planId}
            onChange={(e) => setPlanId(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleRecover()}
            placeholder={t.planIdPh}
            className="w-full bg-[#0a0a0a] border border-[#d4af37]/30 rounded-lg px-4 py-3 mb-5 focus:outline-none focus:border-[#d4af37] transition font-mono"
          />

          <button
            onClick={handleRecover}
            disabled={loading || !planId}
            className="w-full py-3 rounded-lg bg-[#d4af37] text-black font-semibold hover:bg-[#ffd700] transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? t.loading : t.submit}
          </button>

          {err && (
            <p className="mt-4 text-red-400 text-sm whitespace-pre-wrap">{err}</p>
          )}
        </div>

        {session && (
          <div className="bg-[#1a1a1a] border border-[#d4af37]/20 rounded-xl p-6 mb-6">
            <h2 className="text-xl font-bold text-[#d4af37] mb-4">{t.sessionInfo}</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              <Field label={t.from} value={session.session.from_address} mono />
              <Field label={t.to} value={session.session.to_address} mono />
              <Field
                label={t.amount}
                value={`${session.session.total_amount} ${session.session.chain?.toUpperCase()}`}
              />
              <Field label={t.hops} value={String(session.session.num_hops)} />
              <Field label={t.mode} value={session.session.mode} />
              <Field
                label={t.chain}
                value={
                  session.session.chain +
                  (session.session.relay_chain
                    ? ` → ${session.session.relay_chain} → ${session.session.chain}`
                    : "")
                }
              />
              <Field label={t.status} value={session.session.status} />
              <Field
                label={t.created}
                value={new Date(session.session.created_at).toLocaleString()}
              />
            </div>
          </div>
        )}

        {session?.session.mnemonic_enc && (
          <div className="bg-[#1a1a1a] border border-[#10b981]/40 rounded-xl p-6 mb-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xl font-bold text-[#10b981]">{t.mnemonicTitle}</h2>
              <button
                onClick={() => handleCopy(session.session.mnemonic_enc || "", "mn")}
                className="px-3 py-1 text-sm border border-[#10b981]/50 text-[#10b981] rounded hover:bg-[#10b981]/10"
              >
                {copied === "mn" ? t.copied : t.copy}
              </button>
            </div>
            <p className="font-mono text-[#10b981] break-all bg-[#0a0a0a] p-4 rounded border border-[#10b981]/20">
              {session.session.mnemonic_enc}
            </p>
          </div>
        )}

        {session && session.intermediate.length > 0 && (
          <div className="bg-[#1a1a1a] border border-[#d4af37]/20 rounded-xl p-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xl font-bold text-[#d4af37]">
                {t.intermediateTitle}
              </h2>
              <button
                onClick={() => setShowKeys((v) => !v)}
                className="px-3 py-1 text-sm border border-[#d4af37]/50 text-[#d4af37] rounded hover:bg-[#d4af37]/10"
              >
                {showKeys ? t.hideKeys : t.showKeys}
              </button>
            </div>
            <p className="text-sm text-gray-400 mb-4 leading-relaxed">
              {t.intermediateHint}
            </p>
            <div className="space-y-3 text-sm font-mono">
              {session.intermediate.map((a) => (
                <div
                  key={a.idx}
                  className="py-3 border-b border-gray-800 last:border-0"
                >
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-gray-500 w-10">#{a.idx}</span>
                    <span className="text-gray-200 break-all flex-1">
                      {a.address}
                    </span>
                    <button
                      onClick={() => handleCopy(a.address, `addr-${a.idx}`)}
                      className="text-xs text-[#d4af37] hover:text-[#ffd700]"
                    >
                      {copied === `addr-${a.idx}` ? t.copied : t.copy}
                    </button>
                  </div>
                  {showKeys && a.privkey_enc && (
                    <div className="flex items-center gap-3 pl-14">
                      <span className="text-xs text-gray-600">pk:</span>
                      <span className="text-yellow-300/80 break-all flex-1 text-xs">
                        {a.privkey_enc}
                      </span>
                      <button
                        onClick={() =>
                          handleCopy(a.privkey_enc || "", `pk-${a.idx}`)
                        }
                        className="text-xs text-[#d4af37] hover:text-[#ffd700]"
                      >
                        {copied === `pk-${a.idx}` ? t.copied : t.copy}
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  mono
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className={`text-gray-200 break-all ${mono ? "font-mono text-sm" : ""}`}>
        {value}
      </div>
    </div>
  );
}
