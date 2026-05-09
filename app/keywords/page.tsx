"use client";

import { useState } from "react";
import Link from "next/link";
import { Globe } from "lucide-react";
import {
  highDensityKeywords,
  mediumDensityKeywords,
  lowDensityKeywords,
  longTailKeywords,
  getAllKeywords
} from "@/lib/seo-keywords";

export default function KeywordsPage() {
  const [lang, setLang] = useState<"en" | "zh">("en");

  const t = {
    en: {
      title: "CYGJ Crypto Tools - Keywords & Features",
      subtitle: "Professional Web3 Toolbox for Crypto Hunters",
      description: "Comprehensive keyword index and feature overview",
      backHome: "← Back to Home",
      highDensity: "Core Features",
      mediumDensity: "Popular Tools",
      lowDensity: "Additional Features",
      longTail: "Extended Keywords"
    },
    zh: {
      title: "CYGJ 加密工具 - 关键词与功能",
      subtitle: "专业的 Web3 币工具箱",
      description: "完整的关键词索引和功能概览",
      backHome: "← 返回首页",
      highDensity: "核心功能",
      mediumDensity: "热门工具",
      lowDensity: "附加功能",
      longTail: "扩展关键词"
    }
  };

  const text = t[lang];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-sm text-gray-600 hover:text-[#d4af37] transition-colors">
            {text.backHome}
          </Link>
          
          {/* Language Toggle */}
          <button
            onClick={() => setLang(lang === "en" ? "zh" : "en")}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-[#d4af37]/10 transition-all duration-200 group"
          >
            <Globe className="w-4 h-4 text-gray-600 group-hover:text-[#d4af37]" />
            <span className="text-sm font-medium text-gray-700 group-hover:text-[#d4af37]">
              {lang === "en" ? "中文" : "English"}
            </span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        {/* Title Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {text.title}
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            {text.subtitle}
          </p>
          <p className="text-sm text-gray-500">
            {text.description}
          </p>
        </div>

        {/* SEO Content - High Density Keywords */}
        <section className="mb-12 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-[#d4af37] pb-2">
            {text.highDensity}
          </h2>
          <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed space-y-4">
            <p>
              CYGJ <strong className="text-[#d4af37]">币工具</strong>是专业的<strong className="text-[#d4af37]">Web3工具箱</strong>平台。
              我们的<strong className="text-[#d4af37]">币工具</strong>提供完整的<strong className="text-[#d4af37]">加密工具箱</strong>功能，
              支持68+条区块链。使用CYGJ <strong className="text-[#d4af37]">币工具</strong>，您可以访问强大的<strong className="text-[#d4af37]">加密货币工具</strong>集合。
            </p>
            <p>
              作为领先的<strong className="text-[#d4af37]">cointool</strong>平台，我们的<strong className="text-[#d4af37]">crypto toolbox</strong>包含批量钱包生成、
              隐私转账、批量转账等核心功能。CYGJ <strong className="text-[#d4af37]">币工具</strong>致力于为加密货币用户提供最专业的
              <strong className="text-[#d4af37]">Web3工具箱</strong>服务。
            </p>
            <p>
              我们的<strong className="text-[#d4af37]">加密工具箱</strong>支持BSC、ETH、Polygon等主流链。
              无论您需要<strong className="text-[#d4af37]">币工具</strong>进行批量操作，还是使用<strong className="text-[#d4af37]">crypto tools</strong>进行链上分析，
              CYGJ <strong className="text-[#d4af37]">cointool</strong>都能满足您的需求。
            </p>
            <p>
              选择CYGJ <strong className="text-[#d4af37]">币工具</strong>，就是选择专业的<strong className="text-[#d4af37]">Web3工具箱</strong>。
              我们的<strong className="text-[#d4af37]">加密工具箱</strong>经过数千用户验证，是您进行加密货币操作的最佳选择。
              立即体验CYGJ <strong className="text-[#d4af37]">币工具</strong>，开启您的<strong className="text-[#d4af37]">crypto toolbox</strong>之旅。
            </p>
          </div>
        </section>

        {/* Medium Density Keywords */}
        <section className="mb-12 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-[#d4af37] pb-2">
            {text.mediumDensity}
          </h2>
          <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed space-y-4">
            <p>
              <strong className="text-[#d4af37]">批量钱包生成</strong>是CYGJ币工具的核心功能之一。
              我们的<strong className="text-[#d4af37]">batch wallet generator</strong>支持BIP44标准，
              可以快速生成大量HD钱包地址。使用<strong className="text-[#d4af37]">批量钱包生成</strong>工具，
              您可以一次性创建10-10000个钱包地址。
            </p>
            <p>
              <strong className="text-[#d4af37]">隐私转账</strong>功能提供多跳跨链混币服务。
              我们的<strong className="text-[#d4af37]">stealth transfer</strong>支持68+条链，
              通过<strong className="text-[#d4af37]">隐匿转账</strong>技术保护您的链上隐私。
              <strong className="text-[#d4af37]">privacy transfer</strong>采用多层隔离架构，
              确保资金路径完全无法追踪。
            </p>
            <p>
              <strong className="text-[#d4af37]">批量转账</strong>工具支持一键发送Token到多个地址。
              使用<strong className="text-[#d4af37]">batch transfer</strong>功能，
              您可以导入CSV文件进行批量操作。我们的<strong className="text-[#d4af37]">批量转账</strong>系统
              自动优化Gas费用，为您节省成本。
            </p>
            <p>
              <strong className="text-[#d4af37]">HD钱包生成器</strong>基于BIP44标准开发。
              我们的<strong className="text-[#d4af37]">HD wallet generator</strong>支持助记词导入，
              可以派生无限数量的子地址。使用<strong className="text-[#d4af37]">HD钱包生成器</strong>，
              您可以安全地管理多个钱包地址。
            </p>
          </div>
        </section>

        {/* Low Density Keywords */}
        <section className="mb-12 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-[#d4af37] pb-2">
            {text.lowDensity}
          </h2>
          <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed space-y-4">
            <p>
              <strong className="text-[#d4af37]">批量地址查询</strong>功能支持一键查询多个地址余额。
              我们的<strong className="text-[#d4af37]">batch address check</strong>工具可以快速检查地址状态。
              <strong className="text-[#d4af37]">批量发送Token</strong>功能支持ERC-20、BEP-20等标准。
              使用<strong className="text-[#d4af37]">token multisender</strong>，您可以高效完成空投任务。
            </p>
            <p>
              <strong className="text-[#d4af37]">跨链转账</strong>支持多链资产转移。
              我们的<strong className="text-[#d4af37]">cross-chain transfer</strong>集成主流跨链桥。
              <strong className="text-[#d4af37]">DeFi工具</strong>包含流动性分析、收益计算等功能。
              使用<strong className="text-[#d4af37]">DeFi tools</strong>，您可以优化投资策略。
            </p>
            <p>
              <strong className="text-[#d4af37]">BSC工具</strong>专为币安智能链优化。
              我们的<strong className="text-[#d4af37]">BSC tools</strong>支持PancakeSwap等主流DEX。
              <strong className="text-[#d4af37]">ETH工具</strong>提供以太坊链上分析功能。
              使用<strong className="text-[#d4af37]">ETH tools</strong>，您可以追踪Gas价格和网络状态。
            </p>
            <p>
              <strong className="text-[#d4af37]">链上工具</strong>集合包含多种实用功能。
              我们的<strong className="text-[#d4af37]">on-chain tools</strong>支持交易追踪、地址标签等。
              <strong className="text-[#d4af37]">Gas追踪器</strong>实时监控网络Gas价格。
              <strong className="text-[#d4af37]">代币分析器</strong>提供持币分布、交易历史等数据。
              <strong className="text-[#d4af37]">NFT批量铸造</strong>支持ERC-721和ERC-1155标准。
            </p>
          </div>
        </section>

        {/* Long Tail Keywords - Tag Cloud */}
        <section className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-[#d4af37] pb-2">
            {text.longTail}
          </h2>
          <div className="flex flex-wrap gap-3">
            {longTailKeywords.map((keyword, index) => (
              <span
                key={index}
                className="px-4 py-2 bg-gray-100 hover:bg-[#d4af37]/10 text-gray-700 hover:text-[#d4af37] rounded-lg text-sm font-medium transition-all duration-200 cursor-default"
              >
                {keyword}
              </span>
            ))}
          </div>
        </section>

        {/* Additional SEO Content */}
        <section className="mt-12 bg-gradient-to-r from-[#d4af37]/5 to-[#ffd700]/5 rounded-xl p-8">
          <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed space-y-4">
            <p>
              CYGJ币工具作为专业的Web3工具箱，为全球加密货币用户提供一站式服务。
              我们的加密工具箱涵盖钱包管理、隐私保护、批量操作、链上分析等多个领域。
              无论您是DeFi玩家、NFT收藏家，还是加密货币交易者，CYGJ币工具都能满足您的需求。
            </p>
            <p>
              选择CYGJ crypto toolbox，您将获得：批量钱包生成器（支持BIP44标准）、
              隐私转账路由器（68+链支持）、批量转账工具（CSV导入）、HD钱包生成器、
              Gas追踪器、代币分析器、NFT批量铸造等强大功能。我们的币工具经过严格测试，
              确保安全可靠。
            </p>
            <p>
              立即访问 tool.cygj.us，体验最专业的Web3工具箱。CYGJ币工具 - 您的加密货币操作首选平台。
            </p>
          </div>
        </section>

        {/* Back to Home Button */}
        <div className="mt-12 text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-8 py-3 bg-[#d4af37] hover:bg-[#c9a332] text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
          >
            {text.backHome}
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-6 py-6 text-center text-sm text-gray-500">
          © 2024 CYGJ Crypto Tools. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
