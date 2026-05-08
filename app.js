// 工具数据
const tools = [
    {
        id: 1,
        name: "Stealth Transfer",
        category: "privacy",
        description: "多跳混币器，通过交叉转账隐藏资金路径，保护隐私",
        icon: "🎭",
        features: [
            "10-1000 跳可选",
            "自动路径生成",
            "支持 BSC/ETH",
            "服务费 1-30%"
        ],
        chains: ["BSC", "ETH"],
        url: "/stealth-transfer",
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
        url: "/hd-wallet",
        status: "active",
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
        url: "/batch-transfer",
        status: "active",
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
        url: "/token-analyzer",
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
        url: "/gas-tracker",
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
        url: "/nft-mint",
        status: "coming-soon",
        rating: 0,
        users: "Soon"
    }
];

// 渲染工具卡片
function renderTools(toolsToRender = tools) {
    const grid = document.getElementById('toolsGrid');
    grid.innerHTML = '';
    
    toolsToRender.forEach(tool => {
        const card = document.createElement('div');
        card.className = 'tool-card bg-white rounded-xl shadow-lg p-6 border-2 border-gray-100';
        card.dataset.category = tool.category;
        
        const statusBadge = tool.status === 'active' 
            ? '<span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">可用</span>'
            : '<span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">即将推出</span>';
        
        const ratingStars = tool.status === 'active'
            ? `<div class="flex items-center space-x-1">
                <span class="text-yellow-400">★</span>
                <span class="text-sm font-semibold">${tool.rating}</span>
                <span class="text-gray-400 text-sm ml-2">${tool.users} 用户</span>
               </div>`
            : '<div class="text-gray-400 text-sm">即将推出</div>';
        
        card.innerHTML = `
            <div class="flex items-start justify-between mb-4">
                <div class="text-4xl">${tool.icon}</div>
                ${statusBadge}
            </div>
            
            <h3 class="text-xl font-bold mb-2">${tool.name}</h3>
            <p class="text-gray-600 text-sm mb-4">${tool.description}</p>
            
            <div class="mb-4">
                <div class="flex flex-wrap gap-2 mb-3">
                    ${tool.chains.map(chain => 
                        `<span class="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded">${chain}</span>`
                    ).join('')}
                </div>
                
                <ul class="space-y-1">
                    ${tool.features.slice(0, 3).map(feature => 
                        `<li class="text-sm text-gray-600 flex items-center">
                            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                            </svg>
                            ${feature}
                        </li>`
                    ).join('')}
                </ul>
            </div>
            
            ${ratingStars}
            
            <div class="mt-4 pt-4 border-t border-gray-100">
                ${tool.status === 'active' 
                    ? `<a href="${tool.url}" class="block w-full text-center bg-purple-600 text-white py-2 rounded-lg font-semibold hover:bg-purple-700 transition">
                        立即使用
                       </a>`
                    : `<button class="block w-full text-center bg-gray-300 text-gray-600 py-2 rounded-lg font-semibold cursor-not-allowed">
                        即将推出
                       </button>`
                }
            </div>
        `;
        
        grid.appendChild(card);
    });
    
    if (toolsToRender.length === 0) {
        grid.innerHTML = '<div class="col-span-full text-center text-gray-500 py-12">未找到匹配的工具</div>';
    }
}

// 搜索工具
function searchTools() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filtered = tools.filter(tool => 
        tool.name.toLowerCase().includes(searchTerm) ||
        tool.description.toLowerCase().includes(searchTerm) ||
        tool.features.some(f => f.toLowerCase().includes(searchTerm))
    );
    renderTools(filtered);
}

// 按分类筛选
function filterTools(category) {
    const filtered = tools.filter(tool => tool.category === category);
    renderTools(filtered);
    
    // 滚动到工具区域
    document.getElementById('tools').scrollIntoView({ behavior: 'smooth' });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    renderTools();
});
