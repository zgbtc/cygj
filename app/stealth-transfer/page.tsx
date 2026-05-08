"use client";

import Link from "next/link";
import { useState } from "react";
import { API_URL } from "@/lib/config";

export default function StealthTransferPage() {
  const [lang, setLang] = useState<"en" | "zh">("en");
  const [chain, setChain] = useState("bsc_testnet");
  const [inputType, setInputType] = useState<"private_key" | "mnemonic">("private_key");
  const [privateKey, setPrivateKey] = useState("");
  const [mnemonic, setMnemonic] = useState("");
  const [toAddress, setToAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [numHops, setNumHops] = useState(100);
  const [customHops, setCustomHops] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState<string[]>([]);

  const t = {
    en: {
      backHome: "Back to Home",
      title: "Stealth Transfer Mixer",
      subtitle: "Untraceable Crypto Mixer",
      userRating: "User Rating",
      activeUsers: "Active Users",
      howItWorks: "How It Works",
      step1Title: "Generate Intermediate Addresses",
      step1Desc: "Create multiple addresses from mnemonic",
      step2Title: "Multi-hop Cross Transfers",
      step2Desc: "Funds jump through multiple addresses",
      step3Title: "Collect to Target Address",
      step3Desc: "Final funds arrive at destination",
      feeStructure: "Fee Structure",
      hops: "hops",
      tip: "Tip:",
      tipText: "Test on testnet first",
      selectNetwork: "Select Network",
      mainnetWarning: "⚠️ Mainnet: Use ≥0.1 BNB to avoid gas depletion",
      inputMethod: "Input Method *",
      privateKey: "Private Key",
      mnemonic: "Mnemonic",
      sourcePrivateKey: "Source Private Key *",
      enterPrivateKey: "Enter private key",
      mnemonicPhrase: "Mnemonic Phrase *",
      enterMnemonic: "Enter 12 or 24 word mnemonic phrase",
      mnemonicNote: "Will use the first address (m/44'/60'/0'/0/0) as source",
      targetAddress: "Target Address *",
      transferAmount: "Transfer Amount (BNB) *",
      numHops: "Number of Hops:",
      custom: "Custom",
      serviceFee: "Service Fee",
      estimatedGas: "Estimated Gas",
      totalFee: "Total Fee",
      expectedReceive: "Expected Receive",
      executeButton: "🚀 Execute Mixing",
      executing: "Executing...",
      fillAllFields: "Please fill all required fields",
      startMixing: "🚀 Starting mixing...",
      hopsLabel: "📊 Hops:",
      amountLabel: "💰 Amount:",
      txDetails: "📦 Transaction Details:",
      step1: "Step 1: Distribute to",
      intermediateAddresses: "intermediate addresses",
      step2: "Step 2: Intermediate address hops",
      times: "times",
      moreHops: "more hops",
      step3: "Step 3: Collect to target address",
      received: "Received",
      mixingComplete: "🎉 Mixing complete!",
      targetReceived: "💵 Target address received:",
      processing: "Processing...",
      executionSuccess: "✅ Execution Successful",
      executionFailed: "❌ Execution Failed",
      totalTx: "Total Transactions:",
      success: "Success:",
      failed: "Failed:",
      error: "❌ Error:"
    },
    zh: {
      backHome: "返回首页",
      title: "鬼魅无影混币引擎",
      subtitle: "唯一无法追踪的混币器",
      userRating: "用户评分",
      activeUsers: "活跃用户",
      howItWorks: "工作原理",
      step1Title: "生成中间地址",
      step1Desc: "从助记词生成多个地址",
      step2Title: "多跳交叉转账",
      step2Desc: "资金通过多个地址跳转",
      step3Title: "汇总到目标地址",
      step3Desc: "最终资金到达目标",
      feeStructure: "费用说明",
      hops: "跳",
      tip: "提示：",
      tipText: "建议先在测试网测试",
      selectNetwork: "选择网络",
      mainnetWarning: "⚠️ 主网建议使用 ≥0.1 BNB，避免 Gas 费用消耗完所有金额",
      inputMethod: "输入方式 *",
      privateKey: "私钥",
      mnemonic: "助记词",
      sourcePrivateKey: "源地址私钥 *",
      enterPrivateKey: "输入私钥",
      mnemonicPhrase: "助记词 *",
      enterMnemonic: "输入 12 或 24 个单词的助记词",
      mnemonicNote: "将使用助记词的第一个地址（m/44'/60'/0'/0/0）作为源地址",
      targetAddress: "目标地址 *",
      transferAmount: "转账金额 (BNB) *",
      numHops: "跳数:",
      custom: "自定义",
      serviceFee: "服务费",
      estimatedGas: "预估 Gas",
      totalFee: "总费用",
      expectedReceive: "预计收到",
      executeButton: "🚀 执行混币",
      executing: "执行中...",
      fillAllFields: "请填写所有必填字段",
      startMixing: "🚀 开始混币...",
      hopsLabel: "📊 跳数:",
      amountLabel: "💰 金额:",
      txDetails: "📦 交易详情:",
      step1: "步骤 1: 分散到",
      intermediateAddresses: "个中间地址",
      step2: "步骤 2: 中间地址跳转",
      times: "次",
      moreHops: "次跳转",
      step3: "步骤 3: 汇总到目标地址",
      received: "收到",
      mixingComplete: "🎉 混币完成！",
      targetReceived: "💵 目标地址共收到:",
      processing: "处理中...",
      executionSuccess: "✅ 执行成功",
      executionFailed: "❌ 执行失败",
      totalTx: "总交易数:",
      success: "成功:",
      failed: "失败:",
      error: "❌ 错误:"
    }
  };

  const handleExecute = async () => {
    const inputValue = inputType === "private_key" ? privateKey : mnemonic;
    
    if (!inputValue || !toAddress || !amount) {
      alert(t[lang].fillAllFields);
      return;
    }

    setIsLoading(true);
    setResult(null);
    setProgress([]);

    try {
      // 添加初始进度
      setProgress(prev => [...prev, t[lang].startMixing]);
      setProgress(prev => [...prev, `${t[lang].hopsLabel} ${numHops}`]);
      setProgress(prev => [...prev, `${t[lang].amountLabel} ${amount} BNB`]);
      
      const requestBody: any = {
        chain,
        input_type: inputType,
        to_address: toAddress,
        total_amount: parseFloat(amount),
        num_hops: numHops,
        gas_level: "standard"
      };
      
      // 根据输入类型添加对应字段
      if (inputType === "private_key") {
        requestBody.from_private_key = privateKey;
      } else {
        requestBody.from_mnemonic = mnemonic;
      }
      
      const response = await fetch(`${API_URL}/api/mixer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();
      
      // 如果成功，显示详细进度
      if (data.success && data.results) {
        setProgress(prev => [...prev, `\n${t[lang].txDetails}`]);
        
        // 按步骤分组显示
        const step1 = data.results.filter((r: any) => r.step === 1);
        const step2 = data.results.filter((r: any) => r.step === 2);
        const step3 = data.results.filter((r: any) => r.step === 3);
        
        if (step1.length > 0) {
          setProgress(prev => [...prev, `\n✅ ${t[lang].step1} ${step1.length} ${t[lang].intermediateAddresses}`]);
          step1.forEach((r: any, i: number) => {
            if (r.status === 'success') {
              setProgress(prev => [...prev, `  ${i+1}. ${r.to.slice(0, 10)}... (${r.amount} BNB)`]);
            }
          });
        }
        
        if (step2.length > 0) {
          setProgress(prev => [...prev, `\n✅ ${t[lang].step2} ${step2.length} ${t[lang].times}`]);
          step2.slice(0, 5).forEach((r: any, i: number) => {
            if (r.status === 'success') {
              setProgress(prev => [...prev, `  ${i+1}. ${r.from.slice(0, 8)}... → ${r.to.slice(0, 8)}...`]);
            }
          });
          if (step2.length > 5) {
            setProgress(prev => [...prev, `  ... ${lang === 'en' ? 'and' : '还有'} ${step2.length - 5} ${t[lang].moreHops}`]);
          }
        }
        
        if (step3.length > 0) {
          setProgress(prev => [...prev, `\n✅ ${t[lang].step3}`]);
          step3.forEach((r: any, i: number) => {
            if (r.status === 'success') {
              setProgress(prev => [...prev, `  ${i+1}. ${t[lang].received} ${r.amount} BNB`]);
            }
          });
        }
        
        setProgress(prev => [...prev, `\n${t[lang].mixingComplete}`]);
        setProgress(prev => [...prev, `${t[lang].targetReceived} ${data.total_collected} BNB`]);
      }
      
      setResult(data);
    } catch (error) {
      setProgress(prev => [...prev, `\n${t[lang].error} ${error}`]);
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
              <span className="font-semibold">{t[lang].backHome}</span>
            </Link>
            <div className="flex items-center gap-4">
              <div className="text-xl font-bold text-gray-800">
                Crypto Tools Hub
              </div>
              <button
                onClick={() => setLang(lang === "en" ? "zh" : "en")}
                className="px-3 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-sm font-medium transition"
              >
                {lang === "en" ? "中文" : "EN"}
              </button>
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
                <h1 className="text-2xl font-bold mb-2">{t[lang].title}</h1>
                <p className="text-gray-600 text-sm">{t[lang].subtitle}</p>
              </div>

              <div className="space-y-4 mb-6">
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">4.8</div>
                  <div className="text-xs text-gray-600">{t[lang].userRating}</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">1.2K+</div>
                  <div className="text-xs text-gray-600">{t[lang].activeUsers}</div>
                </div>
              </div>

              <div className="border-t pt-4 mb-4">
                <h3 className="font-semibold mb-3 text-sm">{t[lang].howItWorks}</h3>
                <div className="space-y-3 text-xs">
                  <div className="flex items-start">
                    <div className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center font-bold mr-2 flex-shrink-0 text-xs">1</div>
                    <div>
                      <p className="font-medium">{t[lang].step1Title}</p>
                      <p className="text-gray-500">{t[lang].step1Desc}</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center font-bold mr-2 flex-shrink-0 text-xs">2</div>
                    <div>
                      <p className="font-medium">{t[lang].step2Title}</p>
                      <p className="text-gray-500">{t[lang].step2Desc}</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center font-bold mr-2 flex-shrink-0 text-xs">3</div>
                    <div>
                      <p className="font-medium">{t[lang].step3Title}</p>
                      <p className="text-gray-500">{t[lang].step3Desc}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4 mb-4">
                <h3 className="font-semibold mb-3 text-sm">{t[lang].feeStructure}</h3>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-600">10 {t[lang].hops}</span>
                    <span className="font-semibold">0.003 BNB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">50 {t[lang].hops}</span>
                    <span className="font-semibold">0.015 BNB</span>
                  </div>
                  <div className="flex justify-between bg-purple-50 p-2 rounded">
                    <span className="text-gray-600">100 {t[lang].hops} ⭐</span>
                    <span className="font-semibold text-purple-600">0.03 BNB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">500 {t[lang].hops}</span>
                    <span className="font-semibold">0.15 BNB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">1000 {t[lang].hops}</span>
                    <span className="font-semibold">0.30 BNB</span>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 text-xs">
                <p className="text-yellow-700">
                  <strong>{t[lang].tip}</strong> {t[lang].tipText}
                </p>
              </div>
            </div>
          </div>

          {/* Right Panel - Application */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold mb-6">{t[lang].title}</h2>
              
              {/* Chain Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t[lang].selectNetwork}
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
                {chain === 'bsc' && (
                  <p className="text-xs text-orange-600 mt-1">
                    {t[lang].mainnetWarning}
                  </p>
                )}
              </div>

              {/* Input Type Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t[lang].inputMethod}
                </label>
                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={() => setInputType("private_key")}
                    className={`flex-1 px-4 py-3 rounded-lg font-medium transition ${
                      inputType === "private_key"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    🔑 {t[lang].privateKey}
                  </button>
                  <button
                    type="button"
                    onClick={() => setInputType("mnemonic")}
                    className={`flex-1 px-4 py-3 rounded-lg font-medium transition ${
                      inputType === "mnemonic"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    📝 {t[lang].mnemonic}
                  </button>
                </div>
              </div>

              {/* Private Key or Mnemonic Input */}
              {inputType === "private_key" ? (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t[lang].sourcePrivateKey}
                  </label>
                  <input
                    type="password"
                    value={privateKey}
                    onChange={(e) => setPrivateKey(e.target.value)}
                    placeholder={t[lang].enterPrivateKey}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              ) : (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t[lang].mnemonicPhrase}
                  </label>
                  <textarea
                    value={mnemonic}
                    onChange={(e) => setMnemonic(e.target.value)}
                    placeholder={t[lang].enterMnemonic}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {t[lang].mnemonicNote}
                  </p>
                </div>
              )}

              {/* Target Address */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t[lang].targetAddress}
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
                  {t[lang].transferAmount}
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
                  {t[lang].numHops} {numHops}
                </label>
                <div className="flex gap-2">
                  {[10, 50, 100, 500, 1000].map((num) => (
                    <button
                      key={num}
                      onClick={() => {
                        setNumHops(num);
                        setCustomHops("");
                      }}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
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
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder={t[lang].custom}
                  />
                </div>
              </div>

              {/* Fee Estimate */}
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">{t[lang].serviceFee}</p>
                    <p className="font-semibold">
                      {numHops === 10 ? "0.003" : numHops === 50 ? "0.015" : numHops === 100 ? "0.03" : numHops === 500 ? "0.15" : "0.30"} BNB
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">{t[lang].estimatedGas}</p>
                    <p className="font-semibold">~{(numHops * 0.00021).toFixed(5)} BNB</p>
                  </div>
                  <div>
                    <p className="text-gray-600">{t[lang].totalFee}</p>
                    <p className="font-semibold text-purple-600">
                      ~{(parseFloat(numHops === 10 ? "0.003" : numHops === 50 ? "0.015" : numHops === 100 ? "0.03" : numHops === 500 ? "0.15" : "0.30") + numHops * 0.00021).toFixed(5)} BNB
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">{t[lang].expectedReceive}</p>
                    <p className="font-semibold text-green-600">
                      {amount ? (parseFloat(amount) - parseFloat(numHops === 10 ? "0.003" : numHops === 50 ? "0.015" : numHops === 100 ? "0.03" : numHops === 500 ? "0.15" : "0.30") - numHops * 0.00021).toFixed(5) : "0"} BNB
                    </p>
                  </div>
                </div>
              </div>

              {/* Execute Button */}
              <button
                onClick={handleExecute}
                disabled={isLoading || (!privateKey && !mnemonic) || !toAddress || !amount}
                className={`w-full py-4 rounded-lg font-semibold text-lg transition ${
                  isLoading || (!privateKey && !mnemonic) || !toAddress || !amount
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-purple-600 text-white hover:bg-purple-700"
                }`}
              >
                {isLoading ? t[lang].executing : t[lang].executeButton}
              </button>

              {/* Progress Display */}
              {progress.length > 0 && (
                <div className="mt-6 bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-y-auto">
                  {progress.map((line, index) => (
                    <div key={index} className="whitespace-pre-wrap">
                      {line}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="mt-2 flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-400 mr-2"></div>
                      <span>{t[lang].processing}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Result */}
              {result && (
                <div className={`mt-6 p-4 rounded-lg ${result.success ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"}`}>
                  <h3 className={`font-semibold mb-2 ${result.success ? "text-green-800" : "text-red-800"}`}>
                    {result.success ? t[lang].executionSuccess : t[lang].executionFailed}
                  </h3>
                  {result.success ? (
                    <div className="text-sm space-y-2">
                      <p>{t[lang].totalTx} {result.total_transactions}</p>
                      <p>{t[lang].success} {result.success_count}</p>
                      <p>{t[lang].failed} {result.failed_count}</p>
                      <p>{t[lang].targetReceived} {result.total_collected} BNB</p>
                      <p>{t[lang].serviceFee}: {result.service_fee} BNB</p>
                    </div>
                  ) : (
                    <p className="text-sm text-red-700">{result.error}</p>
                  )}
                </div>
              )}

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
