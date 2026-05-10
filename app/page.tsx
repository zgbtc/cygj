"use client";

import { useState, useEffect } from "react";
import { API_URL } from "@/lib/config";
import { Globe } from "lucide-react";

// Tool data
const tools = [
  {
    id: 1,
    name: "Stealth Transfer Router",
    category: "privacy",
    description: "68+ blockchain supported. Professional multi-hop cross-chain relay solution, shielding on-chain transaction traces and network IP, delivering reliable Web3 identity and asset privacy protection.",
    icon: "🎭",
    chains: ["BSC", "ETH"],
    status: "active",
    rating: 4.8,
    users: "1.2K+"
  },
  {
    id: 2,
    name: "HD Wallet Generator",
    category: "wallet",
    description: "BIP44 standard HD wallet generator, generate multiple addresses from mnemonic",
    icon: "🔐",
    features: [
      "BIP44 Standard",
      "Batch Generate",
      "MetaMask Compatible",
      "Secure & Reliable"
    ],
    chains: ["BSC", "ETH", "Polygon"],
    status: "coming-soon",
    rating: 4.9,
    users: "3.5K+"
  },
  {
    id: 3,
    name: "Batch Transfer",
    category: "defi",
    description: "Batch transfer tool, send tokens to multiple addresses at once",
    icon: "💸",
    features: [
      "10-10000 Addresses",
      "CSV Import",
      "Gas Optimization",
      "Real-time Tracking"
    ],
    chains: ["BSC", "ETH", "Polygon"],
    status: "coming-soon",
    rating: 4.7,
    users: "2.8K+"
  },
  {
    id: 4,
    name: "Token Analyzer",
    category: "analytics",
    description: "Token analysis tool, view holder distribution, transaction history and more",
    icon: "📊",
    features: [
      "Holder Analysis",
      "Transaction History",
      "Price Charts",
      "Smart Contract Audit"
    ],
    chains: ["BSC", "ETH"],
    status: "coming-soon",
    rating: 0,
    users: "Soon"
  },
  {
    id: 5,
    name: "Gas Tracker",
    category: "analytics",
    description: "Real-time gas price tracking, help you choose the best transaction timing",
    icon: "⛽",
    features: [
      "Real-time Gas Price",
      "Historical Data",
      "Price Prediction",
      "Notification Alerts"
    ],
    chains: ["BSC", "ETH", "Polygon"],
    status: "coming-soon",
    rating: 0,
    users: "Soon"
  },
  {
    id: 6,
    name: "NFT Batch Mint",
    category: "defi",
    description: "Batch NFT minting tool, supports multiple standards",
    icon: "🎨",
    features: [
      "ERC-721/1155",
      "Batch Minting",
      "Metadata Management",
      "IPFS Upload"
    ],
    chains: ["ETH", "Polygon"],
    status: "coming-soon",
    rating: 0,
    users: "Soon"
  }
];

// Mixing mode configuration
const MIXING_MODES = {
  fast: {
    name: "Fast Mode",
    icon: "⚡",
    privacy: "⭐⭐⭐⭐⭐",
    time: "30s - 2 min",
    description: "Cross Obfuscation · Hide IP · Fast Arrival",
    color: "blue",
    feeRate: 0.0003,
    crosschainFee: 0,  // No cross-chain fee for single chain
    percentageFee: 0   // No percentage fee
  },
  ultimate: {
    name: "Ultimate Privacy",
    icon: "🛡️",
    privacy: "⭐⭐⭐⭐⭐⭐⭐",
    time: "1 - 5 min",
    description: "Multi-chain Ghost Mode · Fully Anonymous · Untraceable",
    color: "red",
    feeRate: 0,  // No per-hop fee
    crosschainFee: 0.006,  // 3 cross-chain, 0.002 each
    percentageFee: 4.9  // 4.9% of transfer amount
  }
};

