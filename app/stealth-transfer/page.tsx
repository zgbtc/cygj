"use client";

import Link from "next/link";
import { useState, useRef, useCallback } from "react";
import { API_URL } from "@/lib/config";
import { Shield, Wallet, ArrowRightLeft, TrendingUp, Globe } from "lucide-react";

// ─── 类型定义 ────────────────────────────────────────────────
interface StepResult {
  step_idx: number;
  next_idx: number;
  done: boolean;
  total_steps: number;
  step: {
    type: "send" | "bridge";
    purpose?: string;
    desc?: string;
    from_chain?: string;
    to_chain?: string;
    chain?: string;
  };
  result: {
    tx_hash?: string;
    tx_hash_to_chain?: string;
    from?: string;
    to?: string;
    amount?: number;
    chain?: string;
    from_chain?: string;
    to_chain?: string;
    bridge_status?: string; // PENDING / DONE / FAILED
    requires_polling?: boolean;
    explorer?: string;
    explorer_from?: string;
    explorer_to?: string;
    early_exit?: boolean;
  };
}

interface Plan {
  plan_id: string;
  mode: string;
  chain: string;
  from_address: string;
  to_address: string;
  total_amount: number;
  num_hops: number;
  fees: {
    service_fee: number;
    gas_fee_estimate: number;
    crosschain_fee: number;
    total_fee: number;
    net_amount: number;
  };
  mnemonic: string;
  from_private_key: string;
  intermediate_keys: { address: string; private_key: string }[];
  relay_chain?: string;
  steps: any[];
  total_steps: number;
}

interface LogLine {
  text: string;
  type: "info" | "success" | "error" | "warn" | "bridge" | "dim";
  link?: string;
}

// ─── 工具函数 ────────────────────────────────────────────────
function purposeIcon(purpose?: string, type?: string): string {
  if (type === "bridge") return "🌉";
  switch (purpose) {
    case "donation": return "💳";
    case "source_isolation": return "🔒";
    case "hop": return "🔀";
    case "cross_out": return "🌉";
    case "cross_back": return "🌉";
    case "cross_back_final": return "🌉";
    case "target_isolation_in": return "🔒";
    case "target_final": return "✅";
    default: return "➡️";
  }
}

function chainLabel(chain?: string): string {
  const map: Record<string, string> = {
    bsc: "BSC", bsc_testnet: "BSC测试网",
    polygon: "Polygon", arbitrum: "Arbitrum",
    optimism: "Optimism", base: "Base", ethereum: "ETH"
  };
  return chain ? (map[chain] || chain.toUpperCase()) : "";
}

