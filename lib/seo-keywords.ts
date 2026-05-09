/**
 * SEO Keywords Configuration
 * 
 * 用于 /keywords 页面的关键词密度优化
 * 未来需要优化的关键词都添加到这里
 */

export interface KeywordConfig {
  en: string;
  zh: string;
  targetDensity: number; // 目标密度百分比（如 3.0 表示 3%）
  category: string;
}

/**
 * 高密度关键词（目标 3%+）
 * 这些关键词会在页面中重复出现 15-20 次
 */
export const highDensityKeywords: KeywordConfig[] = [
  {
    en: "cointool",
    zh: "币工具",
    targetDensity: 3.5,
    category: "brand"
  },
  {
    en: "crypto toolbox",
    zh: "加密工具箱",
    targetDensity: 3.2,
    category: "brand"
  },
  {
    en: "web3 toolbox",
    zh: "Web3工具箱",
    targetDensity: 3.0,
    category: "brand"
  },
  {
    en: "crypto tools",
    zh: "加密货币工具",
    targetDensity: 3.0,
    category: "brand"
  }
];

/**
 * 中等密度关键词（目标 2-3%）
 * 这些关键词会在页面中重复出现 10-15 次
 */
export const mediumDensityKeywords: KeywordConfig[] = [
  {
    en: "batch wallet generator",
    zh: "批量钱包生成",
    targetDensity: 2.5,
    category: "tool"
  },
  {
    en: "stealth transfer",
    zh: "隐私转账",
    targetDensity: 2.5,
    category: "tool"
  },
  {
    en: "privacy transfer",
    zh: "隐匿转账",
    targetDensity: 2.3,
    category: "tool"
  },
  {
    en: "batch transfer",
    zh: "批量转账",
    targetDensity: 2.2,
    category: "tool"
  },
  {
    en: "HD wallet generator",
    zh: "HD钱包生成器",
    targetDensity: 2.0,
    category: "tool"
  }
];

/**
 * 低密度关键词（目标 1-2%）
 * 这些关键词会在页面中重复出现 5-10 次
 */
export const lowDensityKeywords: KeywordConfig[] = [
  {
    en: "batch address check",
    zh: "批量地址查询",
    targetDensity: 1.8,
    category: "tool"
  },
  {
    en: "token multisender",
    zh: "批量发送Token",
    targetDensity: 1.5,
    category: "tool"
  },
  {
    en: "cross-chain transfer",
    zh: "跨链转账",
    targetDensity: 1.5,
    category: "tool"
  },
  {
    en: "DeFi tools",
    zh: "DeFi工具",
    targetDensity: 1.5,
    category: "category"
  },
  {
    en: "BSC tools",
    zh: "BSC工具",
    targetDensity: 1.3,
    category: "chain"
  },
  {
    en: "ETH tools",
    zh: "ETH工具",
    targetDensity: 1.3,
    category: "chain"
  },
  {
    en: "on-chain tools",
    zh: "链上工具",
    targetDensity: 1.2,
    category: "category"
  },
  {
    en: "gas tracker",
    zh: "Gas追踪器",
    targetDensity: 1.0,
    category: "tool"
  },
  {
    en: "token analyzer",
    zh: "代币分析器",
    targetDensity: 1.0,
    category: "tool"
  },
  {
    en: "NFT batch mint",
    zh: "NFT批量铸造",
    targetDensity: 1.0,
    category: "tool"
  }
];

/**
 * 长尾关键词
 * 这些关键词会在页面中出现 2-5 次
 */
export const longTailKeywords: string[] = [
  "BIP44 wallet",
  "bulk wallet generator",
  "bulk token transfer",
  "crypto batch tool",
  "anonymous transfer crypto",
  "cross-chain privacy",
  "on-chain privacy protection",
  "untraceable transfer",
  "web3 identity protection",
  "IP protection crypto",
  "airdrop tool ethereum",
  "multi-chain wallet",
  "crypto privacy tool",
  "blockchain tools",
  "web3 淘金工具",
  "多对多批量转账",
  "链上隐私保护",
  "BIP44钱包",
  "批量空投工具",
  "多链钱包生成器"
];

/**
 * 获取所有关键词（用于生成内容）
 */
export function getAllKeywords(): KeywordConfig[] {
  return [
    ...highDensityKeywords,
    ...mediumDensityKeywords,
    ...lowDensityKeywords
  ];
}

/**
 * 根据目标密度计算关键词应该出现的次数
 * @param targetDensity 目标密度（百分比）
 * @param totalWords 页面总字数
 */
export function calculateKeywordCount(targetDensity: number, totalWords: number): number {
  return Math.ceil((targetDensity / 100) * totalWords);
}
