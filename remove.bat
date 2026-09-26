@echo off
chcp 65001 > nul

set "TARGET_DIR=%~dp0"
set "TARGET_DIR=%TARGET_DIR:~0,-1%"

cd /d "%TARGET_DIR%\.."

choice /c YN /m "確定要刪除專案資料夾嗎？"
if errorlevel 2 (
    echo 已取消刪除動作。
    pause
    exit /b
)

start /b cmd /c "title 正在刪除專案 & timeout /t 1 /nobreak > nul & rd /s /q "%TARGET_DIR%""

exit
