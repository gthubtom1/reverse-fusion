@echo off
chcp 65001 >nul
title 标签收纳盒
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 goto try_py
python "%~dp0launch.py"
goto finished
:try_py
where py >nul 2>nul
if errorlevel 1 goto missing
py -3 "%~dp0launch.py"
goto finished
:missing
echo 未找到 Python 3。此电脑需要先安装 Python 3 才能启动本地版本。
echo 如已安装，请确保启动命令可用，或请协助配置本地启动器。
pause
exit /b 1
:finished
if errorlevel 1 pause
