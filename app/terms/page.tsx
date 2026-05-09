"use client";

import Link from "next/link";
import { useState } from "react";
import { Globe, ArrowLeft } from "lucide-react";

export default function TermsPage() {
  const [lang, setLang] = useState<"en" | "zh">("en");

  const content = {
    en: {
      title: "Terms of Service · Geographic Restrictions · Prohibited Conduct",
      backHome: "Back to Home",
      lastUpdated: "Last Updated: January 2024",
      sections: [
        {
          title: "1. Platform Statement",
          content: "This is a non-profit Web3 technical learning & research platform. We only provide off-chain technical routing, network privacy protection, multi-chain utilities and on-chain inquiry tools for academic reference only.\n\nWe do not operate on-chain fund pools, financial intermediary services, asset trading or third-party fund custody business."
        },
        {
          title: "2. Restricted Regions",
          content: "Access and usage are strictly prohibited for users from:\n\nMainland China, Hong Kong, Macau, Taiwan, United States, all European Union member states, United Kingdom, Canada, Australia, New Zealand, Singapore, Japan, South Korea, and all regions under international sanctions.\n\nAny unauthorized usage shall be at the user's full legal risk.\n\nThe platform will employ technical measures to detect and restrict access from prohibited regions."
        },
        {
          title: "3. Voluntary Donation Policy",
          content: "This platform has no mandatory fees, memberships or paid functions.\n\nSmall automatic allocation funds are defined as voluntary user goodwill donations for server, domain and technical maintenance only.\n\nThey are NOT transaction fees, service charges or commercial revenue, and do not unlock or restrict any platform functions.\n\nDonations are optional and non-refundable."
        },
        {
          title: "4. Prohibited Behaviors",
          content: "Strictly prohibited:\n• Money laundering, fund cleaning, illegal capital circulation\n• Fraud, gray/black industry fund relay\n• Evading foreign exchange control, tax declaration and financial regulation\n• Using bots, crawlers or automated scripts to abuse platform tools\n• Providing paid third-party fund transfer or agency services\n• Promoting or sharing this platform to restricted regions"
        },
        {
          title: "5. Liability Disclaimer",
          content: "The platform does not custody user assets or private keys. All operations are performed by users independently at their own on-chain and legal risk.\n\nWe are not liable for:\n• Loss of funds due to user error, network failures or smart contract bugs\n• Third-party service failures (RPC nodes, cross-chain bridges, etc.)\n• Transaction failures, gas fee depletion or blockchain issues\n• Data accuracy (prices, balances, etc.)\n• Any civil, administrative or criminal liability arising from user violations\n\nThe platform reserves the right to suspend service, block IPs and restrict access at any time.\n\nThe operator shall not be held responsible for any illegal or improper use by users."
        },
        {
          title: "6. Age Requirement",
          content: "You must be at least 18 years old to use this service. By using the service, you represent and warrant that you meet this age requirement."
        },
        {
          title: "7. Intellectual Property",
          content: "All content, features, and functionality of the service are owned by CYGJ Crypto Tools and are protected by international copyright, trademark, and other intellectual property laws."
        },
        {
          title: "8. Service Modifications",
          content: "We reserve the right to modify, suspend, or discontinue the service at any time without prior notice. Continued use of the service after changes constitutes acceptance of the modified terms."
        }
      ]
    },
    zh: {
      title: "服务条款 · 地域限制 · 行为禁令",
      backHome: "返回首页",
      lastUpdated: "最后更新：2024年1月",
      sections: [
        {
          title: "1. 平台定位",
          content: "本站为个人非营利Web3技术学习交流站点，仅提供链外技术路由、网络隐私防护、多链工具、链上查询等纯技术应用；无链上资金池合约、不开展金融中介、不做代转代收、不经营加密资产交易业务，所有工具仅供技术学习与研究参考。"
        },
        {
          title: "2. 禁止访问与使用地区",
          content: "严格禁止以下国家/地区用户访问、注册、使用本站任何功能：\n\n中国大陆、中国港澳台、美国、欧盟全部成员国、英国、加拿大、澳大利亚、新西兰、新加坡、日本、韩国，以及联合国、国际金融机构所有受制裁国家及地区。\n\n违规访问及使用者，自行承担全部法律风险与责任。\n\n平台将采用技术手段检测并限制受限地区访问。"
        },
        {
          title: "3. 自愿捐赠说明",
          content: "本站无任何强制收费、VIP会员及付费服务；系统自动划转的小额款项定义为用户自愿善意捐赠，仅用于服务器、域名、技术维护成本，不属于交易手续费、服务费、经营收费，不绑定任何功能权限。\n\n捐赠为可选项，一经捐赠不可退还。"
        },
        {
          title: "4. 严格禁止行为",
          content: "严格禁止：\n• 用于洗钱、资金洗白、对冲拆分、非法资金周转\n• 用于诈骗、灰产黑产、盘口资金中转\n• 用于逃避外汇管制、税务申报、金融监管\n• 爬虫、机器人、批量接口恶意调用本站工具\n• 基于本站工具开展有偿代转、代收代付商业服务\n• 向中国大陆及受限地区引流、推广、分享本站服务"
        },
        {
          title: "5. 责任免责",
          content: "平台不触碰、不托管、不保管用户资产与私钥，所有操作由用户自主操作、自担链上风险。\n\n我们不对以下情况负责：\n• 因用户错误、网络故障或智能合约漏洞导致的资金损失\n• 第三方服务故障（RPC节点、跨链桥等）\n• 交易失败、Gas费耗尽或区块链问题\n• 数据准确性（价格、余额显示等）\n• 任何用户违规使用造成的民事、行政、刑事责任\n\n平台保留随时关停服务、封禁IP、限制访问的权利。\n\n任何用户违规使用造成的法律责任，均由使用者本人承担，与平台运营方无任何关联。"
        },
        {
          title: "6. 年龄要求",
          content: "您必须年满 18 周岁才能使用本服务。使用本服务即表示您声明并保证您符合此年龄要求。"
        },
        {
          title: "7. 知识产权",
          content: "服务的所有内容、功能和特性均归 CYGJ 加密工具集所有，并受国际版权、商标和其他知识产权法律保护。"
        },
        {
          title: "8. 服务修改",
          content: "我们保留随时修改、暂停或终止服务的权利，恕不另行通知。修改后继续使用服务即表示接受修改后的条款。"
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

          <div className="mt-12 p-6 bg-red-50 border-l-4 border-red-500 rounded">
            <p className="text-sm text-red-800 font-medium">
              {lang === "en" 
                ? "⚠️ IMPORTANT: By using our service, you acknowledge that you have read and agreed to these Terms of Service, including geographic restrictions and prohibited conduct."
                : "⚠️ 重要提示：使用我们的服务即表示您已阅读并同意这些服务条款，包括地域限制和行为禁令。"
              }
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
