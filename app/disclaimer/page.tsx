"use client";

import Link from "next/link";
import { useState } from "react";
import { Globe, ArrowLeft } from "lucide-react";

export default function DisclaimerPage() {
  const [lang, setLang] = useState<"en" | "zh">("zh");

  const content = {
    en: {
      title: "Disclaimer",
      backHome: "Back to Home",
      lastUpdated: "Last Updated: January 2024",
      sections: [
        {
          title: "1. General Disclaimer",
          content: "CYGJ Crypto Tools (\"the Service\") is provided for educational and research purposes only. By using this service, you acknowledge and agree that you use it at your own risk."
        },
        {
          title: "2. No Financial Advice",
          content: "The tools and services provided do not constitute financial, investment, legal, or tax advice. You should consult with appropriate professionals before making any financial decisions."
        },
        {
          title: "3. Risk of Loss",
          content: "Cryptocurrency transactions are irreversible. We are not responsible for any loss of funds, whether due to:\n• User error (wrong address, incorrect amount, etc.)\n• Technical issues (smart contract bugs, network congestion)\n• Network problems (RPC node failures, blockchain forks)\n• Gas fee depletion or transaction failures\n• Third-party service failures (cross-chain bridges, DEX protocols)\n• Any other cause\n\nAlways test with small amounts first."
        },
        {
          title: "4. No Guarantees",
          content: "We make no guarantees regarding the availability, reliability, or accuracy of the service. The service is provided \"as is\" without warranties of any kind, either express or implied."
        },
        {
          title: "5. User Responsibility",
          content: "You are solely responsible for:\n• Securing your private keys and mnemonic phrases\n• Verifying recipient addresses before transactions\n• Complying with applicable laws and regulations in your jurisdiction\n• Understanding the risks associated with cryptocurrency transactions"
        },
        {
          title: "6. Legal Compliance",
          content: "Users must comply with all applicable laws and regulations. The service should not be used for any illegal activities, including but not limited to money laundering, tax evasion, or financing illegal activities."
        },
        {
          title: "7. Privacy and Security",
          content: "While we implement security measures, we cannot guarantee absolute security. Users should take additional precautions such as using VPNs and secure networks when accessing the service."
        },
        {
          title: "8. Third-Party Services",
          content: "Our service may interact with third-party blockchain networks and services. We are not responsible for the actions, policies, or security of these third parties."
        },
        {
          title: "9. Service Modifications",
          content: "We reserve the right to modify, suspend, or discontinue the service at any time without prior notice."
        },
        {
          title: "10. Limitation of Liability",
          content: "To the maximum extent permitted by law, we shall not be liable for any direct, indirect, incidental, special, consequential, or punitive damages arising from your use of the service."
        }
      ]
    },
    zh: {
      title: "免责声明",
      backHome: "返回首页",
      lastUpdated: "最后更新：2024年1月",
      sections: [
        {
          title: "1. 总则",
          content: "CYGJ 加密工具集（\"本服务\"）仅供教育和研究目的使用。使用本服务即表示您承认并同意自行承担使用风险。"
        },
        {
          title: "2. 非财务建议",
          content: "本服务提供的工具和服务不构成财务、投资、法律或税务建议。在做出任何财务决策之前，您应咨询相关专业人士。"
        },
        {
          title: "3. 资金损失风险",
          content: "加密货币交易是不可逆的。我们不对任何资金损失负责，包括但不限于：\n• 用户错误（地址错误、金额错误等）\n• 技术问题（智能合约漏洞、网络拥堵）\n• 网络问题（RPC节点故障、区块链分叉）\n• Gas费耗尽或交易失败\n• 第三方服务故障（跨链桥、DEX协议等）\n• 任何其他原因\n\n请务必先用小额测试。"
        },
        {
          title: "4. 无担保",
          content: "我们不对服务的可用性、可靠性或准确性做任何保证。本服务按\"现状\"提供，不提供任何明示或暗示的担保。"
        },
        {
          title: "5. 用户责任",
          content: "您需要对以下事项负全部责任：\n• 保护您的私钥和助记词安全\n• 在交易前验证接收地址\n• 遵守您所在司法管辖区的适用法律法规\n• 了解与加密货币交易相关的风险"
        },
        {
          title: "6. 法律合规",
          content: "用户必须遵守所有适用的法律法规。本服务不得用于任何非法活动，包括但不限于洗钱、逃税或资助非法活动。"
        },
        {
          title: "7. 隐私与安全",
          content: "虽然我们实施了安全措施，但我们无法保证绝对安全。用户在访问服务时应采取额外的预防措施，例如使用 VPN 和安全网络。"
        },
        {
          title: "8. 第三方服务",
          content: "我们的服务可能与第三方区块链网络和服务交互。我们不对这些第三方的行为、政策或安全性负责。"
        },
        {
          title: "9. 服务修改",
          content: "我们保留随时修改、暂停或终止服务的权利，恕不另行通知。"
        },
        {
          title: "10. 责任限制",
          content: "在法律允许的最大范围内，我们不对因您使用本服务而产生的任何直接、间接、附带、特殊、后果性或惩罚性损害承担责任。"
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

          <div className="mt-12 p-6 bg-yellow-50 border-l-4 border-yellow-400 rounded">
            <p className="text-sm text-yellow-800 font-medium">
              {lang === "en" 
                ? "⚠️ Important: By using our service, you acknowledge that you have read, understood, and agreed to this disclaimer."
                : "⚠️ 重要提示：使用我们的服务即表示您已阅读、理解并同意本免责声明。"
              }
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
