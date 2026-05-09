"use client";

import Link from "next/link";
import { useState } from "react";
import { Globe, ArrowLeft } from "lucide-react";

export default function PrivacyPage() {
  const [lang, setLang] = useState<"en" | "zh">("en");

  const content = {
    en: {
      title: "Privacy Policy",
      backHome: "Back to Home",
      lastUpdated: "Last Updated: January 2024",
      sections: [
        {
          title: "1. Introduction",
          content: "CYGJ Crypto Tools (\"we\", \"our\", or \"us\") is committed to protecting your privacy. This Privacy Policy explains how we handle information when you use our service."
        },
        {
          title: "2. Information We DO NOT Collect",
          content: "We prioritize your privacy and security. We DO NOT collect, store, or transmit:\n• Private keys or mnemonic phrases\n• Wallet addresses or transaction details\n• Personal identification information (name, email, phone)\n• IP addresses or location data\n• Browsing history or usage patterns\n• Any sensitive financial information"
        },
        {
          title: "3. How Our Service Works",
          content: "All cryptographic operations are performed locally in your browser:\n• Private keys never leave your device\n• Transactions are signed locally\n• No data is sent to our servers\n• We operate a non-custodial service\n\nThis architecture ensures maximum privacy and security for our users."
        },
        {
          title: "4. Blockchain Transparency",
          content: "Please note that blockchain transactions are public and permanent:\n• All transactions are recorded on public blockchains\n• Transaction details can be viewed by anyone using blockchain explorers\n• While we provide privacy-enhancing tools, blockchain data remains publicly accessible\n• Users should understand the inherent transparency of blockchain technology"
        },
        {
          title: "5. Cookies and Local Storage",
          content: "We may use minimal browser storage for:\n• User interface preferences (language selection)\n• Session management\n• Performance optimization\n\nNo personal or sensitive data is stored. You can clear this data at any time through your browser settings."
        },
        {
          title: "6. Third-Party Services",
          content: "Our service interacts with:\n• Public blockchain networks (BSC, Ethereum, etc.)\n• Blockchain RPC providers\n• Cross-chain bridge protocols\n\nThese third parties have their own privacy policies. We recommend reviewing their policies as well."
        },
        {
          title: "7. Analytics",
          content: "We do not use analytics or tracking tools. We do not monitor user behavior or collect usage statistics."
        },
        {
          title: "8. Data Security",
          content: "Security measures we implement:\n• All operations performed client-side\n• No server-side storage of sensitive data\n• Open-source code for transparency\n• Regular security audits\n\nHowever, users are responsible for:\n• Securing their own devices\n• Using secure networks (VPN recommended)\n• Protecting their private keys and credentials"
        },
        {
          title: "9. Children's Privacy",
          content: "Our service is not intended for users under 18 years of age. We do not knowingly collect information from children."
        },
        {
          title: "10. International Users",
          content: "Our service is accessible globally. Users are responsible for complying with their local laws and regulations regarding cryptocurrency use and privacy."
        },
        {
          title: "11. Your Rights",
          content: "Since we do not collect personal data, there is no data to:\n• Access or download\n• Correct or update\n• Delete or erase\n\nYour privacy is protected by design."
        },
        {
          title: "12. Changes to Privacy Policy",
          content: "We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated revision date. Continued use of the service constitutes acceptance of the updated policy."
        },
        {
          title: "13. Contact Us",
          content: "If you have questions about this Privacy Policy, please contact us through our official channels."
        }
      ]
    },
    zh: {
      title: "隐私政策",
      backHome: "返回首页",
      lastUpdated: "最后更新：2024年1月",
      sections: [
        {
          title: "1. 简介",
          content: "CYGJ 加密工具集（\"我们\"）致力于保护您的隐私。本隐私政策说明了您使用我们的服务时我们如何处理信息。"
        },
        {
          title: "2. 我们不收集的信息",
          content: "我们优先考虑您的隐私和安全。我们不收集、存储或传输：\n• 私钥或助记词\n• 钱包地址或交易详情\n• 个人身份信息（姓名、电子邮件、电话）\n• IP 地址或位置数据\n• 浏览历史或使用模式\n• 任何敏感的财务信息"
        },
        {
          title: "3. 服务工作原理",
          content: "所有加密操作均在您的浏览器本地执行：\n• 私钥永远不会离开您的设备\n• 交易在本地签名\n• 没有数据发送到我们的服务器\n• 我们运营非托管服务\n\n这种架构确保为用户提供最大的隐私和安全性。"
        },
        {
          title: "4. 区块链透明度",
          content: "请注意，区块链交易是公开且永久的：\n• 所有交易都记录在公共区块链上\n• 任何人都可以使用区块链浏览器查看交易详情\n• 虽然我们提供隐私增强工具，但区块链数据仍然是公开可访问的\n• 用户应了解区块链技术固有的透明性"
        },
        {
          title: "5. Cookie 和本地存储",
          content: "我们可能使用最少的浏览器存储用于：\n• 用户界面偏好设置（语言选择）\n• 会话管理\n• 性能优化\n\n不存储个人或敏感数据。您可以随时通过浏览器设置清除这些数据。"
        },
        {
          title: "6. 第三方服务",
          content: "我们的服务与以下服务交互：\n• 公共区块链网络（BSC、以太坊等）\n• 区块链 RPC 提供商\n• 跨链桥接协议\n\n这些第三方有自己的隐私政策。我们建议您也查看他们的政策。"
        },
        {
          title: "7. 分析",
          content: "我们不使用分析或跟踪工具。我们不监控用户行为或收集使用统计数据。"
        },
        {
          title: "8. 数据安全",
          content: "我们实施的安全措施：\n• 所有操作在客户端执行\n• 服务器端不存储敏感数据\n• 开源代码以确保透明度\n• 定期安全审计\n\n但是，用户需要负责：\n• 保护自己的设备安全\n• 使用安全网络（建议使用 VPN）\n• 保护他们的私钥和凭证"
        },
        {
          title: "9. 儿童隐私",
          content: "我们的服务不适用于 18 岁以下的用户。我们不会故意收集儿童的信息。"
        },
        {
          title: "10. 国际用户",
          content: "我们的服务可在全球范围内访问。用户有责任遵守其当地关于加密货币使用和隐私的法律法规。"
        },
        {
          title: "11. 您的权利",
          content: "由于我们不收集个人数据，因此没有数据可以：\n• 访问或下载\n• 更正或更新\n• 删除或清除\n\n您的隐私通过设计得到保护。"
        },
        {
          title: "12. 隐私政策变更",
          content: "我们可能会不时更新本隐私政策。更改将发布在此页面上，并附有更新的修订日期。继续使用服务即表示接受更新后的政策。"
        },
        {
          title: "13. 联系我们",
          content: "如果您对本隐私政策有疑问，请通过我们的官方渠道与我们联系。"
        }
      ]
    }
  };

  const t = content[lang];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <nav className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2 text-purple-600 hover:text-purple-700 transition">
              <ArrowLeft className="w-5 h-5" />
              <span className="font-semibold">{t.backHome}</span>
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

      {/* Content */}
      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="bg-white rounded-xl shadow-lg p-8 md:p-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">{t.title}</h1>
          <p className="text-sm text-gray-500 mb-8">{t.lastUpdated}</p>

          <div className="prose prose-lg max-w-none">
            {t.sections.map((section, index) => (
              <div key={index} className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-800 mb-3">
                  {section.title}
                </h2>
                <p className="text-gray-600 leading-relaxed whitespace-pre-line">
                  {section.content}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-12 p-6 bg-green-50 border-l-4 border-green-400 rounded">
            <p className="text-sm text-green-800 font-medium">
              {lang === "en" 
                ? "🔒 Your privacy is our priority. We do not collect, store, or transmit any sensitive information."
                : "🔒 您的隐私是我们的首要任务。我们不收集、存储或传输任何敏感信息。"
              }
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
