@echo off
chcp 65001 >nul
title E2seq - Quick Start

REM ============================================================
REM E2seq 快速启动脚本 (Quick Run)
REM 直接使用虚拟环境启动，跳过依赖检查和配置向导
REM ============================================================

cd /d "%~dp0"

REM 设置 HuggingFace 镜像
set HF_ENDPOINT=https://hf-mirror.com

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境 venv\Scripts\python.exe
    echo 请先运行 start.py 创建虚拟环境
    pause
    exit /b 1
)

REM 默认端口
set PORT=8000

REM 启动服务器 (在新窗口中运行)
echo 启动 E2seq 服务，端口: %PORT%
echo 启动后自动打开浏览器...
start "E2seq Server" cmd /k "venv\Scripts\python.exe -m uvicorn e2sc.api.server:app --host 127.0.0.1 --port %PORT%"

REM 等待服务器启动
timeout /t 3 /nobreak >nul

REM 打开浏览器
start http://127.0.0.1:%PORT%

exit
