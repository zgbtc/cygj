"use client";

import Link from "next/link";
import { useState } from "react";
import { API_URL } from "@/lib/config";

export default function StealthTransferPage() {
  const [chain, setChain] = useState("bsc_testnet");
  const [privateKey, setPrivateKey] = useState("");
  const [toAddress, setToAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [numHops, setNumHops] = useState(100);
  const [mnemonic, setMnemonic] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleExecute = async () => {
    if (!privateKey || !toAddress || !amount) {
      alert("请填写所有必填字段");
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/mixer/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chain,
          from_private_key: privateKey,
          to_address: toAddress,
          total_amount: parseFloat(amount),
          num_hops: numHops,
          mnemonic: mnemonic || undefined,
          gas_level: "standard"
        })
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ success: false, error: String(error) });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <nav className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2 text-purple-600 hover:text-purple-700">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
              <span className="font-semibold">返回首页</span>
            </Link>
            <div className="text-xl font-bold text-gray-800">
              Crypto Tools Hub
            </div>
          </div>
        </nav>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Sidebar - Tool Info */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-8">
              <div className="text-center mb-6">
                <div className="text-6xl mb-4">🎭</div>
                <h1 className="text-2xl font-bold mb-2">Stealth Transfer</h1>
                <p className="text-gray-600 text-sm">多跳混币器</p>
              </div>

              <div className="space-y-4 mb-6">
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">4.8</div>
                  <div className="text-xs text-gray-600">用户评分</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">1.2K+</div>
                  <div className="text-xs text-gray-600">活跃用户</div>
                </div>
              </div>

              <div className="border-t pt-4 mb-4">
                <h3 className="font-semibold mb-3 text-sm">工作原理</h3>
                <div className="space-y-3 text-xs">
                  <div className="flex items-start">
                    <div className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center font-bold mr-2 flex-shrink-0 text-xs">1</div>
                    <div>
                      <p className="font-medium">生成中间地址</p>
                      <p className="text-gray-500">从助记词生成多个地址</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center font-bold mr-2 flex-shrink-0 text-xs">2</div>
                    <div>
                      <p className="font-medium">多跳交叉转账</p>
                      <p className="text-gray-500">资金通过多个地址跳转</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center font-bold mr-2 flex-shrink-0 text-xs">3</div>
                    <div>
                      <p className="font-medium">汇总到目标地址</p>
                      <p className="text-gray-500">最终资金到达目标</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4 mb-4">
                <h3 className="font-semibold mb-3 text-sm">费用说明</h3>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-600">10 跳</span>
                    <span className="font-semibold">0.003 BNB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">50 跳</span>
                    <span className="font-semibold">0.015 BNB</span>
                  </div>
                  <div className="flex justify-between bg-purple-50 p-2 rounded">
                    <span className="text-gray-600">100 跳 ⭐</span>
                    <span className="font-semibold text-purple-600">0.03 BNB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">500 跳</span>
                    <span className="font-semibold">0.15 BNB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">1000 跳</span>
                    <span className="font-semibold">0.30 BNB</span>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 text-xs">
                <p className="text-yellow-700">
                  <strong>提示：</strong> 建议先在测试网测试
                </p>
              </div>
            </div>
          </div>

          {/* Right Panel - Application */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold mb-6">BSC Stealth Transfer</h2>
              
              {/* Chain Selection */}
              <div className="mb-6">
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
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  源地址私钥 *
                </label>
                <input
                  type="password"
                  value={privateKey}
                  onChange={(e) => setPrivateKey(e.target.value)}
                  placeholder="输入私钥"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Target Address */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  目标地址 *
                </label>
                <input
                  type="text"
                  value={toAddress}
                  onChange={(e) => setToAddress(e.target.value)}
                  placeholder="0x..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Amount */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  转账金额 (BNB) *
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.1"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Number of Hops */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  跳数: {numHops}
                </label>
                <div className="flex gap-2 mb-3">
                  {[10, 50, 100, 500, 1000].map((num) => (
                    <button
                      key={num}
                      onClick={() => setNumHops(num)}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
                        numHops === num
                          ? "bg-purple-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {num}
                    </button>
                  ))}
                </div>
                <input
                  type="range"
                  min="10"
                  max="1000"
                  step="10"
                  value={numHops}
                  onChange={(e) => setNumHops(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Mnemonic (Optional) */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  助记词（可选，留空自动生成）
                </label>
                <input
                  type="text"
                  value={mnemonic}
                  onChange={(e) => setMnemonic(e.target.value)}
                  placeholder="12 个单词，空格分隔"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Fee Estimate */}
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">服务费</p>
                    <p className="font-semibold">
                      {numHops === 10 ? "0.003" : numHops === 50 ? "0.015" : numHops === 100 ? "0.03" : numHops === 500 ? "0.15" : "0.30"} BNB
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">预估 Gas</p>
                    <p className="font-semibold">~{(numHops * 0.00021).toFixed(5)} BNB</p>
                  </div>
                  <div>
                    <p className="text-gray-600">总费用</p>
                    <p className="font-semibold text-purple-600">
                      ~{(parseFloat(numHops === 10 ? "0.003" : numHops === 50 ? "0.015" : numHops === 100 ? "0.03" : numHops === 500 ? "0.15" : "0.30") + numHops * 0.00021).toFixed(5)} BNB
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">预计收到</p>
                    <p className="font-semibold text-green-600">
                      {amount ? (parseFloat(amount) - parseFloat(numHops === 10 ? "0.003" : numHops === 50 ? "0.015" : numHops === 100 ? "0.03" : numHops === 500 ? "0.15" : "0.30") - numHops * 0.00021).toFixed(5) : "0"} BNB
                    </p>
                  </div>
                </div>
              </div>

              {/* Execute Button */}
              <button
                onClick={handleExecute}
                disabled={isLoading || !privateKey || !toAddress || !amount}
                className={`w-full py-4 rounded-lg font-semibold text-lg transition ${
                  isLoading || !privateKey || !toAddress || !amount
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-purple-600 text-white hover:bg-purple-700"
                }`}
              >
                {isLoading ? "执行中..." : "🚀 执行混币"}
              </button>

              {/* Result */}
              {result && (
                <div className={`mt-6 p-4 rounded-lg ${result.success ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"}`}>
                  <h3 className={`font-semibold mb-2 ${result.success ? "text-green-800" : "text-red-800"}`}>
                    {result.success ? "✅ 执行成功" : "❌ 执行失败"}
                  </h3>
                  {result.success ? (
                    <div className="text-sm space-y-2">
                      <p>总交易数: {result.total_transactions}</p>
                      <p>成功: {result.success_count}</p>
                      <p>失败: {result.failed_count}</p>
                      <p>目标地址收到: {result.total_collected} BNB</p>
                      <p>服务费: {result.service_fee} BNB</p>
                    </div>
                  ) : (
                    <p className="text-sm text-red-700">{result.error}</p>
                  )}
                </div>
              )}

              {/* Warning */}
              <div className="mt-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path>
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-yellow-700">
                      <strong>安全提示：</strong> 请妥善保管私钥和助记词，不要泄露给任何人。建议先在测试网测试。刷新或关闭页面将中断程序。
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
