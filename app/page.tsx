"use client";

import { useState } from "react";
import { API_URL } from "@/lib/config";

// 工具数据
const tools = [
  {
    id: 1,
    name: "鬼魅多跳混币器",
    category: "privacy",
    description: "唯一无法追踪的混币器，N次交叉转账跨链100%隐藏资金路径，安全保护隐私",
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
    feeRate: 0.0003
  },
  ultimate: {
    name: "极致隐私",
    icon: "🛡️",
    privacy: "⭐⭐⭐⭐⭐⭐⭐",
    time: "8-50 小时",
    description: "多链幽灵模式 · 完全匿名 · 无法追踪",
    color: "red",
    feeRate: 0.0006
  }
};

// 鬼魅多跳混币器组件
function StealthTransferApp() {
  const [chain, setChain] = useState("bsc_testnet");
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

  const handleExecute = async () => {
    if (!privateKey || !toAddress || !amount) {
      alert("请填写所有必填字段");
      return;
    }

    setIsLoading(true);
    setResult(null);
    setProgress([]);

    try {
      setProgress(prev => [...prev, "🚀 开始混币..."]);
      setProgress(prev => [...prev, `🎯 模式: ${MIXING_MODES[mode as keyof typeof MIXING_MODES].name}`]);
      setProgress(prev => [...prev, `📊 跳数: ${numHops}`]);
      
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

      const data = await response.json();
      
      if (data.success && data.results) {
        setProgress(prev => [...prev, "\n📦 交易详情:"]);
        
        const step1 = data.results.filter((r: any) => r.step === 1);
        const step2 = data.results.filter((r: any) => r.step === 2);
        const step3 = data.results.filter((r: any) => r.step === 3);
        
        if (step1.length > 0) {
          setProgress(prev => [...prev, `✅ 步骤 1: 分散 ${step1.length} 次`]);
        }
        
        if (step2.length > 0) {
          setProgress(prev => [...prev, `✅ 步骤 2: 跳转 ${step2.length} 次`]);
        }
        
        if (step3.length > 0) {
          setProgress(prev => [...prev, `✅ 步骤 3: 汇总完成`]);
        }
        
        setProgress(prev => [...prev, `\n🎉 完成！收到: ${data.total_collected} BNB`]);
      }
      
      setResult(data);
    } catch (error) {
      setProgress(prev => [...prev, `❌ 错误: ${error}`]);
      setResult({ success: false, error: String(error) });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-bold mb-6">鬼魅多跳混币器</h2>
      
      {/* Mixing Mode Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          混币模式
        </label>
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
          <option value="bsc_testnet">BSC Testnet</option>
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
          跳数: {numHops}
        </label>
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
              {(numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)).toFixed(4)} BNB
            </p>
            <p className="text-xs text-gray-500">
              {numHops} 次 × {MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003} BNB
            </p>
          </div>
          <div>
            <p className="text-gray-600 text-xs">预估 Gas</p>
            <p className="font-semibold">~{(numHops * 0.00021).toFixed(5)} BNB</p>
          </div>
          <div>
            <p className="text-gray-600 text-xs">总费用</p>
            <p className="font-semibold text-purple-600">
              ~{((numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)) + numHops * 0.00021).toFixed(5)} BNB
            </p>
          </div>
          <div>
            <p className="text-gray-600 text-xs">预计收到</p>
            <p className="font-semibold text-green-600">
              {amount ? (parseFloat(amount) - (numHops * (MIXING_MODES[mode as keyof typeof MIXING_MODES]?.feeRate || 0.0003)) - numHops * 0.00021).toFixed(5) : "0"} BNB
            </p>
          </div>
        </div>
      </div>

      {/* Execute Button */}
      <button
        onClick={handleExecute}
        disabled={isLoading || !privateKey || !toAddress || !amount}
        className={`w-full py-3 rounded-lg font-semibold transition ${
          isLoading || !privateKey || !toAddress || !amount
            ? "bg-gray-300 text-gray-500 cursor-not-allowed"
            : "bg-purple-600 text-white hover:bg-purple-700"
        }`}
      >
        {isLoading ? "执行中..." : "🚀 执行混币"}
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

      {/* Result */}
      {result && (
        <div className={`mt-4 p-4 rounded-lg text-sm ${result.success ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"}`}>
          <h3 className={`font-semibold mb-2 ${result.success ? "text-green-800" : "text-red-800"}`}>
            {result.success ? "✅ 执行成功" : "❌ 执行失败"}
          </h3>
          {result.success ? (
            <div className="text-xs space-y-1">
              <p>总交易数: {result.total_transactions}</p>
              <p>成功: {result.success_count}</p>
              <p>失败: {result.failed_count}</p>
              <p>目标地址收到: {result.total_collected} BNB</p>
              <p>服务费: {result.service_fee} BNB</p>
            </div>
          ) : (
            <p className="text-xs text-red-700">{result.error}</p>
          )}
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
                        <div className="text-lg font-bold text-purple-600">{selectedTool.rating}</div>
                        <div className="text-xs text-gray-600">评分</div>
                      </div>
                      <div className="bg-green-50 p-2 rounded text-center">
                        <div className="text-lg font-bold text-green-600">{selectedTool.users}</div>
                        <div className="text-xs text-gray-600">用户</div>
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
