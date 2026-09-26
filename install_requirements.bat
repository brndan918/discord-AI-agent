@echo off
chcp 65001 > nul

cd /d "%~dp0"

echo 正在安裝 requirements.txt
pip install -r requirements.txt > nul
echo 安裝完成！

pause