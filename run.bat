:: 設定 utf-8 編碼
@echo off
chcp 65001 > nul

cd /d "%~dp0"
title discord bot: AI-Agent

set "MISSING="

where python 2>nul | findstr /i /v "WindowsApps" >nul
if %errorlevel% neq 0 (
    echo 找不到 python
    set "MISSING=1"
)

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo 找不到git
    set "MISSING=1"
)

if defined MISSING exit /b 1

set "VERSION_URL=https://raw.githubusercontent.com/brndan918/discord-AI-agent/refs/heads/main/version.json"

curl -L -s "%VERSION_URL%" -o "%TEMP%\discord_ai_agent_version.json"

if not exist "%TEMP%\discord_ai_agent_version.json" (
    goto :RUN
)

for /f "delims=" %%i in ('python -c "import json; print(json.load(open(r'%TEMP%\discord_ai_agent_version.json', encoding='utf-8')).get('version',''))" 2^>nul') do set "REMOTE_VERSION=%%i"

if not exist "version.json" (
    goto :RUN
)

for /f "delims=" %%i in ('python -c "import json; print(json.load(open('version.json', encoding='utf-8')).get('version',''))" 2^>nul') do set "LOCAL_VERSION=%%i"

if "%REMOTE_VERSION%"=="" (
    goto :RUN
)

if "%LOCAL_VERSION%"=="" (
    goto :RUN
)

if "%LOCAL_VERSION%"=="%REMOTE_VERSION%" (
    goto :RUN
)

echo updating...
git fetch --all > nul
git reset --hard origin/main > nul

del install_ai-agent.txt

start "" "%~f0"

exit /b

:RUN
python main.py
pause