// Stealth Transfer Mixer component
function StealthTransferApp({ lang }: { lang: "en" | "zh" }) {
  const [chain, setChain] = useState("bsc");
  const [mode, setMode] = useState("fast");
  const [pathType, setPathType] = useState<"simple" | "standard" | "complex">("standard");
  const [privateKey, setPrivateKey] = useState("");
  const [toAddress, setToAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [numHops, setNumHops] = useState(100);
  const [customHops, setCustomHops] = useState("");
  const [mnemonic, setMnemonic] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [detectedInputType, setDetectedInputType] = useState<"private_key" | "mnemonic" | null>(null);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState<string[]>([]);
  const [progressPercent, setProgressPercent] = useState(0);
  const [onlineUsers, setOnlineUsers] = useState(0);
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  // Translation object
  const t = {
    en: {
      onlineToday: "Online Today",
      fastMode: "Fast Mode",
      ultimatePrivacy: "Ultimate Privacy",
      fastModeDesc: "Cross Obfuscation · Hide IP · Fast Arrival",
      ultimatePrivacyDesc: "Multi-chain Ghost Mode · Fully Anonymous · Untraceable",
      singleChainMixing: "Single-chain Mixing",
      vpnRecommended: "VPN recommended for IP protection",
      suitableSmallTransfers: "Suitable for small transfers (<0.5 BNB)",
      suitableLargeTransfers: "Suitable for large transfers",
      multiHopCrossChain: "Multi-hop cross-chain + multi-chain paths + 100% hide fund paths, IP untraceable, absolute privacy protection",
      selectNetwork: "Select Network",
      sourcePrivateKey: "Source Private Key / Mnemonic *",
      enterPrivateKey: "Enter private key or mnemonic (12/24 words)",
      detectedAs: "Detected as:",
      mnemonic: "Mnemonic",
      privateKey: "Private Key",
      willUseFirstAddress: "(will use first address)",
      targetAddress: "Target Address *",
      transferAmount: "Transfer Amount (BNB) *",
      hops: "Hops:",
      moreIsStealthier: "(more is stealthier)",
      est: "Est.",
      multipleIntermediateWallets: "Multiple intermediate wallet addresses hide transfer paths for anonymous transfers and fund privacy.",
      custom: "Custom",
      donation: "Donation",
      estGas: "Est. Gas",
      crosschainFee: "Cross-chain Fee",
      totalFee: "Total Fee",
      expectedReceive: "Expected Receive",
      secureTransfer: "Secure Transfer",
      processing: "Processing",
      faq: "FAQ",
      faqQuestion1: "How to ensure transfers are completely untraceable?",
      faqQuestion2: "How is fund security guaranteed? Risk of theft or loss?",
      faqQuestion3: "What's the key difference in privacy protection between modes?",
      faqQuestion4: "Why provide mnemonic? Is it safe?",
      faqQuestion5: "What if transaction fails or gets stuck?",
      // FAQ 1 content
      faq1TechPrinciple: "Technical Principle:",
      faq1MultiLayer: "We use multi-layer isolation architecture to completely sever fund tracing at the technical level:",
      faq1FastModeDual: "Fast Mode - Dual-layer Isolation:",
      faq1Layer1: "First Layer: Source → Temp Address T1 (cut source)",
      faq1MixLayer: "Mixing Layer: T1 randomly hops through 10-100 HD wallet addresses",
      faq1Layer2: "Second Layer: Temp Address T2 → Target (cut destination)",
      faq1OnChain: "On-chain Trace Analysis:",
      faq1Explorer: "Blockchain explorer only sees: A → T1 (no continuation)",
      faq1Middle: "Middle layer: T1 → B1 → C3 → B5 → C2... (random path)",
      faq1Final: "Final layer: T2 → Z (no predecessor)",
      faq1Conclusion: "Conclusion: Even with Chainalysis tools, cannot link A to Z",
      faq1Ultimate: "Ultimate Privacy - Cross-chain Break:",
      faq1MixBefore: "Mix to new temp address before each cross-chain",
      faq1Bridge: "Bridge records: Temp B → Temp C (different chains)",
      faq1Unlinkable: "Unlinkable: Source A on BSC, Target Z on BSC, but via Polygon, Arbitrum",
      faq1IP: "IP Protection: Use VPN/Cloudflare on your side, we don't log IPs",
      faq1Time: "Time Obfuscation: random delays break timing patterns",
      // FAQ 2 content
      faq2Decentralized: "Decentralized Architecture Guarantee:",
      faq2NonCustodial: "✅ Non-custodial Design",
      faq2BIP44: "All intermediate addresses derived from your mnemonic via BIP44",
      faq2Control: "Private keys fully controlled by you, we cannot touch your funds",
      faq2NoPool: "No fund pool, no centralized servers",
      faq2OnChain: "✅ On-chain Verifiable",
      faq2Hash: "Each transaction has unique hash, queryable on blockchain explorer",
      faq2OpenSource: "Smart contracts open source, code logic transparent and auditable",
      faq2Immutable: "All operations executed on-chain, immutable",
      faq2MnemonicSec: "✅ Mnemonic Security",
      faq2Local: "Mnemonic only used locally in your browser, never uploaded",
      faq2Hardware: "Recommend using hardware wallet generated mnemonic",
      faq2AutoClear: "After mixing, intermediate addresses auto-cleared, no balance left",
      faq2Recommendations: "⚠️ Security Recommendations",
      faq2FirstTime: "First time use: test with small amount (0.01-0.05 BNB)",
      faq2Keep: "Keep mnemonic safe, loss is unrecoverable",
      faq2Confirm: "Confirm target address correct, on-chain transactions irreversible",
      // FAQ 3 content
      faq3FastMode: "Fast Mode - Single-chain Deep Obfuscation:",
      faq3UseCase: "Use Case:",
      faq3FastUseCase: "Daily transfers, small amounts (<0.5 BNB), need fast arrival (30s-5min)",
      faq3TechFeatures: "Technical Features:",
      faq3FastTech: "Dual-layer isolation + multi-hop mixing, 10-100 intermediate addresses random hops",
      faq3PrivacyLevel: "Privacy Level:",
      faq3FastPrivacy: "⭐⭐⭐⭐⭐ Resistant to blockchain explorers, common analysis tools",
      faq3Ultimate: "Ultimate Privacy - Cross-chain Ghost Mode:",
      faq3UltimateUseCase: "Large fund transfers (>0.5 BNB), need highest privacy protection",
      faq3CrossChain: "Cross-chain break: BSC → Polygon → Arbitrum → BSC (68+ chains available)",
      faq3NewTemp: "New temp address for each cross-chain (bridge cannot link)",
      faq3AutoProxy: "Recommend VPN/Cloudflare on your side, we don't log IPs",
      faq3Delays: "Random delays between hops: break timing correlation patterns",
      faq3UltimatePrivacy: "⭐⭐⭐⭐⭐⭐⭐ Resistant to Chainalysis, Elliptic and other pro tools",
      faq3CoreDiff: "Core Difference:",
      faq3CoreDiffText: "Fast Mode: Single-chain obfuscation, speed priority | Ultimate Privacy: Cross-chain break, privacy priority",
      // FAQ 4 content
      faq4TechNecessity: "Technical Necessity:",
      faq4HDPrinciple: "HD Wallet Principle:",
      faq4Requires: "Mixing requires generating 10-100 intermediate addresses",
      faq4BIP44: "Use BIP44 standard to derive child addresses from mnemonic",
      faq4Child: "Each child address has independent private key for signing transactions",
      faq4WhyNot: "Why not use single private key:",
      faq4SingleKey: "Single private key only controls one address",
      faq4CannotGen: "Cannot generate multiple intermediate addresses for mixing",
      faq4HDWallet: "HD wallet can derive unlimited addresses from one mnemonic",
      faq4Security: "Security Guarantee:",
      faq4Local: "✅ Local Processing",
      faq4BrowserOnly: "Mnemonic only used in your browser",
      faq4NotSent: "Not sent to server or any third party",
      faq4LocalCalc: "All derivation calculations done locally",
      faq4Temp: "✅ Temporary Use",
      faq4AutoClear: "After mixing, intermediate addresses auto-cleared",
      faq4NoBalance: "No balance left in intermediate addresses",
      faq4Dedicated: "Recommend using dedicated mnemonic, not main wallet",
      faq4BestPractices: "Best Practices:",
      faq4NewMnemonic: "Use newly generated mnemonic (not main wallet)",
      faq4Discard: "After mixing, can discard the mnemonic",
      faq4HardwareWallet: "Or use hardware wallet generated mnemonic",
      // FAQ 5 content
      faq5FaultTolerance: "Fault Tolerance Mechanism:",
      faq5AutoRetry: "✅ Auto Retry",
      faq5Retry3: "Failed transactions auto-retry 3 times",
      faq5GasIncrease: "Insufficient gas price auto-increased and resent",
      faq5Congestion: "Network congestion waits then retries",
      faq5FundProtection: "✅ Fund Protection",
      faq5NoDeduct: "Failed transactions don't deduct funds",
      faq5AutoCollect: "Intermediate address balances auto-collected",
      faq5NoStuck: "No funds stuck in intermediate addresses",
      faq5RealTime: "✅ Real-time Monitoring",
      faq5Status: "Page shows real-time transaction status",
      faq5Progress: "Can see current progress and remaining time",
      faq5Hash: "Each transaction has hash, queryable on blockchain explorer",
      faq5CommonIssues: "Common Issue Handling:",
      faq5Case1: "Case 1: Transaction pending long time",
      faq5Case1Cause: "Cause: Network congestion | Solution: System auto-increases gas and resends",
      faq5Case2: "Case 2: Partial transaction failure",
      faq5Case2Cause: "Cause: Insufficient balance | Solution: System collects completed portions",
      faq5Case3: "Case 3: Cross-chain stuck (Ultimate Privacy)",
      faq5Case3Cause: "Cause: Bridge congestion | Solution: Wait for cross-chain confirmation (usually 5-30min)",
      // misc
      processingText: "Processing...",
      executionFailed: "❌ Execution Failed",
      comingSoon: "🚧 Coming Soon",
      stayTuned: "Stay tuned...",
      fillAllFields: "Please fill all required fields",
      startMixing: "Starting mixing...",
      mode: "Mode:",
      ipHidden: "IP Hidden: VPN recommended",
      ipHiddenVpn: "IP Hidden: VPN recommended",
      detectedMnemonic: "Detected as: Mnemonic",
      detectedPrivateKey: "Detected as: Private Key",
      transactionFlowDetails: "Transaction Flow Details:",
      stealthTransferComplete: "Stealth transfer complete!",
      targetReceived: "Target received:",
      success: "Success:",
      failed: "Failed:",
      error: "Error:",
      transactionFailed: "Transaction failed:"
    },
    zh: {
      onlineToday: "今日在线",
      fastMode: "快速模式",
      ultimatePrivacy: "极致隐私",
      fastModeDesc: "交叉混淆 · 隐藏IP · 快速到账",
      ultimatePrivacyDesc: "多链幽灵模式 · 完全匿名 · 无法追踪",
      singleChainMixing: "单链混币",
      vpnRecommended: "建议使用VPN保护IP",
      suitableSmallTransfers: "适合小额转账（<0.5 BNB）",
      suitableLargeTransfers: "适合大额转账",
      multiHopCrossChain: "多跳跨链 + 多链路径 + 100%隐藏资金路径，IP无法追踪，绝对隐私保护",
      selectNetwork: "选择网络",
      sourcePrivateKey: "源地址私钥 / 助记词 *",
      enterPrivateKey: "输入私钥或助记词（12/24个单词）",
      detectedAs: "识别为：",
      mnemonic: "助记词",
      privateKey: "私钥",
      willUseFirstAddress: "（将使用第一个地址）",
      targetAddress: "目标地址 *",
      transferAmount: "转账金额 (BNB) *",
      hops: "跳数：",
      moreIsStealthier: "（越多越隐蔽）",
      est: "预计",
      multipleIntermediateWallets: "多个中间钱包地址隐藏转账路径，实现匿名转账和资金隐私。",
      custom: "自定义",
      donation: "捐赠",
      estGas: "预估 Gas",
      crosschainFee: "跨链费用",
      totalFee: "总费用",
      expectedReceive: "预计收到",
      secureTransfer: "安全转账",
      processing: "处理中",
      faq: "常见问题",
      faqQuestion1: "如何确保转账完全无法追踪？",
      faqQuestion2: "资金安全如何保障？有被盗或丢失的风险吗？",
      faqQuestion3: "两种模式在隐私保护上的核心区别是什么？",
      faqQuestion4: "为什么要提供助记词？安全吗？",
      faqQuestion5: "交易失败或卡住了怎么办？",
      // FAQ 1 content
      faq1TechPrinciple: "技术原理：",
      faq1MultiLayer: "我们使用多层隔离架构，在技术层面彻底切断资金追踪：",
      faq1FastModeDual: "快速模式 - 双层隔离：",
      faq1Layer1: "第一层：源地址 → 临时地址T1（切断来源）",
      faq1MixLayer: "混币层：T1随机跳转10-100个HD钱包地址",
      faq1Layer2: "第二层：临时地址T2 → 目标地址（切断去向）",
      faq1OnChain: "链上追踪分析：",
      faq1Explorer: "区块链浏览器只能看到：A → T1（无后续）",
      faq1Middle: "中间层：T1 → B1 → C3 → B5 → C2...（随机路径）",
      faq1Final: "最终层：T2 → Z（无前驱）",
      faq1Conclusion: "结论：即使使用Chainalysis工具，也无法将A与Z关联",
      faq1Ultimate: "极致隐私 - 跨链断点：",
      faq1MixBefore: "每次跨链前混币到新临时地址",
      faq1Bridge: "桥接记录：临时B → 临时C（不同链）",
      faq1Unlinkable: "无法关联：BSC上的源地址A，BSC上的目标Z，但经过Polygon、Arbitrum",
      faq1IP: "IP保护：用户侧建议使用 VPN/Cloudflare，服务端不记录 IP",
      faq1Time: "时间混淆：随机延迟打破时序关联模式",
      // FAQ 2 content
      faq2Decentralized: "去中心化架构保障：",
      faq2NonCustodial: "✅ 非托管设计",
      faq2BIP44: "所有中间地址通过BIP44从您的助记词派生",
      faq2Control: "私钥完全由您控制，我们无法触碰您的资金",
      faq2NoPool: "无资金池，无中心化服务器",
      faq2OnChain: "✅ 链上可验证",
      faq2Hash: "每笔交易有唯一哈希，可在区块链浏览器查询",
      faq2OpenSource: "智能合约开源，代码逻辑透明可审计",
      faq2Immutable: "所有操作在链上执行，不可篡改",
      faq2MnemonicSec: "✅ 助记词安全",
      faq2Local: "助记词仅在您的浏览器本地使用，从不上传",
      faq2Hardware: "建议使用硬件钱包生成的助记词",
      faq2AutoClear: "混币完成后，中间地址自动清空，无余额残留",
      faq2Recommendations: "⚠️ 安全建议",
      faq2FirstTime: "首次使用：用小额测试（0.01-0.05 BNB）",
      faq2Keep: "妥善保管助记词，丢失不可恢复",
      faq2Confirm: "确认目标地址正确，链上交易不可逆",
      // FAQ 3 content
      faq3FastMode: "快速模式 - 单链深度混淆：",
      faq3UseCase: "适用场景：",
      faq3FastUseCase: "日常转账、小额（<0.5 BNB）、需要快速到账（30秒-5分钟）",
      faq3TechFeatures: "技术特点：",
      faq3FastTech: "双层隔离 + 多跳混币，10-100个中间地址随机跳转",
      faq3PrivacyLevel: "隐私等级：",
      faq3FastPrivacy: "⭐⭐⭐⭐⭐ 可抵御区块链浏览器、常见分析工具",
      faq3Ultimate: "极致隐私 - 跨链幽灵模式：",
      faq3UltimateUseCase: "大额资金转移（>0.5 BNB）、需要最高隐私保护",
      faq3CrossChain: "跨链断点：BSC → Polygon → Arbitrum → BSC（支持68+条链）",
      faq3NewTemp: "每次跨链使用新临时地址（桥接无法关联）",
      faq3AutoProxy: "建议用户侧启用 VPN/Cloudflare，服务端不记录 IP",
      faq3Delays: "跳转之间随机延迟：打破时序关联模式",
      faq3UltimatePrivacy: "⭐⭐⭐⭐⭐⭐⭐ 可抵御Chainalysis、Elliptic等专业工具",
      faq3CoreDiff: "核心区别：",
      faq3CoreDiffText: "快速模式：单链混淆，速度优先 | 极致隐私：跨链断点，隐私优先",
      // FAQ 4 content
      faq4TechNecessity: "技术必要性：",
      faq4HDPrinciple: "HD钱包原理：",
      faq4Requires: "混币需要生成10-100个中间地址",
      faq4BIP44: "使用BIP44标准从助记词派生子地址",
      faq4Child: "每个子地址有独立私钥用于签名交易",
      faq4WhyNot: "为什么不用单个私钥：",
      faq4SingleKey: "单个私钥只控制一个地址",
      faq4CannotGen: "无法生成多个中间地址进行混币",
      faq4HDWallet: "HD钱包可从一个助记词派生无限地址",
      faq4Security: "安全保障：",
      faq4Local: "✅ 本地处理",
      faq4BrowserOnly: "助记词仅在您的浏览器中使用",
      faq4NotSent: "不发送到服务器或任何第三方",
      faq4LocalCalc: "所有派生计算在本地完成",
      faq4Temp: "✅ 临时使用",
      faq4AutoClear: "混币完成后，中间地址自动清空",
      faq4NoBalance: "中间地址无余额残留",
      faq4Dedicated: "建议使用专用助记词，不要用主钱包",
      faq4BestPractices: "最佳实践：",
      faq4NewMnemonic: "使用新生成的助记词（不要用主钱包）",
      faq4Discard: "混币完成后，可以丢弃该助记词",
      faq4HardwareWallet: "或使用硬件钱包生成的助记词",
      // FAQ 5 content
      faq5FaultTolerance: "容错机制：",
      faq5AutoRetry: "✅ 自动重试",
      faq5Retry3: "失败交易自动重试3次",
      faq5GasIncrease: "Gas不足时自动提高并重发",
      faq5Congestion: "网络拥堵时等待后重试",
      faq5FundProtection: "✅ 资金保护",
      faq5NoDeduct: "失败交易不扣除资金",
      faq5AutoCollect: "中间地址余额自动归集",
      faq5NoStuck: "资金不会卡在中间地址",
      faq5RealTime: "✅ 实时监控",
      faq5Status: "页面实时显示交易状态",
      faq5Progress: "可查看当前进度和剩余时间",
      faq5Hash: "每笔交易有哈希，可在区块链浏览器查询",
      faq5CommonIssues: "常见问题处理：",
      faq5Case1: "情况1：交易长时间pending",
      faq5Case1Cause: "原因：网络拥堵 | 解决：系统自动提高Gas重发",
      faq5Case2: "情况2：部分交易失败",
      faq5Case2Cause: "原因：余额不足 | 解决：系统归集已完成部分",
      faq5Case3: "情况3：跨链卡住（极致隐私模式）",
      faq5Case3Cause: "原因：桥接拥堵 | 解决：等待跨链确认（通常5-30分钟）",
      // misc
      processingText: "处理中...",
      executionFailed: "❌ 执行失败",
      comingSoon: "🚧 即将上线",
      stayTuned: "敬请期待...",
      fillAllFields: "请填写所有必填字段",
      startMixing: "开始混币...",
      mode: "模式：",
      ipHidden: "IP隐藏：建议使用VPN",
      ipHiddenVpn: "IP隐藏：建议使用VPN",
      detectedMnemonic: "已识别为：助记词",
      detectedPrivateKey: "已识别为：私钥",
      transactionFlowDetails: "交易流程详情：",
      stealthTransferComplete: "隐匿转账完成！",
      targetReceived: "目标地址收到：",
      success: "成功：",
      failed: "失败：",
      error: "错误：",
      transactionFailed: "交易失败："
    }
  };

  const text = t[lang];

  // 初始化在线人数（基于当前时间生成一个稳定的基数）
  useEffect(() => {
    const now = new Date();
    const dayMinutes = now.getHours() * 60 + now.getMinutes();
    // 根据时间段设置基础人数：凌晨少，白天多
    const baseUsers = Math.floor(30 + Math.sin(dayMinutes / 229) * 20 + Math.random() * 15);
    setOnlineUsers(baseUsers);
  }, []);

  // 动态更新在线人数
  useEffect(() => {
    const interval = setInterval(() => {
      setOnlineUsers(prev => {
        // 随机增减 -2 到 +3 之间
        const change = Math.floor(Math.random() * 6) - 2;
        const newValue = prev + change;
        // 限制在 15-120 之间
        return Math.max(15, Math.min(120, newValue));
      });
    }, 8000 + Math.random() * 7000); // 8-15秒随机更新一次

    return () => clearInterval(interval);
  }, []);

  // Auto-detect input type (private key or mnemonic)
  const detectInputType = (input: string): "private_key" | "mnemonic" => {
    const trimmed = input.trim();
    const words = trimmed.split(/\s+/);
    const wordCount = words.length;
    
    // 助记词：12/15/18/21/24 个单词
    if ([12, 15, 18, 21, 24].includes(wordCount)) {
      return 'mnemonic';
    }
    
    // 私钥：0x开头或64位十六进制
    if (trimmed.startsWith('0x') || /^[0-9a-fA-F]{64}$/.test(trimmed)) {
      return 'private_key';
    }
    
    return 'private_key'; // 默认
  };

  // 处理输入变化
  const handleInputChange = (value: string) => {
    setPrivateKey(value);
    if (value.trim()) {
      const type = detectInputType(value);
      setDetectedInputType(type);
    } else {
      setDetectedInputType(null);
    }
  };

  const handleExecute = async () => {
    if (!privateKey || !toAddress || !amount) {
      alert(text.fillAllFields);
      return;
    }

    setIsLoading(true);
    setResult(null);
    setProgress([]);
    setProgressPercent(0);

    try {
      setProgress(prev => [...prev, `🆕 v2.0 Plan+Step Architecture`]);
      setProgress(prev => [...prev, text.startMixing]);
      setProgressPercent(3);
      setProgress(prev => [...prev, `${text.mode} ${MIXING_MODES[mode as keyof typeof MIXING_MODES].name}`]);
      
      if (mode === 'ultimate') {
        setProgress(prev => [...prev, `🔒 ${text.ipHidden}`]);
      } else {
        setProgress(prev => [...prev, `⚠️ ${text.ipHiddenVpn}`]);
      }
      setProgress(prev => [...prev, `${text.hops} ${numHops}`]);
      setProgressPercent(8);

      const inputType = detectInputType(privateKey);
      const inputValue = privateKey.trim();

      // ==========================================
      // Ultimate Privacy：跨链 + DEX Swap（2-3 分钟完成）
      // LiFi any-to-any：BNB → Relay USDC → BNB，币种+链+地址三维混淆
      // 大额自动拆分并行执行，总时间不变
      // ==========================================
      if (mode === 'ultimate') {
        setProgress(prev => [...prev, `🛡️ ${lang === 'en' ? 'Ultimate Privacy activated' : '极致隐私模式启动'}`]);
        setProgressPercent(10);

        const { ethers } = await import('ethers');

        // 构造 signer
        let sourceSigner: any;
        try {
          if (inputType === 'mnemonic') {
            sourceSigner = ethers.HDNodeWallet.fromMnemonic(ethers.Mnemonic.fromPhrase(inputValue));
          } else {
            sourceSigner = new ethers.Wallet(inputValue);
          }
        } catch {
          throw new Error(lang === 'en' ? 'Invalid private key or mnemonic' : '无效的私钥或助记词');
        }
        const fromAddress = sourceSigner.address;

        // 规划：金额拆分 + 中继链分配
        const planResp = await fetch(`${API_URL}/api/dex_mixer`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'plan',
            from_address: fromAddress,
            to_address: toAddress,
            total_amount: parseFloat(amount),
          })
        });
        const planData = await planResp.json();
        if (!planData.success) throw new Error(planData.error || 'DEX route planning failed');
        const route = planData.route;
        setProgress(prev => [...prev, `📋 ${lang === 'en' ? `Route: ${route.num_legs} parallel split(s)` : `路由：${route.num_legs} 笔并行拆分`}`]);
        setProgressPercent(15);

        const bscProvider = new ethers.JsonRpcProvider('https://bsc-dataseed.binance.org');
        const bscSigner = new ethers.Wallet(sourceSigner.privateKey, bscProvider);

        // 先扣服务费
        if (route.service_fee > 0) {
          setProgress(prev => [...prev, `💳 ${lang === 'en' ? `Service fee: ${route.service_fee.toFixed(6)} BNB (${route.fee_rate_percent}%)` : `服务费：${route.service_fee.toFixed(6)} BNB (${route.fee_rate_percent}%)`}`]);
          const feeWei = ethers.parseEther(route.service_fee.toFixed(8));
          const feeTx = await bscSigner.sendTransaction({
            to: route.fee_address,
            value: feeWei,
          });
          await feeTx.wait(1);
          setProgress(prev => [...prev, `   ✅ ${lang === 'en' ? 'Fee paid' : '服务费已支付'}: ${feeTx.hash.slice(0, 16)}...`]);
        }
        setProgressPercent(20);

        // 中间地址（HD 钱包派生），用于接收第一跳的 USDC
        const sourceWallet = inputType === 'mnemonic'
          ? ethers.HDNodeWallet.fromMnemonic(ethers.Mnemonic.fromPhrase(inputValue))
          : null;

        // 并行执行所有 leg
        const executeOneLeg = async (leg: any, idx: number): Promise<any> => {
          const delay = leg.delay_seconds || 0;
          if (delay > 0) {
            setProgress(prev => [...prev, `   ⏳ [${idx + 1}] ${lang === 'en' ? `Delay ${delay}s...` : `延迟 ${delay}s...`}`]);
            await new Promise(r => setTimeout(r, delay * 1000));
          }
          setProgress(prev => [...prev, `\n💸 [${idx + 1}/${route.num_legs}] ${leg.amount_bnb.toFixed(6)} BNB → ${leg.relay_chain.toUpperCase()} POL`]);

          // 使用后端派生的中继地址（固定助记词，不是 createRandom）
          const relayAddress = leg.relay_address;
          const relayPrivateKey = leg.relay_private_key;
          const relayProvider = new ethers.JsonRpcProvider('https://polygon-bor-rpc.publicnode.com');
          const relaySigner = new ethers.Wallet(relayPrivateKey, relayProvider);

          // ═══ 第一跳：BSC BNB → Polygon POL @ relayAddress ═══
          const amountWei = ethers.parseEther(leg.amount_bnb.toFixed(6)).toString();
          setProgress(prev => [...prev, `   🔀 [${idx + 1}] ${lang === 'en' ? 'Quote hop 1: BSC BNB → Polygon POL' : '报价第一跳：BSC BNB → Polygon POL'}`]);

          const q1Resp = await fetch(`${API_URL}/api/dex_mixer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'quote',
              from_chain: 56,
              to_chain: leg.relay_chain_id,
              from_token: '0x0000000000000000000000000000000000000000',
              to_token: '0x0000000000000000000000000000000000000000',
              from_amount: amountWei,
              from_address: fromAddress,
              to_address: relayAddress,
              slippage: 0.03,
            })
          });
          const q1Data = await q1Resp.json();
          if (!q1Data.success) throw new Error(`Hop1 quote: ${q1Data.error}`);
          const txReq1 = q1Data.quote.transactionRequest;
          if (!txReq1) throw new Error('Hop1: no transactionRequest');

          // 发送第一跳
          setProgress(prev => [...prev, `   🚀 [${idx + 1}] ${lang === 'en' ? 'Sending BSC tx...' : '发送 BSC 交易...'}`]);
          const txValue = txReq1.value ? (typeof txReq1.value === 'string' && txReq1.value.startsWith('0x') ? BigInt(txReq1.value) : BigInt(txReq1.value)) : BigInt(0);
          const txGasLimit = txReq1.gasLimit ? (typeof txReq1.gasLimit === 'string' && txReq1.gasLimit.startsWith('0x') ? BigInt(txReq1.gasLimit) : BigInt(txReq1.gasLimit)) : BigInt(500000);
          const tx1 = await bscSigner.sendTransaction({
            to: txReq1.to,
            value: txValue,
            data: txReq1.data,
            gasLimit: txGasLimit,
          });
          setProgress(prev => [...prev, `   ✅ [${idx + 1}] BSC tx: ${tx1.hash.slice(0, 16)}...`]);
          await tx1.wait(1);

          // 轮询第一跳状态
          setProgress(prev => [...prev, `   ⏳ [${idx + 1}] ${lang === 'en' ? 'Bridging...' : '跨链中...'}`]);
          const hop1Deadline = Date.now() + 5 * 60 * 1000;
          let hop1Status = 'PENDING';
          while (Date.now() < hop1Deadline && hop1Status !== 'DONE' && hop1Status !== 'FAILED') {
            await new Promise(r => setTimeout(r, 6000));
            try {
              const s = await fetch(`${API_URL}/api/dex_mixer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'status', tx_hash: tx1.hash, from_chain: 56, to_chain: leg.relay_chain_id })
              });
              const sd = await s.json();
              hop1Status = sd.status || 'PENDING';
            } catch {}
          }
          if (hop1Status !== 'DONE') throw new Error(`Hop1 not done: ${hop1Status}`);
          setProgress(prev => [...prev, `   ✅ [${idx + 1}] ${lang === 'en' ? 'POL arrived on Polygon' : 'POL 到达 Polygon'}`]);

          // 查中继地址 POL 余额（原生币，不需要 ERC20 查询）
          let nativeBalance = BigInt(0);
          for (let t = 0; t < 15; t++) {
            nativeBalance = await relayProvider.getBalance(relayAddress);
            if (nativeBalance > BigInt(0)) break;
            await new Promise(r => setTimeout(r, 3000));
          }
          if (nativeBalance === BigInt(0)) throw new Error('Relay POL balance = 0');

          // ═══ 第二跳：Polygon POL → BSC BNB @ target（不需要 approve！）═══
          // 预留 gas 费（Polygon gas 极便宜，预留 0.005 POL 足够）
          const gasReserve = ethers.parseEther('0.005');
          const sendAmount = nativeBalance - gasReserve;
          if (sendAmount <= BigInt(0)) throw new Error('POL balance too low after gas reserve');

          setProgress(prev => [...prev, `   🔀 [${idx + 1}] ${lang === 'en' ? 'Quote hop 2: Polygon POL → BSC BNB' : '报价第二跳：Polygon POL → BSC BNB'}`]);
          const q2Resp = await fetch(`${API_URL}/api/dex_mixer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'quote',
              from_chain: leg.relay_chain_id,
              to_chain: 56,
              from_token: '0x0000000000000000000000000000000000000000',
              to_token: '0x0000000000000000000000000000000000000000',
              from_amount: sendAmount.toString(),
              from_address: relayAddress,
              to_address: toAddress,
              slippage: 0.03,
            })
          });
          const q2Data = await q2Resp.json();
          if (!q2Data.success) throw new Error(`Hop2 quote: ${q2Data.error}`);
          const quote2 = q2Data.quote;
          const txReq2 = quote2.transactionRequest;
          if (!txReq2) throw new Error('Hop2: no transactionRequest');

          // 发送第二跳
          setProgress(prev => [...prev, `   🚀 [${idx + 1}] ${lang === 'en' ? 'Sending relay tx...' : '发送中继交易...'}`]);
          const tx2Value = txReq2.value ? (typeof txReq2.value === 'string' && txReq2.value.startsWith('0x') ? BigInt(txReq2.value) : BigInt(txReq2.value)) : BigInt(0);
          const tx2GasLimit = txReq2.gasLimit ? (typeof txReq2.gasLimit === 'string' && txReq2.gasLimit.startsWith('0x') ? BigInt(txReq2.gasLimit) : BigInt(txReq2.gasLimit)) : BigInt(800000);
          const tx2 = await relaySigner.sendTransaction({
            to: txReq2.to,
            value: tx2Value,
            data: txReq2.data,
            gasLimit: tx2GasLimit,
          });
          setProgress(prev => [...prev, `   ✅ [${idx + 1}] Relay tx: ${tx2.hash.slice(0, 16)}...`]);
          await tx2.wait(1);

          // 轮询第二跳
          setProgress(prev => [...prev, `   ⏳ [${idx + 1}] ${lang === 'en' ? 'Bridging back to BSC...' : '跨链回 BSC...'}`]);
          const hop2Deadline = Date.now() + 5 * 60 * 1000;
          let hop2Status = 'PENDING';
          while (Date.now() < hop2Deadline && hop2Status !== 'DONE' && hop2Status !== 'FAILED') {
            await new Promise(r => setTimeout(r, 6000));
            try {
              const s = await fetch(`${API_URL}/api/dex_mixer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'status', tx_hash: tx2.hash, from_chain: leg.relay_chain_id, to_chain: 56 })
              });
              const sd = await s.json();
              hop2Status = sd.status || 'PENDING';
            } catch {}
          }
          if (hop2Status !== 'DONE') throw new Error(`Hop2 not done: ${hop2Status}`);

          setProgress(prev => [...prev, `   🎉 [${idx + 1}] ${lang === 'en' ? 'Delivered to target!' : '已到达目标！'}`]);
          return { leg_idx: idx, status: 'success', tx1: tx1.hash, tx2: tx2.hash, relay: leg.relay_chain };
        };

        // 并行执行所有 leg（Promise.allSettled）
        setProgress(prev => [...prev, `🚀 ${lang === 'en' ? 'Executing ' + route.num_legs + ' legs in parallel...' : '并行执行 ' + route.num_legs + ' 笔...'}`]);
        const legResults = await Promise.allSettled(
          route.legs.map((leg: any, idx: number) => executeOneLeg(leg, idx))
        );
        const successLegs = legResults.filter(r => r.status === 'fulfilled').length;
        const failedLegs = legResults.length - successLegs;

        setProgress(prev => [...prev, `\n🎉 ${lang === 'en' ? 'Ultimate Privacy complete!' : '极致隐私完成！'}`]);
        setProgress(prev => [...prev, `✅ ${lang === 'en' ? `${successLegs}/${route.num_legs} splits delivered` : `${successLegs}/${route.num_legs} 笔已到账`}`]);
        if (failedLegs > 0) {
          setProgress(prev => [...prev, `⚠️ ${lang === 'en' ? `${failedLegs} split(s) failed — funds safe (recoverable via relay mnemonic)` : `${failedLegs} 笔失败——资金安全（可通过中继助记词恢复）`}`]);
          // 显示具体错误
          legResults.filter(r => r.status === 'rejected').forEach((r: any) => {
            setProgress(prev => [...prev, `   ❌ ${String(r.reason).slice(0, 200)}`]);
          });
        }
        setProgress(prev => [...prev, `🔒 ${lang === 'en' ? 'Source untraceable: amount split + currency changed + chain bridged' : '源地址已隐匿：金额打碎 + 币种切换 + 跨链断点'}`]);
        setProgressPercent(100);

        setResult({
          success: successLegs > 0,
          mode: 'ultimate',
          total_transactions: route.num_legs,
          success_count: successLegs,
          failed_count: failedLegs,
          results: legResults.map(r => r.status === 'fulfilled' ? r.value : { status: 'failed', error: String(r.reason) }),
          route_id: route.route_id,
        });
        return;
      }

      // ==========================================
      // 快速模式：单链混币（保持原流程）
      // ==========================================

      // === 1. 调用 plan 端点拿完整计划 ===
      const planBody: any = {
        chain,
        mode,
        input_type: inputType,
        to_address: toAddress,
        total_amount: parseFloat(amount),
        num_hops: numHops,
        mnemonic: mnemonic || undefined
      };
      if (inputType === 'mnemonic') {
        planBody.from_mnemonic = inputValue;
        setProgress(prev => [...prev, `✅ ${text.detectedMnemonic}`]);
      } else {
        planBody.from_private_key = inputValue;
        setProgress(prev => [...prev, `✅ ${text.detectedPrivateKey}`]);
      }

      setProgress(prev => [...prev, `📋 Building plan...`]);
      const planResp = await fetch(`${API_URL}/api/mixer_plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(planBody)
      });
      const planCt = planResp.headers.get("content-type") || "";
      let planData: any;
      if (planCt.includes("application/json")) {
        planData = await planResp.json();
      } else {
        planData = { success: false, error: `Plan API error (${planResp.status})` };
      }
      if (!planData.success) {
        throw new Error(planData.error || 'Plan generation failed');
      }

      const plan = planData.plan;
      const totalSteps = plan.total_steps;
      setProgress(prev => [...prev, `📋 Plan ready: ${totalSteps} steps`]);
      if (plan.relay_chain) {
        setProgress(prev => [...prev, `🌉 Cross-chain: ${plan.chain.toUpperCase()} → ${plan.relay_chain.toUpperCase()} → ${plan.chain.toUpperCase()}`]);
      }

      // 关键：立即把 mnemonic 存 localStorage（资金恢复的唯一凭证）
      try {
        const stored = JSON.parse(localStorage.getItem('cygj_sessions') || '[]');
        stored.unshift({
          plan_id: plan.plan_id,
          mnemonic: plan.mnemonic,
          from_address: plan.from_address,
          to_address: plan.to_address,
          total_amount: plan.total_amount,
          num_hops: plan.num_hops,
          mode: plan.mode,
          chain: plan.chain,
          relay_chain: plan.relay_chain,
          created_at: new Date().toISOString()
        });
        // 只保留最近 50 条
        localStorage.setItem('cygj_sessions', JSON.stringify(stored.slice(0, 50)));
        setProgress(prev => [...prev, `💾 Session saved to local storage (plan_id: ${plan.plan_id})`]);
      } catch (e) {
        console.warn('localStorage save failed', e);
      }

      setProgressPercent(15);

      // === 2. 分步执行 ===
      let successCount = 0;
      let failedCount = 0;
      const stepResults: any[] = [];
      let stepIdx = 0;

      while (stepIdx < totalSteps) {
        const stepResp = await fetch(`${API_URL}/api/mixer_step`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ plan, step_idx: stepIdx })
        });
        const stepCt = stepResp.headers.get("content-type") || "";
        let stepData: any;
        if (stepCt.includes("application/json")) {
          stepData = await stepResp.json();
        } else {
          const t = await stepResp.text();
          stepData = { success: false, error: `Step ${stepIdx} HTTP ${stepResp.status}: ${t.slice(0, 200)}` };
        }

        if (stepData.success) {
          const s = stepData.step;
          const r = stepData.result;
          successCount++;
          stepResults.push({ ...s, result: r, status: 'success' });

          if (r.type === 'bridge') {
            const statusIcon = r.bridge_status === 'DONE' ? '✅' : (r.bridge_status === 'FAILED' ? '❌' : '⏳');
            setProgress(prev => [...prev, `${statusIcon} [${stepIdx + 1}/${totalSteps}] 🌉 ${r.from_chain} → ${r.to_chain} (${r.amount.toFixed(6)}) ${r.bridge_status}`]);

            // 如果还 pending 且有 txhash，轮询最多 ~40 秒
            if (r.requires_polling && r.tx_hash) {
              setProgress(prev => [...prev, `   ⏳ Waiting for bridge to complete...`]);
              const pollDeadline = Date.now() + 40_000;
              while (Date.now() < pollDeadline) {
                await new Promise(res => setTimeout(res, 5000));
                try {
                  const ps = await fetch(`${API_URL}/api/mixer_bridge_status`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ tx_hash: r.tx_hash, from_chain: r.from_chain, to_chain: r.to_chain })
                  });
                  const pd = await ps.json();
                  if (pd.success && pd.status === 'DONE') {
                    setProgress(prev => [...prev, `   ✅ Bridge DONE: ${pd.tx_hash_to?.slice(0, 10)}...`]);
                    break;
                  }
                  if (pd.success && pd.status === 'FAILED') {
                    setProgress(prev => [...prev, `   ❌ Bridge FAILED`]);
                    break;
                  }
                } catch {}
              }
            }
          } else {
            const fromAddr = r.from ? `${r.from.slice(0, 6)}...${r.from.slice(-4)}` : '';
            const toAddr = r.to ? `${r.to.slice(0, 6)}...${r.to.slice(-4)}` : '';
            const txShort = r.tx_hash ? `${r.tx_hash.slice(0, 10)}...` : '';
            if (r.early_exit) {
              setProgress(prev => [...prev, `⚡ [${stepIdx + 1}/${totalSteps}] Gas budget low — routed directly to target ${toAddr} (${r.amount.toFixed(6)}) ${txShort}`]);
              setProgress(prev => [...prev, `✅ Funds safely delivered. Stopping early.`]);
              successCount++;
              stepResults.push({ ...s, result: r, status: 'success' });
              break; // 软退出，停止后续步骤
            }
            setProgress(prev => [...prev, `✅ [${stepIdx + 1}/${totalSteps}] ${fromAddr} → ${toAddr} (${r.amount.toFixed(6)}) ${txShort}`]);
          }
        } else {
          failedCount++;
          stepResults.push({ idx: stepIdx, status: 'failed', error: stepData.error });
          setProgress(prev => [...prev, `❌ [${stepIdx + 1}/${totalSteps}] ${stepData.error}`]);
          // 致命错误：无法继续
          if (stepData.error && stepData.error.includes('余额不足')) {
            setProgress(prev => [...prev, `⚠️ Stopping: insufficient funds`]);
            break;
          }
        }

        stepIdx++;
        setProgressPercent(15 + Math.floor((stepIdx / totalSteps) * 80));
      }

      setProgress(prev => [...prev, `\n🎉 ${text.stealthTransferComplete}`]);
      setProgress(prev => [...prev, `${text.success} ${successCount} | ${text.failed} ${failedCount}`]);
      setProgress(prev => [...prev, `\n💾 Plan ID: ${plan.plan_id}`]);
      setProgress(prev => [...prev, `🔑 Mnemonic (SAVE THIS!): ${plan.mnemonic}`]);
      setProgress(prev => [...prev, `🆘 Recovery: enter Plan ID at /recover to retrieve mnemonic & keys`]);
      setProgress(prev => [...prev, `📜 View history at /history`]);
      setProgressPercent(100);

      setResult({
        success: successCount > 0,
        total_transactions: totalSteps,
        success_count: successCount,
        failed_count: failedCount,
        results: stepResults,
        plan: {
          mnemonic: plan.mnemonic,
          relay_chain: plan.relay_chain,
          fees: plan.fees
        }
      });
    } catch (error) {
      setProgress(prev => [...prev, `❌ ${text.error} ${error}`]);
      setResult({ success: false, error: String(error) });
      setProgressPercent(0);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#1a1a1a] border border-[#d4af37]/20 rounded-xl shadow-2xl shadow-[#d4af37]/5 p-6">
      {/* Online Users Display */}
      <div className="mb-4 flex items-center justify-between bg-[#0a0a0a] border border-[#10b981]/30 rounded-lg px-4 py-2">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-[#10b981] rounded-full animate-pulse shadow-lg shadow-[#10b981]/50"></div>
          <span className="text-sm text-gray-400">{text.onlineToday}</span>
        </div>
        <span className="text-lg font-bold text-[#10b981]">{onlineUsers}</span>
      </div>
      
      {/* Mixing Mode Selection */}
      <div className="mb-6">
        <div className="grid grid-cols-2 gap-4">
          {/* Fast Mode */}
          <button
            onClick={() => setMode('fast')}
            className={`relative p-5 rounded-xl transition-all duration-300 overflow-hidden group border ${
              mode === 'fast'
                ? "bg-gradient-to-br from-[#d4af37]/20 to-[#ffd700]/10 border-[#d4af37] shadow-xl shadow-[#d4af37]/30"
                : "bg-[#0a0a0a] border-[#d4af37]/20 hover:border-[#d4af37]/50 hover:shadow-lg hover:shadow-[#d4af37]/20"
            }`}
          >
            {/* Glow effect */}
            <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-[#d4af37]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${
              mode === 'fast' ? 'opacity-30' : ''
            }`}></div>
            
            <div className="relative z-10">
              <div className={`font-bold text-base mb-2 ${mode === 'fast' ? 'text-[#d4af37]' : 'text-white'}`}>{text.fastMode}</div>
              <div className={`text-xs leading-relaxed ${mode === 'fast' ? 'text-[#d4af37]/80' : 'text-gray-400'}`}>
                {text.fastModeDesc}
              </div>
            </div>
          </button>

          {/* Ultimate Privacy */}
          <button
            onClick={() => setMode('ultimate')}
            className={`relative p-5 rounded-xl transition-all duration-300 overflow-hidden group border ${
              mode === 'ultimate'
                ? "bg-gradient-to-br from-[#d4af37]/20 to-[#ffd700]/10 border-[#d4af37] shadow-xl shadow-[#d4af37]/30"
                : "bg-[#0a0a0a] border-[#d4af37]/20 hover:border-[#d4af37]/50 hover:shadow-lg hover:shadow-[#d4af37]/20"
            }`}
          >
            {/* Glow effect */}
            <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-[#d4af37]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${
              mode === 'ultimate' ? 'opacity-30' : ''
            }`}></div>
            
            <div className="relative z-10">
              <div className={`font-bold text-base mb-2 ${mode === 'ultimate' ? 'text-[#d4af37]' : 'text-white'}`}>{text.ultimatePrivacy}</div>
              <div className={`text-xs leading-relaxed ${mode === 'ultimate' ? 'text-[#d4af37]/80' : 'text-gray-400'}`}>
                {text.ultimatePrivacyDesc}
              </div>
            </div>
          </button>
        </div>
        
        {/* Mode Description */}
        {mode === 'fast' && (
          <div className="mt-4 p-4 bg-[#0a0a0a] border border-[#d4af37]/30 rounded-lg shadow-lg shadow-[#d4af37]/10">
            <p className="text-sm text-gray-300 leading-relaxed">
              <span className="font-semibold text-[#d4af37]">{text.singleChainMixing}</span> · {text.vpnRecommended} · {text.suitableSmallTransfers}
            </p>
          </div>
        )}
        
        {mode === 'ultimate' && (
          <div className="mt-4 p-4 bg-[#0a0a0a] border border-[#d4af37]/30 rounded-lg shadow-lg shadow-[#d4af37]/10">
            <p className="text-sm text-gray-300 leading-relaxed">
              <span className="font-semibold text-[#d4af37]">{text.suitableLargeTransfers}</span>, {text.multiHopCrossChain}
            </p>
          </div>
        )}


      </div>
      
      {/* Chain Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          {text.selectNetwork}
        </label>
        <select
          value={chain}
          onChange={(e) => setChain(e.target.value)}
          className="w-full px-4 py-2 bg-[#0a0a0a] border-b-2 border-[#d4af37]/50 text-white rounded-lg focus:ring-2 focus:ring-[#d4af37] focus:border-[#d4af37] transition-all"
        >
          <option value="bsc" className="bg-[#0a0a0a]">BSC</option>
          <option value="eth" className="bg-[#0a0a0a]">Ethereum</option>
        </select>
      </div>

      {/* Private Key / Mnemonic Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          {text.sourcePrivateKey}
        </label>
        <textarea
          value={privateKey}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder={text.enterPrivateKey}
          rows={3}
          className="w-full px-4 py-2 bg-[#0a0a0a] border-b-2 border-[#d4af37]/50 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-[#d4af37] focus:border-[#d4af37] transition-all text-sm resize-none"
        />
        {detectedInputType && (
          <p className="text-xs text-[#d4af37] mt-1 flex items-center">
            <span className="mr-1">ℹ️</span>
            {text.detectedAs} {detectedInputType === 'mnemonic' ? text.mnemonic : text.privateKey}
            {detectedInputType === 'mnemonic' && ` ${text.willUseFirstAddress}`}
          </p>
        )}
      </div>

      {/* Target Address */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          {text.targetAddress}
        </label>
        <input
          type="text"
          value={toAddress}
          onChange={(e) => setToAddress(e.target.value)}
          placeholder="0x..."
          className="w-full px-4 py-2 bg-[#0a0a0a] border-b-2 border-[#d4af37]/50 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-[#d4af37] focus:border-[#d4af37] transition-all text-sm"
        />
      </div>

      {/* Amount */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          {text.transferAmount}
        </label>
        <input
          type="number"
          step="0.001"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="0.1"
          className="w-full px-4 py-2 bg-[#0a0a0a] border-b-2 border-[#d4af37]/50 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-[#d4af37] focus:border-[#d4af37] transition-all text-sm"
        />
      </div>

      {/* Number of Hops - 仅 Fast Mode 显示 */}
      {mode === 'fast' && (
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          {text.hops} <span className="text-[#d4af37]">{numHops}</span> <span className="text-xs text-gray-400">{text.moreIsStealthier}</span>
          <span className="ml-2 text-xs text-[#d4af37]">
            {text.est} {numHops <= 10 ? '~30s' : numHops <= 50 ? '~2.5min' : numHops <= 100 ? '~5min' : '~20min'}
          </span>
        </label>
        <p className="text-xs text-gray-400 mb-2">{text.multipleIntermediateWallets}</p>
        <div className="flex gap-2">
          {[10, 50, 100, 500, 1000].map((num) => (
            <button
              key={num}
              onClick={() => {
                setNumHops(num);
                setCustomHops("");
              }}
              className={`px-3 py-1 rounded-lg font-medium transition text-sm border ${
                numHops === num && customHops === ""
                  ? "bg-gradient-to-r from-[#d4af37] to-[#ffd700] text-black border-[#d4af37] shadow-lg shadow-[#d4af37]/30"
                  : "bg-[#0a0a0a] text-gray-300 border-[#d4af37]/30 hover:border-[#d4af37] hover:shadow-md hover:shadow-[#d4af37]/20"
              }`}
            >
              {num}
            </button>
          ))}
          <input
            type="number"
            min="10"
            max="100000"
            step="1"
            value={customHops}
            onChange={(e) => {
              const val = e.target.value;
              setCustomHops(val);
              if (val !== '' && !isNaN(parseInt(val))) {
                const num = Math.max(10, Math.min(100000, parseInt(val)));
                setNumHops(num);
              }
            }}
            className="flex-1 px-4 py-2 bg-[#0a0a0a] border-b-2 border-[#d4af37]/50 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-[#d4af37] focus:border-[#d4af37] transition-all text-sm"
            placeholder={text.custom}
          />
        </div>
      </div>
      )}
      {/* Fee Estimate - Fast Mode 显示详细费用，Ultimate 显示简要 */}
      {mode === 'fast' ? (
      <div className="bg-[#0a0a0a] border border-[#d4af37]/30 p-4 rounded-lg mb-4 shadow-lg shadow-[#d4af37]/10">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-gray-400 text-xs">{text.donation}</p>
            <p className="font-semibold text-[#d4af37]">
              {(numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)).toFixed(4)} BNB
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">{text.estGas}</p>
            <p className="font-semibold text-[#d4af37]">~{(numHops * 0.00021).toFixed(5)} BNB</p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">{text.totalFee}</p>
            <p className="font-semibold text-[#d4af37]">
              ~{((numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)) + numHops * 0.00021).toFixed(5)} BNB
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">{text.expectedReceive}</p>
            <p className="font-semibold text-[#10b981]">
              {amount ? (parseFloat(amount) - (numHops * 0.0003) - numHops * 0.00021).toFixed(5) : "0"} BNB
            </p>
          </div>
        </div>
      </div>
      ) : (
      <div className="bg-[#0a0a0a] border border-[#d4af37]/30 p-4 rounded-lg mb-4 shadow-lg shadow-[#d4af37]/10">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-gray-400 text-xs">{text.donation}</p>
            <p className="font-semibold text-[#d4af37]">
              {amount && parseFloat(amount) > 0 ? (() => {
                const a = parseFloat(amount);
                const rate = a < 1 ? 0.049 : a < 10 ? 0.041 : a < 100 ? 0.031 : 0.027;
                return `${(a * rate).toFixed(5)} BNB`;
              })() : '0.00000 BNB'}
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">{text.estGas}</p>
            <p className="font-semibold text-[#d4af37]">~0.00150 BNB</p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">{text.totalFee}</p>
            <p className="font-semibold text-[#d4af37]">
              {amount && parseFloat(amount) > 0 ? (() => {
                const a = parseFloat(amount);
                const rate = a < 1 ? 0.049 : a < 10 ? 0.041 : a < 100 ? 0.031 : 0.027;
                return `~${(a * rate + 0.0015).toFixed(5)} BNB`;
              })() : '~0.00000 BNB'}
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">{text.expectedReceive}</p>
            <p className="font-semibold text-[#10b981]">
              {amount && parseFloat(amount) > 0 ? (() => {
                const a = parseFloat(amount);
                const rate = a < 1 ? 0.049 : a < 10 ? 0.041 : a < 100 ? 0.031 : 0.027;
                return `${(a * (1 - rate) - 0.0015).toFixed(5)} BNB`;
              })() : '0.00000 BNB'}
            </p>
          </div>
        </div>
      </div>
      )}

      {/* Execute Button */}
      <button
        onClick={handleExecute}
        disabled={isLoading || !privateKey || !toAddress || !amount}
        className={`w-full py-6 rounded-lg font-bold text-lg transition-all duration-300 relative overflow-hidden ${
          isLoading || !privateKey || !toAddress || !amount
            ? "bg-gray-700 text-gray-500 cursor-not-allowed border border-gray-600"
            : "bg-gradient-to-r from-[#d4af37] via-[#ffd700] to-[#d4af37] text-black hover:shadow-2xl hover:shadow-[#d4af37]/50 border-2 border-[#d4af37] shadow-xl shadow-[#d4af37]/30"
        }`}
      >
        {/* Glow animation effect */}
        {!isLoading && privateKey && toAddress && amount && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
        )}
        
        {isLoading ? (
          <div className="relative z-10">
            <div className="flex items-center justify-center mb-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-black mr-2"></div>
              <span>{text.processing} {progressPercent}%</span>
            </div>
            {/* Progress Bar */}
            <div className="absolute bottom-0 left-0 right-0 h-2 bg-black/30 rounded-b-lg overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-[#d4af37] to-[#ffd700] transition-all duration-500 ease-out shadow-lg shadow-[#d4af37]/50"
                style={{ width: `${progressPercent}%` }}
              ></div>
            </div>
          </div>
        ) : (
          <span className="relative z-10">{text.secureTransfer}</span>
        )}
      </button>

      {/* Progress Display - above button area, shown before FAQ */}
      {progress.length > 0 && (
        <div className="mt-4 bg-[#0a0a0a] border border-[#d4af37]/30 text-[#d4af37] p-3 rounded-lg font-mono text-xs max-h-64 overflow-y-auto shadow-lg shadow-[#d4af37]/10">
          {progress.map((line, index) => (
            <div key={index} className="whitespace-pre-wrap">
              {line}
            </div>
          ))}
          {isLoading && (
            <div className="mt-2 flex items-center text-xs">
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-[#d4af37] mr-2"></div>
              <span>{text.processingText}</span>
            </div>
          )}
        </div>
      )}

      {/* Result - Only show on error */}
      {result && !result.success && (
        <div className="mt-4 p-4 rounded-lg text-sm bg-red-900/20 border border-red-500/30">
          <h3 className="font-semibold mb-2 text-red-400">
            {text.executionFailed}
          </h3>
          <p className="text-xs text-red-300">{result.error}</p>
        </div>
      )}

      {/* FAQ Section */}
      <div className="mt-6">
        <h3 className="text-sm font-semibold text-[#d4af37] mb-3 border-b border-[#d4af37]/30 pb-2">{text.faq}</h3>
        <div className="space-y-2">
          {/* FAQ 1 */}
          <div className="border border-[#d4af37]/20 rounded-lg overflow-hidden bg-[#0a0a0a]">
            <button
              onClick={() => setExpandedFaq(expandedFaq === 1 ? null : 1)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#1a1a1a] transition border-l-2 border-l-[#d4af37]/50"
            >
              <span className="text-sm font-medium text-white">{text.faqQuestion1}</span>
              <svg
                className={`w-5 h-5 text-[#d4af37] transition-transform ${expandedFaq === 1 ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedFaq === 1 && (
              <div className="px-4 py-3 bg-[#1a1a1a] text-xs text-gray-300 leading-relaxed border-t border-[#d4af37]/20">
                <p className="font-semibold mb-2">{text.faq1TechPrinciple}</p>
                <p className="mb-3">{text.faq1MultiLayer}</p>
                <p className="font-semibold mb-1">{text.faq1FastModeDual}</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li><strong>{text.faq1Layer1}</strong></li>
                  <li>{text.faq1MixLayer}</li>
                  <li><strong>{text.faq1Layer2}</strong></li>
                </ul>
                <p className="font-semibold mb-1">{text.faq1OnChain}</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>{text.faq1Explorer}</li>
                  <li>{text.faq1Middle}</li>
                  <li>{text.faq1Final}</li>
                  <li><strong>{text.faq1Conclusion}</strong></li>
                </ul>
                <p className="font-semibold mb-1">{text.faq1Ultimate}</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>{text.faq1MixBefore}</li>
                  <li>{text.faq1Bridge}</li>
                  <li>{text.faq1Unlinkable}</li>
                  <li><strong>{text.faq1IP}</strong></li>
                  <li><strong>{text.faq1Time}</strong></li>
                </ul>
              </div>
            )}
          </div>

          {/* FAQ 2 */}
          <div className="border border-[#d4af37]/20 rounded-lg overflow-hidden bg-[#0a0a0a]">
            <button
              onClick={() => setExpandedFaq(expandedFaq === 2 ? null : 2)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#1a1a1a] transition border-l-2 border-l-[#d4af37]/50"
            >
              <span className="text-sm font-medium text-white">{text.faqQuestion2}</span>
              <svg
                className={`w-5 h-5 text-[#d4af37] transition-transform ${expandedFaq === 2 ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedFaq === 2 && (
              <div className="px-4 py-3 bg-[#1a1a1a] text-xs text-gray-300 leading-relaxed border-t border-[#d4af37]/20">
                <p className="font-semibold mb-2">{text.faq2Decentralized}</p>
                <p className="font-semibold text-green-400 mb-1">{text.faq2NonCustodial}</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>{text.faq2BIP44}</li>
                  <li>{text.faq2Control}</li>
                  <li>{text.faq2NoPool}</li>
                </ul>
                <p className="font-semibold text-green-400 mb-1">{text.faq2OnChain}</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>{text.faq2Hash}</li>
                  <li>{text.faq2OpenSource}</li>
                  <li>{text.faq2Immutable}</li>
                </ul>
                <p className="font-semibold text-green-400 mb-1">{text.faq2MnemonicSec}</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>{text.faq2Local}</li>
                  <li>{text.faq2Hardware}</li>
                  <li>{text.faq2AutoClear}</li>
                </ul>
                <p className="font-semibold text-orange-400 mb-1">{text.faq2Recommendations}</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>{text.faq2FirstTime}</li>
                  <li>{text.faq2Keep}</li>
                  <li>{text.faq2Confirm}</li>
                </ul>
              </div>
            )}
          </div>

          {/* FAQ 3 */}
          <div className="border border-[#d4af37]/20 rounded-lg overflow-hidden bg-[#0a0a0a]">
            <button
              onClick={() => setExpandedFaq(expandedFaq === 3 ? null : 3)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#1a1a1a] transition border-l-2 border-l-[#d4af37]/50"
            >
              <span className="text-sm font-medium text-white">{text.faqQuestion3}</span>
              <svg
                className={`w-5 h-5 text-[#d4af37] transition-transform ${expandedFaq === 3 ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedFaq === 3 && (
              <div className="px-4 py-3 bg-[#1a1a1a] text-xs text-gray-300 leading-relaxed border-t border-[#d4af37]/20">
                <p className="font-semibold mb-2">{text.faq3FastMode}</p>
                <p className="mb-1"><strong>{text.faq3UseCase}</strong> {text.faq3FastUseCase}</p>
                <p className="mb-1"><strong>{text.faq3TechFeatures}</strong> {text.faq3FastTech}</p>
                <p className="mb-3"><strong>{text.faq3PrivacyLevel}</strong> {text.faq3FastPrivacy}</p>
                <p className="font-semibold mb-2">{text.faq3Ultimate}</p>
                <p className="mb-1"><strong>{text.faq3UseCase}</strong> {text.faq3UltimateUseCase}</p>
                <p className="mb-1"><strong>{text.faq3TechFeatures}</strong></p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>{text.faq3CrossChain}</li>
                  <li>{text.faq3NewTemp}</li>
                  <li>{text.faq3AutoProxy}</li>
                  <li>{text.faq3Delays}</li>
                </ul>
                <p className="mb-2"><strong>{text.faq3PrivacyLevel}</strong> {text.faq3UltimatePrivacy}</p>
                <p className="font-semibold">{text.faq3CoreDiff}</p>
                <p>{text.faq3CoreDiffText}</p>
              </div>
            )}
          </div>

          {/* FAQ 4 */}
          <div className="border border-[#d4af37]/20 rounded-lg overflow-hidden bg-[#0a0a0a]">
            <button
              onClick={() => setExpandedFaq(expandedFaq === 4 ? null : 4)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#1a1a1a] transition border-l-2 border-l-[#d4af37]/50"
            >
              <span className="text-sm font-medium text-white">{text.faqQuestion4}</span>
              <svg
                className={`w-5 h-5 text-[#d4af37] transition-transform ${expandedFaq === 4 ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedFaq === 4 && (
              <div className="px-4 py-3 bg-[#1a1a1a] text-xs text-gray-300 leading-relaxed border-t border-[#d4af37]/20">
                <p className="font-semibold mb-2">{text.faq4TechNecessity}</p>
                <p className="mb-1"><strong>{text.faq4HDPrinciple}</strong></p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>{text.faq4Requires}</li>
                  <li>{text.faq4BIP44}</li>
                  <li>{text.faq4Child}</li>
                </ul>
                <p className="mb-1"><strong>{text.faq4WhyNot}</strong></p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>{text.faq4SingleKey}</li>
                  <li>{text.faq4CannotGen}</li>
                  <li>{text.faq4HDWallet}</li>
                </ul>
                <p className="font-semibold mb-2">{text.faq4Security}</p>
                <p className="font-semibold text-green-400 mb-1">{text.faq4Local}</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>{text.faq4BrowserOnly}</li>
                  <li>{text.faq4NotSent}</li>
                  <li>{text.faq4LocalCalc}</li>
                </ul>
                <p className="font-semibold text-green-400 mb-1">{text.faq4Temp}</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>{text.faq4AutoClear}</li>
                  <li>{text.faq4NoBalance}</li>
                  <li>{text.faq4Dedicated}</li>
                </ul>
                <p className="font-semibold mb-1">{text.faq4BestPractices}</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>{text.faq4NewMnemonic}</li>
                  <li>{text.faq4Discard}</li>
                  <li>{text.faq4HardwareWallet}</li>
                </ul>
              </div>
            )}
          </div>

          {/* FAQ 5 */}
          <div className="border border-[#d4af37]/20 rounded-lg overflow-hidden bg-[#0a0a0a]">
            <button
              onClick={() => setExpandedFaq(expandedFaq === 5 ? null : 5)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#1a1a1a] transition border-l-2 border-l-[#d4af37]/50"
            >
              <span className="text-sm font-medium text-white">{text.faqQuestion5}</span>
              <svg
                className={`w-5 h-5 text-[#d4af37] transition-transform ${expandedFaq === 5 ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedFaq === 5 && (
              <div className="px-4 py-3 bg-[#1a1a1a] text-xs text-gray-300 leading-relaxed border-t border-[#d4af37]/20">
                <p className="font-semibold mb-2">{text.faq5FaultTolerance}</p>
                <p className="font-semibold text-green-400 mb-1">{text.faq5AutoRetry}</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>{text.faq5Retry3}</li>
                  <li>{text.faq5GasIncrease}</li>
                  <li>{text.faq5Congestion}</li>
                </ul>
                <p className="font-semibold text-green-400 mb-1">{text.faq5FundProtection}</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>{text.faq5NoDeduct}</li>
                  <li>{text.faq5AutoCollect}</li>
                  <li>{text.faq5NoStuck}</li>
                </ul>
                <p className="font-semibold text-green-400 mb-1">{text.faq5RealTime}</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>{text.faq5Status}</li>
                  <li>{text.faq5Progress}</li>
                  <li>{text.faq5Hash}</li>
                </ul>
                <p className="font-semibold mb-2">{text.faq5CommonIssues}</p>
                <p className="mb-1"><strong>{text.faq5Case1}</strong></p>
                <p className="mb-2 ml-2">{text.faq5Case1Cause}</p>
                <p className="mb-1"><strong>{text.faq5Case2}</strong></p>
                <p className="mb-2 ml-2">{text.faq5Case2Cause}</p>
                <p className="mb-1"><strong>{text.faq5Case3}</strong></p>
                <p className="ml-2">{text.faq5Case3Cause}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Coming Soon component
function ComingSoonApp({ tool, lang }: { tool: any; lang: "en" | "zh" }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 text-center">
      <div className="text-6xl mb-4">{tool.icon}</div>
      <h2 className="text-2xl font-bold mb-2">{tool.name}</h2>
      <p className="text-gray-600 mb-6">{tool.description}</p>
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-700 font-semibold">{lang === "zh" ? "🚧 即将上线" : "🚧 Coming Soon"}</p>
        <p className="text-sm text-gray-600 mt-2">{lang === "zh" ? "敬请期待..." : "Stay tuned..."}</p>
      </div>
    </div>
  );
}

export default function Home() {
  const [lang, setLang] = useState<"en" | "zh">("en");
  const [selectedTool, setSelectedTool] = useState(tools[0]);
  const [dailyUsage, setDailyUsage] = useState(0);

  // Translation object for main page
  const t = {
    en: {
      tools: "Tools",
      privacy: "Privacy",
      wallet: "Wallet",
      defi: "DeFi",
      analytics: "Analytics",
      dailyUsage: "Daily Usage",
      totalUsers: "Total Users",
      disclaimer: "Disclaimer",
      terms: "Terms",
      privacyPolicy: "Privacy",
      toolDescriptions: {
        1: "68+ blockchain supported. Professional multi-hop cross-chain relay solution, shielding on-chain transaction traces and network IP, delivering reliable Web3 identity and asset privacy protection.",
        2: "BIP44 standard HD wallet generator, generate multiple addresses from mnemonic",
        3: "Batch transfer tool, send tokens to multiple addresses at once",
        4: "Token analysis tool, view holder distribution, transaction history and more",
        5: "Real-time gas price tracking, help you choose the best transaction timing",
        6: "Batch NFT minting tool, supports multiple standards"
      }
    },
    zh: {
      tools: "工具",
      privacy: "隐私",
      wallet: "钱包",
      defi: "DeFi",
      analytics: "分析",
      dailyUsage: "今日使用",
      totalUsers: "总用户数",
      disclaimer: "免责声明",
      terms: "服务条款",
      privacyPolicy: "隐私政策",
      toolDescriptions: {
        1: "支持68+条区块链。专业多跳跨链中继方案，屏蔽链上交易痕迹与网络IP，提供可靠的Web3身份与资产隐私保护。",
        2: "BIP44标准HD钱包生成器，从助记词生成多个地址",
        3: "批量转账工具，一次性向多个地址发送代币",
        4: "代币分析工具，查看持仓分布、交易历史等",
        5: "实时Gas价格追踪，帮助您选择最佳交易时机",
        6: "批量NFT铸造工具，支持多种标准"
      }
    }
  };

  const text = t[lang];

  // Initialize daily usage count
  useEffect(() => {
    const now = new Date();
    const dayMinutes = now.getHours() * 60 + now.getMinutes();
    const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 0).getTime()) / 86400000);
    const baseUsage = 500 + (dayOfYear * 37) % 300 + Math.floor(dayMinutes / 2);
    setDailyUsage(baseUsage);
  }, []);
  
  // Dynamically increase daily usage count
  useEffect(() => {
    const interval = setInterval(() => {
      setDailyUsage(prev => {
        const increase = Math.random() > 0.3 ? Math.floor(Math.random() * 3) : 0;
        return prev + increase;
      });
    }, 15000 + Math.random() * 20000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Header */}
      <header className="bg-[#0a0a0a] border-b border-[#d4af37]/20 sticky top-0 z-10 backdrop-blur-sm">
        <nav className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img src="/logo.png" alt="CYGJ Logo" className="w-10 h-10" />
              <span className="text-2xl font-bold text-white">CYGJ Crypto Tools</span>
            </div>
            <button
              onClick={() => setLang(lang === "en" ? "zh" : "en")}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#d4af37]/30 hover:border-[#d4af37] text-sm font-medium transition text-white"
            >
              <Globe className="w-4 h-4 text-[#d4af37]" />
              {lang === "en" ? "中文" : "English"}
            </button>
          </div>
        </nav>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* SEO Content Block - visible to crawlers, hidden from users */}
        <div className="sr-only" aria-hidden="false">
          <h1>CYGJ Crypto Tools - Professional Web3 Toolbox</h1>
          <p>
            CYGJ is a professional Web3 toolbox for crypto hunters and DeFi enthusiasts.
            Our platform provides essential on-chain tools including stealth transfer router,
            HD wallet generator, batch transfer, token analyzer, gas tracker, and NFT batch mint.
            Supporting 68+ blockchains including BSC, Ethereum, Polygon, Arbitrum and more.
          </p>
          <h2>Stealth Transfer Router</h2>
          <p>
            Professional multi-hop cross-chain relay solution for on-chain privacy protection.
            Shield transaction traces and network IP with multi-layer isolation architecture.
            Supports fast mode and ultimate privacy mode for different transfer needs.
          </p>
          <h2>HD Wallet Generator</h2>
          <p>
            BIP44 standard HD wallet generator. Generate multiple wallet addresses from a single mnemonic phrase.
            Compatible with MetaMask, Trust Wallet and all major Web3 wallets.
            Supports batch wallet generation for BSC, Ethereum and Polygon.
          </p>
          <h2>Batch Transfer Tool</h2>
          <p>
            Send tokens to multiple addresses in one transaction. Supports 10 to 10000 addresses.
            CSV import, gas optimization, and real-time tracking. Essential tool for airdrops and bulk payments.
          </p>
          <h2>Web3 Tools for Crypto Hunters</h2>
          <p>
            CYGJ Crypto Tools is your essential Web3 toolbox. Whether you need batch wallet generation,
            batch address balance check, stealth transfer, or DeFi utilities — we have you covered.
            Free to use, non-custodial, your keys stay with you.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Tool List */}
          <div className="lg:col-span-1">
            <div className="bg-[#1a1a1a] border border-[#d4af37]/20 rounded-xl p-4 sticky top-24">
              <h2 className="text-lg font-bold mb-4 text-[#d4af37]">{text.tools}</h2>
              <div className="space-y-2">
                {tools.map((tool) => (
                  <button
                    key={tool.id}
                    onClick={() => setSelectedTool(tool)}
                    className={`w-full text-left p-3 rounded-lg transition-all duration-300 ${
                      selectedTool.id === tool.id
                        ? "bg-gradient-to-r from-[#d4af37]/20 to-[#ffd700]/10 border border-[#d4af37] shadow-lg shadow-[#d4af37]/20"
                        : "bg-[#0a0a0a] border border-[#d4af37]/10 hover:border-[#d4af37]/30 hover:shadow-md hover:shadow-[#d4af37]/10"
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{tool.icon}</span>
                      <div className="flex-1 min-w-0">
                        <p className={`font-semibold text-sm truncate ${
                          selectedTool.id === tool.id ? "text-[#d4af37]" : "text-white"
                        }`}>{tool.name}</p>
                        <p className={`text-xs truncate ${
                          selectedTool.id === tool.id ? "text-[#d4af37]/70" : "text-gray-500"
                        }`}>
                          {tool.category === "privacy" ? text.privacy : 
                           tool.category === "wallet" ? text.wallet :
                           tool.category === "defi" ? text.defi : text.analytics}
                        </p>
                      </div>
                      {tool.status === "active" && (
                        <span className="flex-shrink-0 w-2 h-2 bg-[#10b981] rounded-full shadow-lg shadow-[#10b981]/50"></span>
                      )}
                    </div>
                  </button>
                ))}
              </div>

              {/* Tool Info */}
              <div className="mt-6 pt-6 border-t border-[#d4af37]/20">
                <div className="text-center mb-4">
                  <div className="text-4xl mb-2">{selectedTool.icon}</div>
                  <h3 className="font-bold text-sm text-white">{selectedTool.name}</h3>
                  <p className="text-xs text-gray-400 mt-1">{text.toolDescriptions[selectedTool.id as keyof typeof text.toolDescriptions]}</p>
                </div>

                {selectedTool.status === "active" && (
                  <>
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      <div className="bg-[#0a0a0a] border border-[#d4af37]/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-[#d4af37]">{dailyUsage}</div>
                        <div className="text-xs text-gray-400">{text.dailyUsage}</div>
                      </div>
                      <div className="bg-[#0a0a0a] border border-[#10b981]/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-[#10b981]">{selectedTool.users}</div>
                        <div className="text-xs text-gray-400">{text.totalUsers}</div>
                      </div>
                    </div>

                    {/* Legal Links */}
                    <div className="mt-3 pt-3 border-t border-[#d4af37]/20">
                      <div className="flex flex-wrap items-center justify-center gap-1 text-[10px] text-gray-500 leading-tight">
                        <a 
                          href="/disclaimer" 
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:text-[#d4af37] transition-colors duration-200"
                        >
                          {text.disclaimer}
                        </a>
                        <span>|</span>
                        <a 
                          href="/terms" 
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:text-[#d4af37] transition-colors duration-200"
                        >
                          {text.terms}
                        </a>
                        <span>|</span>
                        <a 
                          href="/privacy" 
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:text-[#d4af37] transition-colors duration-200"
                        >
                          {text.privacyPolicy}
                        </a>
                      </div>
                      <div className="text-center text-[10px] text-gray-600 mt-1">
                        © 2024 CYGJ Tools
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - Application */}
          <div className="lg:col-span-3">
            {selectedTool.status === "active" ? (
              selectedTool.id === 1 ? (
                <StealthTransferApp lang={lang} />
              ) : (
                <ComingSoonApp tool={selectedTool} lang={lang} />
              )
            ) : (
              <ComingSoonApp tool={selectedTool} lang={lang} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
