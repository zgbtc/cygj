@echo off
chcp 65001 >nul
echo ======================================
echo 隐私批量转账工具 - Stealth Transfer
echo ======================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
)

echo 激活虚拟环境...
call .venv\Scripts\activate.bat

echo 安装依赖...
pip install -q -r requirements.txt

echo.
echo 选择运行模式:
echo 1. Web 界面 (推荐)
echo 2. 命令行工具
echo 3. 查看示例代码
echo.
set /p choice="请选择 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 启动 Web 服务...
    echo 访问: http://localhost:5000
    python app.py
) else if "%choice%"=="2" (
    echo.
    python cli.py
) else if "%choice%"=="3" (
    echo.
    python example.py
) else (
    echo 无效选择
    pause
    exit /b 1
)

pause
