"""Flask API 服务"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transfer_engine import TransferEngine
from stealth_engine import StealthTransferEngine
from mixer_engine import MixerEngine
from hd_wallet import HDWallet
from config import CHAINS, MIN_ADDRESSES, MAX_ADDRESSES
import logging
import os

app = Flask(__name__, static_folder='static')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """主页"""
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """静态文件"""
    return send_from_directory('static', path)


@app.route('/api/chains', methods=['GET'])
def get_chains():
    """获取支持的链列表"""
    chains_info = []
    for chain_id, config in CHAINS.items():
        chains_info.append({
            'id': chain_id,
            'name': config['name'],
            'chain_id': config['chain_id'],
            'native_token': config['native_token'],
            'gas_levels': list(config['gas_price_gwei'].keys())
        })
    return jsonify({
        'success': True,
        'chains': chains_info,
        'limits': {
            'min_addresses': MIN_ADDRESSES,
            'max_addresses': MAX_ADDRESSES
        }
    })


@app.route('/api/estimate', methods=['POST'])
def estimate_cost():
    """估算转账费用"""
    try:
        data = request.json
        chain = data.get('chain', 'bsc')
        num_addresses = data.get('num_addresses', 10)
        gas_level = data.get('gas_level', 'standard')
        
        engine = TransferEngine(chain)
        estimate = engine.estimate_gas_cost(num_addresses, gas_level)
        
        return jsonify({
            'success': True,
            'estimate': estimate
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/balance', methods=['POST'])
def check_balance():
    """查询地址余额"""
    try:
        data = request.json
        chain = data.get('chain', 'bsc')
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'error': '缺少地址参数'}), 400
        
        engine = TransferEngine(chain)
        balance = engine.get_balance(address)
        
        return jsonify({
            'success': True,
            'address': address,
            'balance': balance,
            'token': engine.chain_config['native_token']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/transfer', methods=['POST'])
def batch_transfer():
    """批量转账"""
    try:
        data = request.json
        chain = data.get('chain', 'bsc')
        private_key = data.get('private_key')
        recipients = data.get('recipients', [])
        gas_level = data.get('gas_level', 'standard')
        
        if not private_key:
            return jsonify({'success': False, 'error': '缺少私钥'}), 400
        
        if not recipients:
            return jsonify({'success': False, 'error': '缺少接收地址列表'}), 400
        
        engine = TransferEngine(chain)
        results = engine.send_batch_transfers(private_key, recipients, gas_level)
        
        success_count = sum(1 for r in results if r['status'] == 'pending')
        failed_count = len(results) - success_count
        
        return jsonify({
            'success': True,
            'summary': {
                'total': len(results),
                'success': success_count,
                'failed': failed_count
            },
            'results': results
        })
    except Exception as e:
        logger.error(f"批量转账失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/validate', methods=['POST'])
def validate_addresses():
    """验证地址列表"""
    try:
        data = request.json
        chain = data.get('chain', 'bsc')
        addresses = data.get('addresses', [])
        
        engine = TransferEngine(chain)
        valid, message = engine.validate_addresses(addresses)
        
        return jsonify({
            'success': True,
            'valid': valid,
            'message': message,
            'count': len(addresses)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/stealth/generate', methods=['POST'])
def generate_stealth_addresses():
    """生成隐私地址"""
    try:
        data = request.json
        count = data.get('count', 10)
        mnemonic = data.get('mnemonic')  # 可选
        
        if count < MIN_ADDRESSES or count > MAX_ADDRESSES:
            return jsonify({
                'success': False,
                'error': f'地址数量必须在 {MIN_ADDRESSES}-{MAX_ADDRESSES} 之间'
            }), 400
        
        wallet = HDWallet(mnemonic)
        addresses = wallet.generate_addresses(count)
        
        return jsonify({
            'success': True,
            'mnemonic': wallet.mnemonic,
            'count': len(addresses),
            'addresses': [
                {
                    'index': addr['index'],
                    'address': addr['address'],
                    'path': addr['path']
                }
                for addr in addresses
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/stealth/plan', methods=['POST'])
def create_stealth_plan():
    """创建隐私转账计划"""
    try:
        data = request.json
        chain = data.get('chain', 'bsc')
        total_amount = data.get('total_amount')
        num_addresses = data.get('num_addresses', 10)
        mnemonic = data.get('mnemonic')
        distribution = data.get('distribution', 'random')
        
        if not total_amount:
            return jsonify({'success': False, 'error': '缺少总金额'}), 400
        
        engine = StealthTransferEngine(chain)
        plan = engine.create_stealth_transfer_plan(
            total_amount=total_amount,
            num_addresses=num_addresses,
            mnemonic=mnemonic,
            distribution=distribution
        )
        
        # 不返回私钥，只返回地址和金额
        safe_plan = {
            'mnemonic': plan['mnemonic'],
            'total_amount': plan['total_amount'],
            'num_addresses': plan['num_addresses'],
            'distribution': plan['distribution'],
            'chain': plan['chain'],
            'recipients': [
                {
                    'index': r['index'],
                    'address': r['address'],
                    'amount': r['amount']
                }
                for r in plan['recipients']
            ]
        }
        
        return jsonify({
            'success': True,
            'plan': safe_plan
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/stealth/execute', methods=['POST'])
def execute_stealth_transfer():
    """执行隐私转账"""
    try:
        data = request.json
        chain = data.get('chain', 'bsc')
        from_private_key = data.get('from_private_key')
        total_amount = data.get('total_amount')
        num_addresses = data.get('num_addresses', 10)
        mnemonic = data.get('mnemonic')
        distribution = data.get('distribution', 'random')
        gas_level = data.get('gas_level', 'standard')
        
        if not from_private_key:
            return jsonify({'success': False, 'error': '缺少源地址私钥'}), 400
        
        if not total_amount:
            return jsonify({'success': False, 'error': '缺少总金额'}), 400
        
        engine = StealthTransferEngine(chain)
        
        # 创建计划
        plan = engine.create_stealth_transfer_plan(
            total_amount=total_amount,
            num_addresses=num_addresses,
            mnemonic=mnemonic,
            distribution=distribution
        )
        
        # 执行转账
        result = engine.execute_stealth_transfer(
            from_private_key=from_private_key,
            plan=plan,
            gas_level=gas_level
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"隐私转账失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/stealth/estimate', methods=['POST'])
def estimate_stealth_cost():
    """估算隐私转账费用"""
    try:
        data = request.json
        chain = data.get('chain', 'bsc')
        num_addresses = data.get('num_addresses', 10)
        gas_level = data.get('gas_level', 'standard')
        
        engine = StealthTransferEngine(chain)
        estimate = engine.estimate_stealth_transfer_cost(num_addresses, gas_level)
        
        return jsonify({
            'success': True,
            'estimate': estimate
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/mixer/execute', methods=['POST'])
def execute_mixer():
    """执行混币"""
    try:
        data = request.json
        chain = data.get('chain', 'bsc_testnet')
        from_private_key = data.get('from_private_key')
        to_address = data.get('to_address')
        total_amount = data.get('total_amount')
        num_hops = data.get('num_hops', 100)
        mnemonic = data.get('mnemonic')
        gas_level = data.get('gas_level', 'standard')
        
        if not from_private_key:
            return jsonify({'success': False, 'error': '缺少源地址私钥'}), 400
        
        if not to_address:
            return jsonify({'success': False, 'error': '缺少目标地址'}), 400
        
        if not total_amount:
            return jsonify({'success': False, 'error': '缺少总金额'}), 400
        
        # 创建混币器引擎
        mixer = MixerEngine(chain)
        
        # 创建混币计划
        plan = mixer.create_mixing_plan(
            from_private_key=from_private_key,
            to_address=to_address,
            total_amount=total_amount,
            num_hops=num_hops,
            mnemonic=mnemonic
        )
        
        # 执行混币
        result = mixer.execute_mixing(plan, gas_level=gas_level)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"混币执行失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
