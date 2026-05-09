"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { ArrowLeft, Copy, Key, Search } from "lucide-react";
import { API_URL } from "@/lib/config";

interface LocalSession {
  plan_id: string;
  mnemonic: string;
  from_address: string;
  to_address: string;
  total_amount: number;
  num_hops: number;
  mode: string;
  chain: string;
  relay_chain?: string;
  created_at: string;
}

export default function HistoryPage() {
  const [sessions, setSessions] = useState<LocalSession[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [serverData, setServerData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem('cygj_sessions') || '[]');
      setSessions(stored);
    } catch {}
  }, []);

  const loadServerSession = async (planId: string) => {
    setLoading(true);
    setSelectedId(planId);
    setServerData(null);
    try {
      const r = await fetch(`${API_URL}/api/session?id=${planId}`);
      const d = await r.json();
      if (d.success) setServerData(d.data);
      else setServerData({ error: d.error });
    } catch (e) {
      setServerData({ error: String(e) });
    } finally {
      setLoading(false);
    }
  };

  const copy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 1500);
  };

  const clearAll = () => {
    if (!confirm('Clear all local history? Mnemonics will be lost forever. Server data not affected.')) return;
    localStorage.removeItem('cygj_sessions');
    setSessions([]);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="flex items-center justify-between mb-8">
          <Link href="/" className="flex items-center text-[#d4af37] hover:underline">
            <ArrowLeft className="w-4 h-4 mr-2" /> Back
          </Link>
          <h1 className="text-2xl font-bold">📜 Session History</h1>
          <button
            onClick={clearAll}
            className="text-sm text-red-400 hover:text-red-300"
          >
            Clear Local
          </button>
        </div>

        <div className="bg-[#fff3cd]/10 border border-[#ffd700]/40 rounded-lg p-4 mb-6 text-sm">
          <strong className="text-[#ffd700]">⚠️ Security:</strong> Mnemonics are saved in your browser's localStorage.
          If you clear browser data, they will be lost. Save them elsewhere (password manager, paper).
          The server only stores encrypted data.
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 左侧：本地会话列表 */}
          <div className="bg-[#1a1a1a] border border-[#d4af37]/20 rounded-xl p-4">
            <h2 className="text-lg font-semibold mb-4">Local Sessions ({sessions.length})</h2>
            {sessions.length === 0 ? (
              <p className="text-gray-500 text-sm">No sessions yet. Run a stealth transfer first.</p>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {sessions.map(s => (
                  <div
                    key={s.plan_id}
                    className={`p-3 rounded border cursor-pointer transition ${
                      selectedId === s.plan_id
                        ? 'border-[#d4af37] bg-[#d4af37]/10'
                        : 'border-gray-700 hover:border-[#d4af37]/50'
                    }`}
                    onClick={() => loadServerSession(s.plan_id)}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-[#d4af37] font-mono">{s.plan_id}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(s.created_at).toLocaleString()}
                      </span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-400">{s.mode}</span> · 
                      <span className="text-white ml-1">{s.total_amount} {s.chain.toUpperCase()}</span> · 
                      <span className="text-gray-400 ml-1">{s.num_hops} hops</span>
                      {s.relay_chain && (
                        <span className="ml-1 text-[#10b981]">🌉 via {s.relay_chain.toUpperCase()}</span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 mt-1 truncate">
                      → {s.to_address}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 右侧：会话详情 */}
          <div className="bg-[#1a1a1a] border border-[#d4af37]/20 rounded-xl p-4">
            <h2 className="text-lg font-semibold mb-4">Details</h2>
            {!selectedId ? (
              <p className="text-gray-500 text-sm">Click a session on the left.</p>
            ) : (
              <>
                {(() => {
                  const local = sessions.find(s => s.plan_id === selectedId);
                  if (!local) return null;
                  return (
                    <div className="mb-6 space-y-3">
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Plan ID</div>
                        <div className="font-mono text-sm">{local.plan_id}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-400 mb-1 flex items-center">
                          <Key className="w-3 h-3 mr-1" /> Mnemonic (click to copy)
                        </div>
                        <div
                          className="font-mono text-sm bg-[#0a0a0a] p-3 rounded border border-red-500/30 cursor-pointer break-words"
                          onClick={() => copy(local.mnemonic, 'mnemonic')}
                        >
                          {local.mnemonic}
                          {copied === 'mnemonic' && (
                            <span className="ml-2 text-green-400 text-xs">✓ Copied</span>
                          )}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Source</div>
                        <div className="font-mono text-xs break-all">{local.from_address}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Target</div>
                        <div className="font-mono text-xs break-all">{local.to_address}</div>
                      </div>
                    </div>
                  );
                })()}

                {loading && <p className="text-gray-400">Loading server data...</p>}

                {serverData?.error && (
                  <p className="text-red-400 text-sm">Error: {serverData.error}</p>
                )}

                {serverData?.session && (
                  <div className="border-t border-gray-700 pt-4">
                    <h3 className="text-sm font-semibold mb-2 text-[#d4af37]">
                      Server Record · Status: {serverData.session.status}
                    </h3>
                    <div className="text-xs space-y-1 mb-3">
                      <div>Steps executed: {serverData.steps.length} / {serverData.session.total_steps}</div>
                      <div>Success: {serverData.steps.filter((s: any) => s.status === 'success').length}</div>
                      <div>Failed: {serverData.steps.filter((s: any) => s.status === 'failed').length}</div>
                    </div>

                    <h4 className="text-xs font-semibold mb-1 text-gray-400">Intermediate Addresses</h4>
                    <div className="max-h-40 overflow-y-auto mb-3 space-y-1">
                      {serverData.intermediate.map((a: any) => (
                        <div key={a.idx} className="text-xs font-mono flex items-center">
                          <span className="text-gray-500 w-6">#{a.idx}</span>
                          <span className="flex-1 truncate">{a.address}</span>
                          <button
                            onClick={() => copy(a.address, `addr-${a.idx}`)}
                            className="text-[#d4af37] hover:text-[#ffd700] ml-2"
                          >
                            <Copy className="w-3 h-3" />
                          </button>
                        </div>
                      ))}
                    </div>

                    <h4 className="text-xs font-semibold mb-1 text-gray-400">Transactions</h4>
                    <div className="max-h-60 overflow-y-auto space-y-1">
                      {serverData.steps.map((step: any) => (
                        <div key={step.step_idx} className="text-xs p-2 rounded bg-[#0a0a0a] border border-gray-800">
                          <div className="flex items-center justify-between">
                            <span>
                              #{step.step_idx} {step.type === 'bridge' ? '🌉' : '→'}
                              <span className={step.status === 'success' ? 'text-green-400' : 'text-red-400'}>
                                {' '}{step.status}
                              </span>
                            </span>
                            <span className="text-gray-500">{step.amount}</span>
                          </div>
                          {step.tx_hash && (
                            <a
                              href={`https://bscscan.com/tx/${step.tx_hash}`}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[#d4af37] hover:underline font-mono block truncate"
                            >
                              {step.tx_hash}
                            </a>
                          )}
                          {step.error && (
                            <div className="text-red-400 mt-1">{step.error}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