// ─── 主组件 ──────────────────────────────────────────────────
export default function StealthTransferPage() {
  const [lang, setLang] = useState<"en" | "zh">("en");
  const [chain, setChain] = useState("bsc_testnet");
  const [mode, setMode] = useState<"fast" | "ultimate">("fast");
  const [inputType, setInputType] = useState<"private_key" | "mnemonic">("private_key");
  const [privateKey, setPrivateKey] = useState("");
  const [mnemonic, setMnemonic] = useState("");
  const [toAddress, setToAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [numHops, setNumHops] = useState(100);
  const [customHops, setCustomHops] = useState("");

  // 执行状态
  const [phase, setPhase] = useState<"idle" | "planning" | "running" | "polling" | "done" | "error">("idle");
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [progress, setProgress] = useState(0); // 0-100
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(0);
  const [finalAmount, setFinalAmount] = useState<number | null>(null);
  const [planRef, setPlanRef] = useState<Plan | null>(null);
  const abortRef = useRef(false);

  // ── 翻译 ──────────────────────────────────────────────────
  const t = {
    en: {
      backHome: "Back to Home", title: "Stealth Transfer Router",
      subtitle: "Professional Privacy Protection Solution",
      userRating: "User Rating", activeUsers: "Active Users",
      howItWorks: "How It Works",
      step1Title: "Generate Intermediate Addresses", step1Desc: "Create temp addresses from mnemonic",
      step2Title: "Multi-hop Transfers", step2Desc: "Funds jump through multiple addresses",
      step3Title: "Collect to Target", step3Desc: "Final funds arrive at destination",
      feeStructure: "Fee Structure", hops: "hops", tip: "Tip:", tipText: "Test on testnet first",
      selectNetwork: "Select Network",
      mainnetWarning: "⚠️ Mainnet: Use ≥0.1 BNB to avoid gas depletion",
      privacyMode: "Privacy Mode",
      fastMode: "⚡ Fast", fastModeDesc: "30s–2min · Single chain · Basic privacy",
      ultimateMode: "🔒 Ultimate", ultimateModeDesc: "3–8min · Cross-chain · Anti-Chainalysis",
      ultimateNote: "Mainnet only · Real cross-chain via LiFi · 4.9% fee",
      inputMethod: "Input Method *", privateKey: "Private Key", mnemonic: "Mnemonic",
      sourcePrivateKey: "Source Private Key *", enterPrivateKey: "Enter private key",
      mnemonicPhrase: "Mnemonic Phrase *", enterMnemonic: "Enter 12 or 24 word mnemonic",
      mnemonicNote: "Uses first address (m/44'/60'/0'/0/0) as source",
      targetAddress: "Target Address *", transferAmount: "Transfer Amount (BNB) *",
      numHops: "Number of Hops:", custom: "Custom",
      serviceFee: "Service Fee", estimatedGas: "Est. Gas",
      totalFee: "Total Fee", expectedReceive: "Expected Receive",
      executeButton: "🚀 Execute", executing: "Executing...",
      fillAllFields: "Please fill all required fields",
      planningTitle: "📋 Planning route...",
      executingTitle: "⚙️ Executing steps",
      doneTitle: "🎉 Complete!",
      errorTitle: "❌ Failed",
      stepOf: "of",
      bridgeWaiting: "⏳ Waiting for cross-chain arrival...",
      received: "Target received:",
      stopButton: "⏹ Stop",
    },
    zh: {
      backHome: "返回首页", title: "鬼魅无影安全转账",
      subtitle: "专业隐私防护方案",
      userRating: "用户评分", activeUsers: "活跃用户",
      howItWorks: "工作原理",
      step1Title: "生成中间地址", step1Desc: "从助记词生成临时地址",
      step2Title: "多跳交叉转账", step2Desc: "资金通过多个地址跳转",
      step3Title: "汇总到目标地址", step3Desc: "最终资金到达目标",
      feeStructure: "费用说明", hops: "跳", tip: "提示：", tipText: "建议先在测试网测试",
      selectNetwork: "选择网络",
      mainnetWarning: "⚠️ 主网建议使用 ≥0.1 BNB，避免 Gas 费用耗尽",
      privacyMode: "隐私模式",
      fastMode: "⚡ 快速模式", fastModeDesc: "30秒-2分钟 · 单链 · 基础隐私",
      ultimateMode: "🔒 极致隐私", ultimateModeDesc: "3-8分钟 · 跨链 · 防 Chainalysis",
      ultimateNote: "仅主网 · LiFi 真实跨链 · 4.9% 服务费",
      inputMethod: "输入方式 *", privateKey: "私钥", mnemonic: "助记词",
      sourcePrivateKey: "源地址私钥 *", enterPrivateKey: "输入私钥",
      mnemonicPhrase: "助记词 *", enterMnemonic: "输入 12 或 24 个单词的助记词",
      mnemonicNote: "将使用第一个地址（m/44'/60'/0'/0/0）作为源地址",
      targetAddress: "目标地址 *", transferAmount: "转账金额 (BNB) *",
      numHops: "跳数:", custom: "自定义",
      serviceFee: "服务费", estimatedGas: "预估 Gas",
      totalFee: "总费用", expectedReceive: "预计收到",
      executeButton: "🚀 执行", executing: "执行中...",
      fillAllFields: "请填写所有必填字段",
      planningTitle: "📋 规划路由中...",
      executingTitle: "⚙️ 逐步执行",
      doneTitle: "🎉 完成！",
      errorTitle: "❌ 执行失败",
      stepOf: "/",
      bridgeWaiting: "⏳ 等待跨链到账...",
      received: "目标地址收到:",
      stopButton: "⏹ 停止",
    }
  };
  const tx = t[lang];

  // ── 日志工具 ──────────────────────────────────────────────
  const addLog = useCallback((text: string, type: LogLine["type"] = "info", link?: string) => {
    setLogs(prev => [...prev, { text, type, link }]);
  }, []);

  // ── 费用计算 ──────────────────────────────────────────────
  const calcFees = () => {
    const amt = parseFloat(amount) || 0;
    if (mode === "ultimate") {
      const svc = amt * 0.049;
      const gas = numHops * 0.00015;
      const cc = 0.006;
      return { svc, gas, cc, total: svc + gas + cc, net: amt - svc - gas - cc };
    } else {
      const hopFeeMap: Record<number, number> = { 10: 0.003, 50: 0.015, 100: 0.03, 500: 0.15, 1000: 0.30 };
      const svc = hopFeeMap[numHops] ?? numHops * 0.0003;
      const gas = numHops * 0.00021;
      return { svc, gas, cc: 0, total: svc + gas, net: amt - svc - gas };
    }
  };
  const fees = calcFees();

  // ── 核心执行逻辑 ─────────────────────────────────────────
  const handleExecute = async () => {
    const inputValue = inputType === "private_key" ? privateKey : mnemonic;
    if (!inputValue || !toAddress || !amount) {
      alert(tx.fillAllFields);
      return;
    }

    abortRef.current = false;
    setLogs([]);
    setProgress(0);
    setCurrentStep(0);
    setTotalSteps(0);
    setFinalAmount(null);
    setPlanRef(null);

    // ── Fast 模式：走老的 /api/mixer 单次调用 ──────────────
    if (mode === "fast") {
      setPhase("running");
      addLog("🚀 " + (lang === "zh" ? "开始快速混币..." : "Starting fast mix..."), "info");
      try {
        const body: any = {
          chain, mode, input_type: inputType,
          to_address: toAddress,
          total_amount: parseFloat(amount),
          num_hops: numHops,
          gas_level: "standard"
        };
        if (inputType === "private_key") body.from_private_key = privateKey;
        else body.from_mnemonic = mnemonic;

        const res = await fetch(`${API_URL}/api/mixer`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body)
        });
        const data = await res.json();

        if (data.success) {
          addLog(lang === "zh" ? `✅ 完成！目标收到 ${data.total_collected} BNB` : `✅ Done! Target received ${data.total_collected} BNB`, "success");
          setFinalAmount(data.total_collected);
          setProgress(100);
          setPhase("done");
        } else {
          addLog(`❌ ${data.error}`, "error");
          setPhase("error");
        }
      } catch (e: any) {
        addLog(`❌ ${e.message}`, "error");
        setPhase("error");
      }
      return;
    }

    // ── Ultimate 模式：mixer_plan + mixer_step 逐步执行 ────
    const STORAGE_KEY = `ultimate_plan_${toAddress.slice(2, 10)}`;

    if (chain.includes("testnet")) {
      addLog(lang === "zh"
        ? "⚠️ 极致隐私模式需要主网（跨链依赖 LiFi），测试网将降级为单链模式"
        : "⚠️ Ultimate mode requires mainnet for real cross-chain. Testnet will use single-chain fallback.",
        "warn");
    }

    // ── 检查 localStorage 是否有未完成的 plan ──────────────
    let plan: Plan | null = null;
    let resumeStepIdx = 0;

    const savedRaw = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
    let isResume = false;
    if (savedRaw) {
      try {
        const saved = JSON.parse(savedRaw);
        if (saved.plan && saved.stepIdx < saved.plan.total_steps) {
          plan = saved.plan;
          resumeStepIdx = saved.stepIdx;
          isResume = true;
          setPlanRef(plan);
          setTotalSteps(plan.total_steps);
          addLog(
            lang === "zh"
              ? `🔄 检测到未完成的执行，从第 ${resumeStepIdx + 1} 步继续...`
              : `🔄 Resuming from step ${resumeStepIdx + 1}...`,
            "warn"
          );
        }
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }

    if (!isResume) {
      // Step 1: 规划
      setPhase("planning");
      addLog(lang === "zh" ? "📋 规划路由，生成中间地址..." : "📋 Planning route, generating addresses...", "info");

      try {
        const planBody: any = {
          mode, chain,
          input_type: inputType,
          to_address: toAddress,
          total_amount: parseFloat(amount),
          num_hops: numHops,
        };
        if (inputType === "private_key") planBody.from_private_key = privateKey;
        else planBody.from_mnemonic = mnemonic;

        const planRes = await fetch(`${API_URL}/api/mixer_plan`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(planBody)
        });
        const planData = await planRes.json();

        if (!planData.success) {
          addLog(`❌ ${planData.error}`, "error");
          setPhase("error");
          return;
        }

        plan = planData.plan;
        setPlanRef(plan);
        setTotalSteps(plan.total_steps);

        // 保存 plan 到 localStorage（不存私钥，只存步骤结构和助记词）
        if (typeof window !== "undefined") {
          const safeplan = { ...plan, from_private_key: "[REDACTED]" };
          localStorage.setItem(STORAGE_KEY, JSON.stringify({ plan: safeplan, stepIdx: 0 }));
        }

        addLog(
          lang === "zh"
            ? `✅ 路由规划完成：${plan.total_steps} 步，${plan.relay_chain ? `跨链经过 ${chainLabel(plan.relay_chain)}` : "单链"}`
            : `✅ Plan ready: ${plan.total_steps} steps${plan.relay_chain ? `, cross-chain via ${chainLabel(plan.relay_chain)}` : ""}`,
          "success"
        );
        if (plan.relay_chain) {
          addLog(
            lang === "zh"
              ? `🌉 跨链路径: ${chainLabel(chain)} → ${chainLabel(plan.relay_chain)} → ${chainLabel(chain)}`
              : `🌉 Path: ${chainLabel(chain)} → ${chainLabel(plan.relay_chain)} → ${chainLabel(chain)}`,
            "bridge"
          );
        }
        addLog(
          lang === "zh"
            ? `💰 服务费 ${plan.fees.service_fee} BNB · Gas ~${plan.fees.gas_fee_estimate} BNB · 预计到账 ${plan.fees.net_amount} BNB`
            : `💰 Fee ${plan.fees.service_fee} BNB · Gas ~${plan.fees.gas_fee_estimate} BNB · Est. receive ${plan.fees.net_amount} BNB`,
          "dim"
        );
        addLog(
          lang === "zh"
            ? `🔑 助记词（请截图保存，资金恢复用）: ${plan.mnemonic}`
            : `🔑 Mnemonic (screenshot this for recovery): ${plan.mnemonic}`,
          "warn"
        );
      } catch (e: any) {
        addLog(`❌ ${lang === "zh" ? "规划失败" : "Planning failed"}: ${e.message}`, "error");
        setPhase("error");
        return;
      }
    }

    // plan 必须已赋值
    if (!plan) {
      addLog(lang === "zh" ? "❌ 内部错误：plan 未初始化" : "❌ Internal error: plan not initialized", "error");
      setPhase("error");
      return;
    }

    // Step 2: 逐步执行
    setPhase("running");
    let stepIdx = resumeStepIdx;
    let bridgePollCount = 0;
    const MAX_BRIDGE_POLLS = 40; // 最多轮询 40 次 × 15s = 10 分钟

    while (stepIdx < plan.total_steps) {
      if (abortRef.current) {
        addLog(lang === "zh" ? "⏹ 用户已停止" : "⏹ Stopped by user", "warn");
        // 保留 localStorage，下次可以继续
        setPhase("error");
        return;
      }

      // 更新 localStorage 进度
      if (typeof window !== "undefined") {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ plan, stepIdx }));
      }

      const step = plan.steps[stepIdx];
      const icon = purposeIcon(step.purpose, step.type);
      const desc = step.desc || `Step ${stepIdx + 1}`;

      setCurrentStep(stepIdx + 1);
      setProgress(Math.round(((stepIdx) / plan.total_steps) * 100));

      addLog(`${icon} [${stepIdx + 1}/${plan.total_steps}] ${desc}`, "info");

      try {
        const stepRes = await fetch(`${API_URL}/api/mixer_step`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ plan, step_idx: stepIdx })
        });

        // Vercel 超时（504）：当作 PENDING 处理，等待后重试
        if (stepRes.status === 504 || stepRes.status === 524) {
          addLog(
            lang === "zh"
              ? `  ⏳ 服务器超时，等待 15 秒后重试...`
              : `  ⏳ Server timeout, retrying in 15s...`,
            "warn"
          );
          await new Promise(r => setTimeout(r, 15000));
          continue; // 重试同一步
        }

        const stepData: StepResult = await stepRes.json();

        if (!stepData.success) {
          addLog(`  ❌ ${(stepData as any).error}`, "error");
          setPhase("error");
          return;
        }

        const r = stepData.result;

        // 紧急降级：跨链失败但资金已发到目标地址
        if (r.type === "emergency_send" || r.bridge_status === "EMERGENCY_FALLBACK") {
          const emergencyChain = (r as any).emergency_chain || step.from_chain || "unknown";
          addLog(
            lang === "zh"
              ? `  ⚠️ 跨链失败，已自动将资金发送到目标地址（${r.amount?.toFixed(6)} ${emergencyChain.toUpperCase()} 原生币）`
              : `  ⚠️ Bridge failed, funds sent to target address (${r.amount?.toFixed(6)} ${emergencyChain.toUpperCase()} native token)`,
            "warn",
            r.explorer || undefined
          );
          if (emergencyChain !== "bsc" && emergencyChain !== chain) {
            addLog(
              lang === "zh"
                ? `  ℹ️ 注意：资金在 ${emergencyChain.toUpperCase()} 链上，需要手动桥回 BSC`
                : `  ℹ️ Note: Funds are on ${emergencyChain.toUpperCase()}, you may need to bridge back to BSC`,
              "warn"
            );
          }
          setFinalAmount(r.amount ?? null);
          setProgress(100);
          setPhase("done");
          if (typeof window !== "undefined") localStorage.removeItem(STORAGE_KEY);
          return;
        }

        // 显示结果
        if (r.tx_hash) {
          const shortHash = r.tx_hash.slice(0, 16) + "...";
          const explorerUrl = r.explorer || r.explorer_from || "";
          addLog(
            `  ✅ tx: ${shortHash}${r.amount ? ` (${r.amount.toFixed(6)} ${r.chain ? chainLabel(r.chain) : ""})` : ""}`,
            "success",
            explorerUrl || undefined
          );
        }

        // 跨链步骤：如果 PENDING，用 poll_tx_hash 模式轮询（不重新发交易）
        if (step.type === "bridge" && r.requires_polling && r.bridge_status === "PENDING") {
          setPhase("polling");
          const bridgeTxHash = r.tx_hash!;
          const fromChain = step.from_chain!;
          const toChain = step.to_chain!;

          addLog(
            lang === "zh"
              ? `  ⏳ 跨链已发出 (${bridgeTxHash.slice(0, 16)}...)，等待 ${chainLabel(toChain)} 到账（最多10分钟）...`
              : `  ⏳ Bridge sent (${bridgeTxHash.slice(0, 16)}...), waiting for ${chainLabel(toChain)} (up to 10 min)...`,
            "bridge"
          );

          bridgePollCount = 0;
          let bridgeDone = false;

          while (bridgePollCount < MAX_BRIDGE_POLLS && !abortRef.current) {
            await new Promise(resolve => setTimeout(resolve, 15000)); // 等 15 秒
            bridgePollCount++;

            try {
              // 纯 poll 模式：传 tx_hash，不重新发交易
              const pollRes = await fetch(`${API_URL}/api/mixer_step`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  poll_tx_hash: bridgeTxHash,
                  poll_from_chain: fromChain,
                  poll_to_chain: toChain
                })
              });
              const pollData = await pollRes.json();
              const pr = pollData.result;

              if (pr?.bridge_status === "DONE") {
                addLog(
                  lang === "zh"
                    ? `  ✅ 跨链到账！${pr.tx_hash_to_chain ? "目标链 tx: " + pr.tx_hash_to_chain.slice(0, 16) + "..." : ""}`
                    : `  ✅ Bridge arrived! ${pr.tx_hash_to_chain ? "Dest tx: " + pr.tx_hash_to_chain.slice(0, 16) + "..." : ""}`,
                  "success",
                  pr.explorer_to || undefined
                );
                bridgeDone = true;
                break;
              } else if (pr?.bridge_status === "FAILED") {
                addLog(lang === "zh" ? "  ❌ 跨链失败" : "  ❌ Bridge failed", "error");
                setPhase("error");
                return;
              } else {
                addLog(
                  lang === "zh"
                    ? `  ⏳ 等待中... (${bridgePollCount * 15}s / 600s)`
                    : `  ⏳ Waiting... (${bridgePollCount * 15}s / 600s)`,
                  "dim"
                );
              }
            } catch {
              // 网络抖动，继续等
            }
          }

          if (!bridgeDone) {
            addLog(
              lang === "zh"
                ? `  ⚠️ 跨链等待超时（10分钟），资金在中间地址，可用助记词恢复\n  助记词: ${planRef?.mnemonic ?? "见规划结果"}`
                : `  ⚠️ Bridge timeout (10 min). Funds in intermediate address.\n  Mnemonic: ${planRef?.mnemonic ?? "see plan"}`,
              "warn"
            );
          }

          setPhase("running");
        }

        // early_exit：资金已直接发到目标，结束
        if (r.early_exit) {
          addLog(
            lang === "zh"
              ? `  ⚡ Gas 预算不足，已直接发送到目标地址 (${r.amount?.toFixed(6)} BNB)`
              : `  ⚡ Gas budget low, sent directly to target (${r.amount?.toFixed(6)} BNB)`,
            "warn"
          );
          setFinalAmount(r.amount ?? null);
          setProgress(100);
          setPhase("done");
          if (typeof window !== "undefined") localStorage.removeItem(STORAGE_KEY);
          return;
        }

        // 最后一步完成
        if (stepData.done) {
          setFinalAmount(r.amount ?? null);
          setProgress(100);
          setPhase("done");
          if (typeof window !== "undefined") localStorage.removeItem(STORAGE_KEY);
          addLog(
            lang === "zh"
              ? `🎉 全部完成！目标地址收到 ${r.amount?.toFixed(6) ?? "?"} BNB`
              : `🎉 All done! Target received ${r.amount?.toFixed(6) ?? "?"} BNB`,
            "success"
          );
          return;
        }

        stepIdx = stepData.next_idx;

      } catch (e: any) {
        addLog(`  ❌ ${e.message}`, "error");
        // 保留 localStorage，下次可以继续
        setPhase("error");
        return;
      }
    }

    setProgress(100);
    if (typeof window !== "undefined") localStorage.removeItem(STORAGE_KEY);
    setPhase("done");
  };

  const handleStop = () => {
    abortRef.current = true;
  };

  const isRunning = phase === "running" || phase === "planning" || phase === "polling";
  const inputValue = inputType === "private_key" ? privateKey : mnemonic;
  const canExecute = !isRunning && !!inputValue && !!toAddress && !!amount;

  // ── 渲染 ─────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <nav className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2 text-purple-600 hover:text-purple-700">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span className="font-semibold">{tx.backHome}</span>
            </Link>
            <button
              onClick={() => setLang(lang === "en" ? "zh" : "en")}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-sm font-medium transition"
            >
              <Globe className="w-4 h-4" />
              {lang === "en" ? "中文" : "EN"}
            </button>
          </div>
        </nav>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* ── 左侧信息栏 ── */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-8">
              <div className="text-center mb-6">
                <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
                  <Shield className="w-12 h-12 text-white" />
                </div>
                <h1 className="text-2xl font-bold mb-2">{tx.title}</h1>
                <p className="text-gray-600 text-sm">{tx.subtitle}</p>
              </div>

              <div className="space-y-4 mb-6">
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">4.8</div>
                  <div className="text-xs text-gray-600">{tx.userRating}</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">1.2K+</div>
                  <div className="text-xs text-gray-600">{tx.activeUsers}</div>
                </div>
              </div>

              <div className="border-t pt-4 mb-4">
                <h3 className="font-semibold mb-3 text-sm">{tx.howItWorks}</h3>
                <div className="space-y-3 text-xs">
                  {[
                    { icon: <Wallet className="w-4 h-4 text-white" />, color: "from-purple-500 to-purple-600", title: tx.step1Title, desc: tx.step1Desc },
                    { icon: <ArrowRightLeft className="w-4 h-4 text-white" />, color: "from-blue-500 to-blue-600", title: tx.step2Title, desc: tx.step2Desc },
                    { icon: <TrendingUp className="w-4 h-4 text-white" />, color: "from-green-500 to-green-600", title: tx.step3Title, desc: tx.step3Desc },
                  ].map((s, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <div className={`w-8 h-8 bg-gradient-to-br ${s.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                        {s.icon}
                      </div>
                      <div>
                        <p className="font-medium">{s.title}</p>
                        <p className="text-gray-500">{s.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 费用表 */}
              <div className="border-t pt-4 mb-4">
                <h3 className="font-semibold mb-3 text-sm">{tx.feeStructure}</h3>
                {mode === "fast" ? (
                  <div className="space-y-2 text-xs">
                    {[10, 50, 100, 500, 1000].map(n => (
                      <div key={n} className={`flex justify-between ${n === 100 ? "bg-purple-50 p-2 rounded" : ""}`}>
                        <span className="text-gray-600">{n} {tx.hops}{n === 100 ? " ⭐" : ""}</span>
                        <span className={`font-semibold ${n === 100 ? "text-purple-600" : ""}`}>
                          {(n * 0.0003).toFixed(3)} BNB
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between"><span className="text-gray-600">&lt; 1 BNB</span><span className="font-semibold">4.9%</span></div>
                    <div className="flex justify-between"><span className="text-gray-600">1–10 BNB</span><span className="font-semibold">4.9%</span></div>
                    <div className="flex justify-between bg-indigo-50 p-2 rounded">
                      <span className="text-gray-600">&gt; 10 BNB ⭐</span>
                      <span className="font-semibold text-indigo-600">4.9%</span>
                    </div>
                    <div className="mt-2 text-gray-500 text-xs">+ 跨链费 ~0.006 BNB</div>
                  </div>
                )}
              </div>

              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 text-xs">
                <p className="text-yellow-700"><strong>{tx.tip}</strong> {tx.tipText}</p>
              </div>
            </div>
          </div>

          {/* ── 右侧操作区 ── */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold mb-6">{tx.title}</h2>

              {/* 网络选择 */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">{tx.selectNetwork}</label>
                <select
                  value={chain}
                  onChange={e => setChain(e.target.value)}
                  disabled={isRunning}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50"
                >
                  <option value="bsc_testnet">BSC Testnet</option>
                  <option value="bsc">BSC Mainnet</option>
                  <option value="eth">Ethereum</option>
                </select>
                {chain === "bsc" && (
                  <p className="text-xs text-orange-600 mt-1">{tx.mainnetWarning}</p>
                )}
              </div>

              {/* 隐私模式 */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">{tx.privacyMode}</label>
                <div className="flex gap-3">
                  {/* Fast */}
                  <button
                    type="button"
                    onClick={() => setMode("fast")}
                    disabled={isRunning}
                    className={`flex-1 p-3 rounded-lg border-2 transition text-left disabled:opacity-50 ${
                      mode === "fast" ? "border-purple-600 bg-purple-50" : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <div className="font-semibold text-sm">{tx.fastMode}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{tx.fastModeDesc}</div>
                  </button>
                  {/* Ultimate */}
                  <button
                    type="button"
                    onClick={() => setMode("ultimate")}
                    disabled={isRunning}
                    className={`flex-1 p-3 rounded-lg border-2 transition text-left disabled:opacity-50 ${
                      mode === "ultimate" ? "border-indigo-600 bg-indigo-50" : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <div className="font-semibold text-sm">{tx.ultimateMode}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{tx.ultimateModeDesc}</div>
                    {mode === "ultimate" && (
                      <div className="text-xs text-indigo-500 mt-1">{tx.ultimateNote}</div>
                    )}
                  </button>
                </div>
              </div>

              {/* 输入方式 */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">{tx.inputMethod}</label>
                <div className="flex gap-4">
                  {(["private_key", "mnemonic"] as const).map(t => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setInputType(t)}
                      disabled={isRunning}
                      className={`flex-1 px-4 py-3 rounded-lg font-medium transition flex items-center justify-center gap-2 disabled:opacity-50 ${
                        inputType === t ? "bg-purple-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {t === "private_key" ? tx.privateKey : tx.mnemonic}
                    </button>
                  ))}
                </div>
              </div>

              {/* 私钥 / 助记词 */}
              {inputType === "private_key" ? (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">{tx.sourcePrivateKey}</label>
                  <input
                    type="password"
                    value={privateKey}
                    onChange={e => setPrivateKey(e.target.value)}
                    placeholder={tx.enterPrivateKey}
                    disabled={isRunning}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                  />
                </div>
              ) : (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">{tx.mnemonicPhrase}</label>
                  <textarea
                    value={mnemonic}
                    onChange={e => setMnemonic(e.target.value)}
                    placeholder={tx.enterMnemonic}
                    rows={3}
                    disabled={isRunning}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                  />
                  <p className="text-xs text-gray-500 mt-1">{tx.mnemonicNote}</p>
                </div>
              )}

              {/* 目标地址 */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">{tx.targetAddress}</label>
                <input
                  type="text"
                  value={toAddress}
                  onChange={e => setToAddress(e.target.value)}
                  placeholder="0x..."
                  disabled={isRunning}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                />
              </div>

              {/* 金额 */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">{tx.transferAmount}</label>
                <input
                  type="number"
                  step="0.001"
                  value={amount}
                  onChange={e => setAmount(e.target.value)}
                  placeholder="0.1"
                  disabled={isRunning}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                />
              </div>

              {/* 跳数 */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {tx.numHops} {numHops}
                </label>
                <div className="flex gap-2 flex-wrap">
                  {[10, 50, 100, 500, 1000].map(n => (
                    <button
                      key={n}
                      onClick={() => { setNumHops(n); setCustomHops(""); }}
                      disabled={isRunning}
                      className={`px-4 py-2 rounded-lg font-medium transition disabled:opacity-50 ${
                        numHops === n && customHops === ""
                          ? "bg-purple-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                  <input
                    type="number"
                    min="3"
                    max="1000"
                    value={customHops}
                    onChange={e => {
                      const v = e.target.value;
                      setCustomHops(v);
                      const n = parseInt(v);
                      if (!isNaN(n)) setNumHops(Math.max(3, Math.min(1000, n)));
                    }}
                    disabled={isRunning}
                    placeholder={tx.custom}
                    className="flex-1 min-w-[80px] px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                  />
                </div>
              </div>

              {/* 费用估算 */}
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">{tx.serviceFee}</p>
                    <p className="font-semibold">{fees.svc.toFixed(5)} BNB{mode === "ultimate" ? " (4.9%)" : ""}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">{tx.estimatedGas}</p>
                    <p className="font-semibold">~{fees.gas.toFixed(5)} BNB</p>
                  </div>
                  <div>
                    <p className="text-gray-600">{tx.totalFee}</p>
                    <p className="font-semibold text-purple-600">~{fees.total.toFixed(5)} BNB</p>
                  </div>
                  <div>
                    <p className="text-gray-600">{tx.expectedReceive}</p>
                    <p className="font-semibold text-green-600">
                      {amount ? Math.max(0, fees.net).toFixed(5) : "0"} BNB
                    </p>
                  </div>
                </div>
              </div>

              {/* 执行按钮 */}
              <div className="flex gap-3">
                <button
                  onClick={handleExecute}
                  disabled={!canExecute}
                  className={`flex-1 py-4 rounded-lg font-semibold text-lg transition flex items-center justify-center gap-2 ${
                    !canExecute
                      ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                      : "bg-purple-600 text-white hover:bg-purple-700"
                  }`}
                >
                  {isRunning ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                      {tx.executing}
                    </>
                  ) : (
                    <>
                      <Shield className="w-5 h-5" />
                      {tx.executeButton}
                    </>
                  )}
                </button>
                {isRunning && (
                  <button
                    onClick={handleStop}
                    className="px-6 py-4 rounded-lg font-semibold bg-red-100 text-red-700 hover:bg-red-200 transition"
                  >
                    {tx.stopButton}
                  </button>
                )}
              </div>
            </div>

            {/* ── 执行进度面板 ── */}
            {(logs.length > 0 || isRunning) && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                {/* 标题 + 进度条 */}
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-sm">
                    {phase === "planning" && tx.planningTitle}
                    {(phase === "running" || phase === "polling") && `${tx.executingTitle} (${currentStep}${tx.stepOf}${totalSteps})`}
                    {phase === "done" && tx.doneTitle}
                    {phase === "error" && tx.errorTitle}
                  </h3>
                  {totalSteps > 0 && (
                    <span className="text-xs text-gray-500">{progress}%</span>
                  )}
                </div>

                {totalSteps > 0 && (
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        phase === "done" ? "bg-green-500" :
                        phase === "error" ? "bg-red-500" :
                        phase === "polling" ? "bg-yellow-400 animate-pulse" :
                        "bg-purple-600"
                      }`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                )}

                {/* 日志终端 */}
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-xs max-h-80 overflow-y-auto space-y-0.5">
                  {logs.map((line, i) => (
                    <div
                      key={i}
                      className={
                        line.type === "success" ? "text-green-400" :
                        line.type === "error" ? "text-red-400" :
                        line.type === "warn" ? "text-yellow-400" :
                        line.type === "bridge" ? "text-cyan-400" :
                        line.type === "dim" ? "text-gray-500" :
                        "text-green-300"
                      }
                    >
                      {line.link ? (
                        <a href={line.link} target="_blank" rel="noopener noreferrer"
                          className="underline hover:text-white">
                          {line.text}
                        </a>
                      ) : line.text}
                    </div>
                  ))}
                  {isRunning && (
                    <div className="flex items-center gap-2 text-gray-400 mt-1">
                      <div className="animate-spin rounded-full h-3 w-3 border-b border-green-400" />
                      <span>{phase === "polling" ? tx.bridgeWaiting : "..."}</span>
                    </div>
                  )}
                </div>

                {/* 完成结果 */}
                {phase === "done" && finalAmount !== null && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-green-800 font-semibold">
                      ✅ {tx.received} <span className="text-green-600">{finalAmount.toFixed(6)} BNB</span>
                    </p>
                  </div>
                )}
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}
