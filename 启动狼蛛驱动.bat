@echo off
title 狼蛛键盘本地离线控制面板
echo ===================================================
echo     狼蛛键盘全系列 100%% 本地离线驱动控制面板
echo ===================================================
echo.
echo [1/2] 正在检测 Python 运行环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [错误] 未检测到 Python 运行环境！
    echo 请先安装 Python 3 并将其添加到系统环境变量 PATH 中。
    echo.
    pause
    exit /b
)

echo [2/2] 正在启动本地离线服务器 (http://localhost:8080)...
echo.
echo ===================================================
echo 使用说明：
echo 1. 稍后将在你的默认浏览器中自动打开控制面板页面。
echo 2. 请使用 Chrome、Edge、Brave 等现代 Chromium 内核浏览器。
echo 3. 插入键盘后，在网页中点击【连接设备】，选中你的键盘即可。
echo 4. 关闭此命令行黑窗口即可退出离线驱动服务。
echo ===================================================
echo.
python server.py
pause
