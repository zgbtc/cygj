const API_BASE = 'http://localhost:5000/api';

// 更新地址统计
document.getElementById('recipients').addEventListener('input', function() {
    const text = this.value.trim();
    if (!text) {
        document.getElementById('addressCount').textContent = '0';
        document.getElementById('totalAmount').textContent = '0';
        return;
    }
    
    const lines = text.split('\n').filter(line => line.trim());
    let totalAmount = 0;
    let validCount = 0;
    
    lines.forEach(line => {
        const parts = line.split(',');
        if (parts.length === 2) {
            const amount = parseFloat(parts[1].trim());
            if (!isNaN(amount)) {
                totalAmount += amount;
                validCount++;
            }
        }
    });
    
    document.getElementById('addressCount').textContent = validCount;
    document.getElementById('totalAmount').textContent = totalAmount.toFixed(4);
});

// 查询余额
async function checkBalance() {
    const privateKey = document.getElementById('privateKey').value.trim();
    const chain = document.getElementById('chainSelect').value;
    
    if (!privateKey) {
        showInfo('balanceInfo', '请输入私钥', 'error');
        return;
    }
    
    try {
        // 从私钥获取地址 (简化版，实际应该用 web3)
        const response = await fetch(`${API_BASE}/balance`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                chain: chain,
                address: privateKey // 这里应该转换为地址
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showInfo('balanceInfo', 
                `地址: ${data.address}<br>余额: ${data.balance} ${data.token}`, 
                'success');
        } else {
            showInfo('balanceInfo', `错误: ${data.error}`, 'error');
        }
    } catch (error) {
        showInfo('balanceInfo', `请求失败: ${error.message}`, 'error');
    }
}

// 估算费用
async function estimateCost() {
    const chain = document.getElementById('chainSelect').value;
    const gasLevel = document.querySelector('input[name="gasLevel"]:checked').value;
    const addressCount = parseInt(document.getElementById('addressCount').textContent);
    
    if (addressCount === 0) {
        showInfo('estimateInfo', '请先输入接收地址列表', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/estimate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                chain: chain,
                num_addresses: addressCount,
                gas_level: gasLevel
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const est = data.estimate;
            showInfo('estimateInfo', 
                `Gas 价格: ${est.gas_price_gwei} Gwei<br>` +
                `总 Gas: ${est.total_gas.toLocaleString()}<br>` +
                `预估费用: ${est.total_cost.toFixed(6)} ${est.token}`, 
                'success');
        } else {
            showInfo('estimateInfo', `错误: ${data.error}`, 'error');
        }
    } catch (error) {
        showInfo('estimateInfo', `请求失败: ${error.message}`, 'error');
    }
}

// 执行转账
async function executeTransfer() {
    const privateKey = document.getElementById('privateKey').value.trim();
    const chain = document.getElementById('chainSelect').value;
    const gasLevel = document.querySelector('input[name="gasLevel"]:checked').value;
    const recipientsText = document.getElementById('recipients').value.trim();
    
    if (!privateKey) {
        alert('请输入私钥');
        return;
    }
    
    if (!recipientsText) {
        alert('请输入接收地址列表');
        return;
    }
    
    // 解析接收地址
    const recipients = [];
    const lines = recipientsText.split('\n').filter(line => line.trim());
    
    for (const line of lines) {
        const parts = line.split(',');
        if (parts.length === 2) {
            recipients.push({
                address: parts[0].trim(),
                amount: parseFloat(parts[1].trim())
            });
        }
    }
    
    if (recipients.length < 10) {
        alert('地址数量不足，最少需要 10 个地址');
        return;
    }
    
    if (recipients.length > 10000) {
        alert('地址数量超限，最多支持 10000 个地址');
        return;
    }
    
    if (!confirm(`确认向 ${recipients.length} 个地址发送转账？`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/transfer`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                chain: chain,
                private_key: privateKey,
                recipients: recipients,
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
    const resultsListDiv = document.getElementById('resultsList');
    
    let html = `<div class="stats">
        <span>总计: <strong>${data.summary.total}</strong></span>
        <span>成功: <strong style="color: #27ae60">${data.summary.success}</strong></span>
        <span>失败: <strong style="color: #e74c3c">${data.summary.failed}</strong></span>
    </div><br>`;
    
    data.results.forEach(result => {
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
    
    resultsListDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// 显示信息框
function showInfo(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.innerHTML = message;
    element.className = `info-box show ${type}`;
}
