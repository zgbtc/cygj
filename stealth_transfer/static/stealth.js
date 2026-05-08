const API_BASE = 'http://localhost:5000/api';

let currentPlan = null;

// 查询余额
async function checkBalance() {
    const privateKey = document.getElementById('fromPrivateKey').value.trim();
    const chain = document.getElementById('chainSelect').value;
    
    if (!privateKey) {
        showInfo('balanceInfo', '请输入私钥', 'error');
        return;
    }
    
    try {
        // 这里简化处理，实际应该从私钥获取地址
        showInfo('balanceInfo', '正在查询余额...', 'info');
        
        // 模拟查询（实际需要实现）
        setTimeout(() => {
            showInfo('balanceInfo', '请确保钱包有足够余额', 'success');
        }, 500);
    } catch (error) {
        showInfo('balanceInfo', `查询失败: ${error.message}`, 'error');
    }
}

// 预览转账计划
async function previewPlan() {
    const chain = document.getElementById('chainSelect').value;
    const totalAmount = parseFloat(document.getElementById('totalAmount').value);
    const numAddresses = parseInt(document.getElementById('numAddresses').value);
    const distribution = document.getElementById('distribution').value;
    const mnemonic = document.getElementById('mnemonic').value.trim() || null;
    const gasLevel = document.querySelector('input[name="gasLevel"]:checked').value;
    
    if (!totalAmount || totalAmount <= 0) {
        alert('请输入有效的总金额');
        return;
    }
    
    if (!numAddresses || numAddresses < 10 || numAddresses > 10000) {
        alert('地址数量必须在 10-10000 之间');
        return;
    }
    
    try {
        // 创建计划
        const planResponse = await fetch(`${API_BASE}/stealth/plan`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                chain: chain,
                total_amount: totalAmount,
                num_addresses: numAddresses,
                mnemonic: mnemonic,
                distribution: distribution
            })
        });
        
        const planData = await planResponse.json();
        
        if (!planData.success) {
            alert(`创建计划失败: ${planData.error}`);
            return;
        }
        
        currentPlan = planData.plan;
        
        // 估算费用
        const estimateResponse = await fetch(`${API_BASE}/stealth/estimate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                chain: chain,
                num_addresses: numAddresses,
                gas_level: gasLevel
            })
        });
        
        const estimateData = await estimateResponse.json();
        
        // 显示预览
        const planDiv = document.getElementById('planPreview');
        const contentDiv = document.getElementById('planContent');
        
        let html = `
            <div class="stats">
                <span>总金额: <strong>${currentPlan.total_amount}</strong></span>
                <span>地址数量: <strong>${currentPlan.num_addresses}</strong></span>
                <span>分配方式: <strong>${currentPlan.distribution === 'random' ? '随机' : '平均'}</strong></span>
            </div>
            <br>
            <div class="info-box success" style="display: block;">
                <strong>助记词:</strong><br>
                <span style="font-family: monospace;">${currentPlan.mnemonic}</span>
            </div>
            <br>
            <p><strong>前 10 个接收地址:</strong></p>
        `;
        
        currentPlan.recipients.slice(0, 10).forEach(r => {
            html += `<div style="padding: 5px; margin: 3px 0; background: #f8f9fa; border-radius: 4px; font-size: 13px;">
                [${r.index}] ${r.address}: ${r.amount}
            </div>`;
        });
        
        if (currentPlan.num_addresses > 10) {
            html += `<p style="color: #666; margin-top: 10px;">... 还有 ${currentPlan.num_addresses - 10} 个地址</p>`;
        }
        
        if (estimateData.success) {
            html += `<br><div class="stats">
                <span>Gas 费用: <strong>${estimateData.estimate.total_cost} ${estimateData.estimate.token}</strong></span>
                <span>总计需要: <strong>${(currentPlan.total_amount + estimateData.estimate.total_cost).toFixed(6)} ${estimateData.estimate.token}</strong></span>
            </div>`;
        }
        
        contentDiv.innerHTML = html;
        planDiv.style.display = 'block';
        planDiv.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert(`预览失败: ${error.message}`);
    }
}

// 执行隐私转账
async function executeStealthTransfer() {
    const privateKey = document.getElementById('fromPrivateKey').value.trim();
    const chain = document.getElementById('chainSelect').value;
    const totalAmount = parseFloat(document.getElementById('totalAmount').value);
    const numAddresses = parseInt(document.getElementById('numAddresses').value);
    const distribution = document.getElementById('distribution').value;
    const mnemonic = document.getElementById('mnemonic').value.trim() || null;
    const gasLevel = document.querySelector('input[name="gasLevel"]:checked').value;
    
    if (!privateKey) {
        alert('请输入源地址私钥');
        return;
    }
    
    if (!totalAmount || totalAmount <= 0) {
        alert('请输入有效的总金额');
        return;
    }
    
    if (!numAddresses || numAddresses < 10 || numAddresses > 10000) {
        alert('地址数量必须在 10-10000 之间');
        return;
    }
    
    if (!confirm(`确认执行隐私转账？\n\n总金额: ${totalAmount}\n地址数量: ${numAddresses}\n\n这将消耗 Gas 费用，请确认。`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/stealth/execute`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                chain: chain,
                from_private_key: privateKey,
                total_amount: totalAmount,
                num_addresses: numAddresses,
                mnemonic: mnemonic,
                distribution: distribution,
                gas_level: gasLevel
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            alert(`转账失败: ${data.error}`);
        }
    } catch (error) {
        alert(`请求失败: ${error.message}`);
    }
}

// 显示结果
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const mnemonicText = document.getElementById('mnemonicText');
    const resultsListDiv = document.getElementById('resultsList');
    
    // 显示助记词
    mnemonicText.textContent = data.mnemonic;
    
    let html = `<div class="stats">
        <span>总计: <strong>${data.total}</strong></span>
        <span>成功: <strong style="color: #27ae60">${data.success_count}</strong></span>
        <span>失败: <strong style="color: #e74c3c">${data.failed_count}</strong></span>
    </div><br>`;
    
    html += `<p><strong>转账记录（前 20 条）:</strong></p>`;
    
    data.results.slice(0, 20).forEach(result => {
        const status = result.status === 'pending' ? 'success' : 'failed';
        html += `<div class="result-item ${status}">
            <strong>[${result.index}]</strong> ${result.to}<br>
            金额: ${result.amount}`;
        
        if (result.status === 'pending') {
            html += `<br>交易: <a href="${result.explorer_url}" target="_blank">${result.tx_hash.substring(0, 20)}...</a>`;
        } else {
            html += `<br>错误: ${result.error}`;
        }
        
        html += `</div>`;
    });
    
    if (data.total > 20) {
        html += `<p style="color: #666; margin-top: 10px;">... 还有 ${data.total - 20} 条记录</p>`;
    }
    
    resultsListDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// 复制助记词
function copyMnemonic() {
    const mnemonicText = document.getElementById('mnemonicText').textContent;
    navigator.clipboard.writeText(mnemonicText).then(() => {
        alert('助记词已复制到剪贴板！\n\n请妥善保管，不要泄露给任何人！');
    }).catch(err => {
        alert('复制失败，请手动复制');
    });
}

// 显示信息框
function showInfo(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.innerHTML = message;
    element.className = `info-box show ${type}`;
}
