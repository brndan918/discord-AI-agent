@echo off
chcp 65001 > nul

cd /d "%~dp0"
title install requirements

if exist .ok-requirements (
    echo 正在安裝 requirements.txt
    ping -n 2 127.0.0.1 > nul
    echo 依賴套件已安裝，跳過安裝步驟。
    ) else (
    echo 正在安裝 requirements.txt
    pip install -r requirements.txt
    echo 安裝完成！

    type nul > .ok-requirements
    attrib +h .ok-requirements
)

if "%~1"=="auto-restart" (
    echo 正在重新啟動...
    ping -n 3 127.0.0.1 > nul
    start "" "run.bat"
    exit
)

pause
exit