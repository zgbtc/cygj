#!/bin/bash

echo "======================================"
echo "隐私批量转账工具 - Stealth Transfer"
echo "======================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

# 检查依赖
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

echo "激活虚拟环境..."
source .venv/bin/activate

echo "安装依赖..."
pip install -q -r requirements.txt

echo ""
echo "选择运行模式:"
echo "1. Web 界面 (推荐)"
echo "2. 命令行工具"
echo "3. 查看示例代码"
echo ""
read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo ""
        echo "启动 Web 服务..."
        echo "访问: http://localhost:5000"
        python app.py
        ;;
    2)
        echo ""
        python cli.py
        ;;
    3)
        echo ""
        python example.py
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
