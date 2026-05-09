import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CYGJ Crypto Tools - Web3 Toolbox | Stealth Transfer · HD Wallet · Batch Tools",
  description: "Professional Web3 toolbox for crypto hunters. Stealth transfer router, HD wallet generator, batch transfer & more. 68+ chains supported. Your essential toolkit for DeFi, privacy & on-chain operations.",
  keywords: [
    // Brand
    "CYGJ", "CYGJ crypto", "cygj tools", "web3 toolbox", "crypto toolbox",
    // Batch tools (high traffic, low competition)
    "batch wallet generator", "batch wallet generate", "bulk wallet generator",
    "batch address check", "batch check balance", "batch transfer crypto",
    "token multisender", "bulk token transfer", "crypto batch tool",
    // Privacy / stealth (avoid sensitive terms)
    "stealth transfer", "privacy transfer", "anonymous transfer crypto",
    "cross-chain privacy", "on-chain privacy protection", "crypto privacy tool",
    "untraceable transfer", "web3 identity protection", "IP protection crypto",
    // DeFi tools
    "DeFi tools", "BSC tools", "ETH tools", "web3 tools", "on-chain tools",
    "HD wallet generator", "BIP44 wallet", "gas tracker", "token analyzer",
    "NFT batch mint", "airdrop tool ethereum", "cross-chain transfer",
    // Chinese keywords
    "加密工具箱", "Web3工具箱", "隐私转账", "隐匿转账", "链上隐私保护",
    "HD钱包生成器", "批量转账", "批量钱包生成", "批量地址查询",
    "链上工具", "DeFi工具", "BSC工具", "ETH工具", "跨链转账",
    "批量发送Token", "多对多批量转账", "加密货币工具", "Web3淘金工具"
  ],
  authors: [{ name: "CYGJ Crypto Tools", url: "https://tool.cygj.us" }],
  creator: "CYGJ Crypto Tools",
  metadataBase: new URL("https://tool.cygj.us"),
  alternates: {
    canonical: "https://tool.cygj.us",
  },
  openGraph: {
    type: "website",
    url: "https://tool.cygj.us",
    title: "CYGJ Crypto Tools - Web3 Toolbox | Stealth Transfer · HD Wallet · DeFi",
    description: "Professional Web3 toolbox for crypto hunters. Stealth transfer, HD wallet, batch transfer & more. 68+ chains supported.",
    siteName: "CYGJ Crypto Tools",
    images: [
      {
        url: "/logo.png",
        width: 512,
        height: 512,
        alt: "CYGJ Crypto Tools",
      },
    ],
  },
  twitter: {
    card: "summary",
    title: "CYGJ Crypto Tools - Web3 Toolbox",
    description: "Professional Web3 toolbox for crypto hunters. 68+ chains supported.",
    images: ["/logo.png"],
  },
  icons: {
    icon: "/logo.png",
    shortcut: "/logo.png",
    apple: "/logo.png",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
