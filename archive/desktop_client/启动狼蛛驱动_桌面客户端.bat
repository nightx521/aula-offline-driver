@echo off
title 狼蛛键盘桌面独立客户端
echo ===================================================
echo     狼蛛键盘全系列 桌面独立客户端
echo ===================================================
echo.

:: 优先检测原生独立桌面窗口模式 (基于内置 Edge/Chrome --app，零拦截零崩溃)
if exist "server.py" goto LAUNCH_NATIVE_APP

:TRY_ELECTRON
if exist node_modules\electron goto START_ELECTRON

echo [提示] 正在安装桌面端依赖...
call npm.cmd install
if %errorlevel% neq 0 goto LAUNCH_NATIVE_APP

:START_ELECTRON
echo [提示] 正在启动 Electron 桌面客户端...
call npm.cmd start
if %errorlevel% equ 0 goto END

:LAUNCH_NATIVE_APP
echo.
echo [提示] 正在以原生独立桌面应用模式启动 (免报毒、零崩溃、完整 WebHID 支持)...
python server.py --app
goto END

:END
