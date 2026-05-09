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
    time: "3-5 minutes",
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
    time: "8-50 hours",
    description: "Multi-chain Ghost Mode · Fully Anonymous · Untraceable",
    color: "red",
    feeRate: 0,  // No per-hop fee
    crosschainFee: 0.006,  // 3 cross-chain, 0.002 each
    percentageFee: 4.9  // 4.9% of transfer amount
  }
};

// Stealth Transfer Mixer component
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
  const [detectedInputType, setDetectedInputType] = useState<"private_key" | "mnemonic" | null>(null);
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
      
      // 智能识别输入类型
      const inputType = detectInputType(privateKey);
      const inputValue = privateKey.trim();
      
      // 构建请求体
      const requestBody: any = {
        chain,
        mode,
        input_type: inputType,
        to_address: toAddress,
        total_amount: parseFloat(amount),
        num_hops: numHops,
        mnemonic: mnemonic || undefined,
        gas_level: "standard"
      };
      
      // 根据输入类型添加对应字段
      if (inputType === 'mnemonic') {
        requestBody.from_mnemonic = inputValue;
        setProgress(prev => [...prev, "✅ 已识别为：助记词"]);
      } else {
        requestBody.from_private_key = inputValue;
        setProgress(prev => [...prev, "✅ 已识别为：私钥"]);
      }
      
      const response = await fetch(`${API_URL}/api/mixer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody)
      });

      setProgressPercent(30);
      const data = await response.json();
      setProgressPercent(40);
      
      if (data.success && data.results) {
        setProgress(prev => [...prev, "\nTransaction Flow Details:"]);
        setProgressPercent(50);
        
        // Display address flow for each transaction
        const totalTxs = data.results.length;
        data.results.forEach((tx: any, index: number) => {
          const currentProgress = 50 + Math.floor((index / totalTxs) * 45);
          setProgressPercent(currentProgress);
          
          if (tx.status === 'success') {
            const fromAddr = tx.from ? `${tx.from.slice(0, 6)}...${tx.from.slice(-4)}` : 'Source';
            const toAddr = tx.to ? `${tx.to.slice(0, 6)}...${tx.to.slice(-4)}` : 'Target';
            const txHash = tx.tx_hash ? `${tx.tx_hash.slice(0, 8)}...` : '';
            
            setProgress(prev => [...prev, 
              `✅ [${index + 1}/${data.results.length}] ${fromAddr} → ${toAddr} (${tx.amount} BNB) ${txHash}`
            ]);
          } else if (tx.status === 'failed') {
            setProgress(prev => [...prev, 
              `❌ [${index + 1}/${data.results.length}] Transaction failed: ${tx.error || 'Unknown error'}`
            ]);
          }
        });
        
        setProgressPercent(95);
        setProgress(prev => [...prev, `\n🎉 Stealth transfer complete!`]);
        setProgress(prev => [...prev, `Target received: ${data.total_collected} BNB`]);
        setProgress(prev => [...prev, `Success: ${data.success_count} | Failed: ${data.failed_count}`]);
        setProgressPercent(100);
      }
      
      setResult(data);
    } catch (error) {
      setProgress(prev => [...prev, `❌ Error: ${error}`]);
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
          <span className="text-sm text-gray-400">Online Today</span>
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
              <div className={`font-bold text-base mb-2 ${mode === 'fast' ? 'text-[#d4af37]' : 'text-white'}`}>Fast Mode</div>
              <div className={`text-xs leading-relaxed ${mode === 'fast' ? 'text-[#d4af37]/80' : 'text-gray-400'}`}>
                Cross Obfuscation · Hide IP · Fast Arrival
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
              <div className={`font-bold text-base mb-2 ${mode === 'ultimate' ? 'text-[#d4af37]' : 'text-white'}`}>Ultimate Privacy</div>
              <div className={`text-xs leading-relaxed ${mode === 'ultimate' ? 'text-[#d4af37]/80' : 'text-gray-400'}`}>
                Multi-chain Ghost Mode · Fully Anonymous · Untraceable
              </div>
            </div>
          </button>
        </div>
        
        {/* Mode Description */}
        {mode === 'fast' && (
          <div className="mt-4 p-4 bg-[#0a0a0a] border border-[#d4af37]/30 rounded-lg shadow-lg shadow-[#d4af37]/10">
            <p className="text-sm text-gray-300 leading-relaxed">
              <span className="font-semibold text-[#d4af37]">Single-chain Mixing</span> · VPN recommended for IP protection · Suitable for small transfers (&lt;0.5 BNB)
            </p>
          </div>
        )}
        
        {mode === 'ultimate' && (
          <div className="mt-4 p-4 bg-[#0a0a0a] border border-[#d4af37]/30 rounded-lg shadow-lg shadow-[#d4af37]/10">
            <p className="text-sm text-gray-300 leading-relaxed">
              <span className="font-semibold text-[#d4af37]">Suitable for large transfers</span>, Multi-hop cross-chain + multi-chain paths + 100% hide fund paths, IP untraceable, absolute privacy protection
            </p>
          </div>
        )}
      </div>
      
      {/* Chain Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          Select Network
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
          Source Private Key / Mnemonic *
        </label>
        <textarea
          value={privateKey}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder="Enter private key or mnemonic (12/24 words)"
          rows={3}
          className="w-full px-4 py-2 bg-[#0a0a0a] border-b-2 border-[#d4af37]/50 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-[#d4af37] focus:border-[#d4af37] transition-all text-sm resize-none"
        />
        {detectedInputType && (
          <p className="text-xs text-[#d4af37] mt-1 flex items-center">
            <span className="mr-1">ℹ️</span>
            Detected as: {detectedInputType === 'mnemonic' ? 'Mnemonic' : 'Private Key'}
            {detectedInputType === 'mnemonic' && ' (will use first address)'}
          </p>
        )}
      </div>

      {/* Target Address */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white mb-2">
          Target Address *
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
          Transfer Amount (BNB) *
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
          Hops: <span className="text-[#d4af37]">{numHops}</span> <span className="text-xs text-gray-400">(more is stealthier)</span>
          <span className="ml-2 text-xs text-[#d4af37]">
            Est. {numHops <= 10 ? '~30s' : numHops <= 50 ? '~2.5min' : numHops <= 100 ? '~5min' : '~20min'}
          </span>
        </label>
        <p className="text-xs text-gray-400 mb-2">Multiple intermediate wallet addresses hide transfer paths for anonymous transfers and fund privacy.</p>
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
            placeholder="Custom"
          />
        </div>
      </div>
      {/* Fee Estimate */}
      <div className="bg-[#0a0a0a] border border-[#d4af37]/30 p-4 rounded-lg mb-4 shadow-lg shadow-[#d4af37]/10">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-gray-400 text-xs">Service Fee</p>
            <p className="font-semibold text-[#d4af37]">
              {mode === 'ultimate' && amount
                ? (parseFloat(amount) * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.percentageFee || 0) / 100).toFixed(4)
                : (numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)).toFixed(4)} BNB
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">Est. Gas</p>
            <p className="font-semibold text-[#d4af37]">~{(numHops * 0.00021).toFixed(5)} BNB</p>
          </div>
          {mode === 'ultimate' && (
            <div>
              <p className="text-gray-400 text-xs">Cross-chain Fee</p>
              <p className="font-semibold text-[#ffa500]">
                ~{MIXING_MODES[mode as keyof typeof MIXING_MODES]?.crosschainFee || 0} BNB
              </p>
            </div>
          )}
          <div>
            <p className="text-gray-400 text-xs">Total Fee</p>
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
            <p className="text-gray-400 text-xs">Expected Receive</p>
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
        {/* Glow animation effect */}
        {!isLoading && privateKey && toAddress && amount && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
        )}
        
        {isLoading ? (
          <div className="relative z-10">
            <div className="flex items-center justify-center mb-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-black mr-2"></div>
              <span>Processing {progressPercent}%</span>
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
          <span className="relative z-10">Secure Transfer</span>
        )}
      </button>

      {/* FAQ Section */}
      <div className="mt-6">
        <h3 className="text-sm font-semibold text-[#d4af37] mb-3 border-b border-[#d4af37]/30 pb-2">FAQ</h3>
        <div className="space-y-2">
          {/* FAQ 1 */}
          <div className="border border-[#d4af37]/20 rounded-lg overflow-hidden bg-[#0a0a0a]">
            <button
              onClick={() => setExpandedFaq(expandedFaq === 1 ? null : 1)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#1a1a1a] transition border-l-2 border-l-[#d4af37]/50"
            >
              <span className="text-sm font-medium text-white">How to ensure transfers are completely untraceable?</span>
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
                <p className="font-semibold mb-2">Technical Principle:</p>
                <p className="mb-3">We use <strong>multi-layer isolation architecture</strong> to completely sever fund tracing at the technical level:</p>
                
                <p className="font-semibold mb-1">Fast Mode - Dual-layer Isolation:</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li><strong>First Layer</strong>: Source → Temp Address T1 (cut source)</li>
                  <li><strong>Mixing Layer</strong>: T1 randomly hops through 10-100 HD wallet addresses</li>
                  <li><strong>Second Layer</strong>: Temp Address T2 → Target (cut destination)</li>
                </ul>
                
                <p className="font-semibold mb-1">On-chain Trace Analysis:</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>Blockchain explorer only sees: A → T1 (no continuation)</li>
                  <li>Middle layer: T1 → B1 → C3 → B5 → C2... (random path)</li>
                  <li>Final layer: T2 → Z (no predecessor)</li>
                  <li><strong>Conclusion</strong>: Even with Chainalysis tools, cannot link A to Z</li>
                </ul>
                
                <p className="font-semibold mb-1">Ultimate Privacy - Cross-chain Break:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Mix to <strong>new temp address</strong> before each cross-chain</li>
                  <li>Bridge records: Temp B → Temp C (different chains)</li>
                  <li>Unlinkable: Source A on BSC, Target Z on BSC, but via Polygon, Arbitrum</li>
                  <li><strong>IP Protection</strong>: Auto proxy pool, different IP per request</li>
                  <li><strong>Time Obfuscation</strong>: 5-30min random delays break timing patterns</li>
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
              <span className="text-sm font-medium text-white">How is fund security guaranteed? Risk of theft or loss?</span>
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
                <p className="font-semibold mb-2">Decentralized Architecture Guarantee:</p>
                
                <p className="font-semibold text-green-700 mb-1">✅ Non-custodial Design</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>All intermediate addresses derived from your mnemonic via BIP44</li>
                  <li>Private keys fully controlled by you, we cannot touch your funds</li>
                  <li>No fund pool, no centralized servers</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ On-chain Verifiable</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>Each transaction has unique hash, queryable on blockchain explorer</li>
                  <li>Smart contracts open source, code logic transparent and auditable</li>
                  <li>All operations executed on-chain, immutable</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ Mnemonic Security</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>Mnemonic only used locally in your browser, never uploaded</li>
                  <li>Recommend using hardware wallet generated mnemonic</li>
                  <li>After mixing, intermediate addresses auto-cleared, no balance left</li>
                </ul>
                
                <p className="font-semibold text-orange-700 mb-1">⚠️ Security Recommendations</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>First time use: test with small amount (0.01-0.05 BNB)</li>
                  <li>Keep mnemonic safe, loss is unrecoverable</li>
                  <li>Confirm target address correct, on-chain transactions irreversible</li>
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
              <span className="text-sm font-medium text-white">What's the key difference in privacy protection between modes?</span>
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
                <p className="font-semibold mb-2">Fast Mode - Single-chain Deep Obfuscation:</p>
                <p className="mb-1"><strong>Use Case:</strong> Daily transfers, small amounts (&lt;0.5 BNB), need fast arrival (30s-5min)</p>
                <p className="mb-1"><strong>Technical Features:</strong> Dual-layer isolation + multi-hop mixing, 10-100 intermediate addresses random hops</p>
                <p className="mb-3"><strong>Privacy Level:</strong> ⭐⭐⭐⭐⭐ Resistant to blockchain explorers, common analysis tools</p>
                
                <p className="font-semibold mb-2">Ultimate Privacy - Cross-chain Ghost Mode:</p>
                <p className="mb-1"><strong>Use Case:</strong> Large fund transfers (&gt;0.5 BNB), need highest privacy protection</p>
                <p className="mb-1"><strong>Technical Features:</strong></p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>Cross-chain break: BSC → Polygon → Arbitrum → BSC (68+ chains available)</li>
                  <li>New temp address for each cross-chain (bridge cannot link)</li>
                  <li>Auto proxy pool: different IP per request, network layer untraceable</li>
                  <li>5-30min random delays: break timing correlation patterns</li>
                </ul>
                <p className="mb-2"><strong>Privacy Level:</strong> ⭐⭐⭐⭐⭐⭐⭐ Resistant to Chainalysis, Elliptic and other pro tools</p>
                
                <p className="font-semibold">Core Difference:</p>
                <p>Fast Mode: Single-chain obfuscation, speed priority | Ultimate Privacy: Cross-chain break, privacy priority</p>
              </div>
            )}
          </div>

          {/* FAQ 4 */}
          <div className="border border-[#d4af37]/20 rounded-lg overflow-hidden bg-[#0a0a0a]">
            <button
              onClick={() => setExpandedFaq(expandedFaq === 4 ? null : 4)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-[#1a1a1a] transition border-l-2 border-l-[#d4af37]/50"
            >
              <span className="text-sm font-medium text-white">Why provide mnemonic? Is it safe?</span>
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
                <p className="font-semibold mb-2">Technical Necessity:</p>
                <p className="mb-1"><strong>HD Wallet Principle:</strong></p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>Mixing requires generating 10-100 intermediate addresses</li>
                  <li>Use BIP44 standard to derive child addresses from mnemonic</li>
                  <li>Each child address has independent private key for signing transactions</li>
                </ul>
                
                <p className="mb-1"><strong>Why not use single private key:</strong></p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>Single private key only controls one address</li>
                  <li>Cannot generate multiple intermediate addresses for mixing</li>
                  <li>HD wallet can derive unlimited addresses from one mnemonic</li>
                </ul>
                
                <p className="font-semibold mb-2">Security Guarantee:</p>
                <p className="font-semibold text-green-700 mb-1">✅ Local Processing</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>Mnemonic only used in your browser</li>
                  <li>Not sent to server or any third party</li>
                  <li>All derivation calculations done locally</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ Temporary Use</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>After mixing, intermediate addresses auto-cleared</li>
                  <li>No balance left in intermediate addresses</li>
                  <li>Recommend using dedicated mnemonic, not main wallet</li>
                </ul>
                
                <p className="font-semibold mb-1">Best Practices:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Use newly generated mnemonic (not main wallet)</li>
                  <li>After mixing, can discard the mnemonic</li>
                  <li>Or use hardware wallet generated mnemonic</li>
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
              <span className="text-sm font-medium text-white">What if transaction fails or gets stuck?</span>
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
                <p className="font-semibold mb-2">Fault Tolerance Mechanism:</p>
                
                <p className="font-semibold text-green-700 mb-1">✅ Auto Retry</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>Failed transactions auto-retry 3 times</li>
                  <li>Insufficient gas price auto-increased and resent</li>
                  <li>Network congestion waits then retries</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ Fund Protection</p>
                <ul className="list-disc list-inside mb-2 space-y-1 ml-2">
                  <li>Failed transactions don't deduct funds</li>
                  <li>Intermediate address balances auto-collected</li>
                  <li>No funds stuck in intermediate addresses</li>
                </ul>
                
                <p className="font-semibold text-green-700 mb-1">✅ Real-time Monitoring</p>
                <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
                  <li>Page shows real-time transaction status</li>
                  <li>Can see current progress and remaining time</li>
                  <li>Each transaction has hash, queryable on blockchain explorer</li>
                </ul>
                
                <p className="font-semibold mb-2">Common Issue Handling:</p>
                <p className="mb-1"><strong>Case 1: Transaction pending long time</strong></p>
                <p className="mb-2 ml-2">Cause: Network congestion | Solution: System auto-increases gas and resends</p>
                
                <p className="mb-1"><strong>Case 2: Partial transaction failure</strong></p>
                <p className="mb-2 ml-2">Cause: Insufficient balance | Solution: System collects completed portions</p>
                
                <p className="mb-1"><strong>Case 3: Cross-chain stuck (Ultimate Privacy)</strong></p>
                <p className="ml-2">Cause: Bridge congestion | Solution: Wait for cross-chain confirmation (usually 5-30min)</p>
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
              <span>Processing...</span>
            </div>
          )}
        </div>
      )}

      {/* Result - Only show on error */}
      {result && !result.success && (
        <div className="mt-4 p-4 rounded-lg text-sm bg-red-900/20 border border-red-500/30">
          <h3 className="font-semibold mb-2 text-red-400">
            ❌ Execution Failed
          </h3>
          <p className="text-xs text-red-300">{result.error}</p>
        </div>
      )}
    </div>
  );
}

// Coming Soon component
function ComingSoonApp({ tool }: { tool: any }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 text-center">
      <div className="text-6xl mb-4">{tool.icon}</div>
      <h2 className="text-2xl font-bold mb-2">{tool.name}</h2>
      <p className="text-gray-600 mb-6">{tool.description}</p>
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-700 font-semibold">🚧 Coming Soon</p>
        <p className="text-sm text-gray-600 mt-2">Stay tuned...</p>
      </div>
    </div>
  );
}

export default function Home() {
  const [lang, setLang] = useState<"en" | "zh">("en");
  const [selectedTool, setSelectedTool] = useState(tools[0]);
  const [dailyUsage, setDailyUsage] = useState(0);

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
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Tool List */}
          <div className="lg:col-span-1">
            <div className="bg-[#1a1a1a] border border-[#d4af37]/20 rounded-xl p-4 sticky top-24">
              <h2 className="text-lg font-bold mb-4 text-[#d4af37]">Tools</h2>
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
                          {tool.category === "privacy" ? "Privacy" : 
                           tool.category === "wallet" ? "Wallet" :
                           tool.category === "defi" ? "DeFi" : "Analytics"}
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
                        <div className="text-xs text-gray-400">Daily Usage</div>
                      </div>
                      <div className="bg-[#0a0a0a] border border-[#10b981]/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-[#10b981]">{selectedTool.users}</div>
                        <div className="text-xs text-gray-400">Total Users</div>
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
