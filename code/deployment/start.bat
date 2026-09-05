@echo off
chcp 65001 >nul
echo ================================
echo   AI推理优化学习项目
echo ================================
echo.

REM 检查是否在正确的conda环境中
if "%CONDA_DEFAULT_ENV%"=="" (
    echo ❌ 请先激活conda环境: conda activate work
    pause
    exit /b 1
)

echo 🚀 启动稳定版聊天应用...
echo 📱 访问地址: http://127.0.0.1:7869
echo.
echo 💡 提示:
echo   - 第一次对话会加载模型，请等待1-2分钟
echo   - 支持多轮对话
echo   - 按 Ctrl+C 停止服务
echo.

REM 启动应用
python apps\stable_chat.py

pause