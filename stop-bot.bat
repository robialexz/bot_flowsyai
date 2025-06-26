@echo off
title FlowsyAI Bot - Quick Stop
color 0C

echo.
echo ========================================
echo      FlowsyAI Bot - Quick Stop
echo ========================================
echo.

cd /d "C:\Users\flowsyai\Desktop\Folder"

echo Opresc FlowsyAI Bot...

REM Opresc toate procesele Python
taskkill /F /IM python.exe 2>nul
taskkill /F /IM py.exe 2>nul

REM Curatenie fisiere PID
if exist "bot_pid.txt" del "bot_pid.txt" 2>nul

echo.
echo ✅ Bot-ul FlowsyAI a fost oprit!
echo.
echo 🛑 Status: OPRIT
echo 📁 Locatie: %CD%
echo.
echo Pentru a porni din nou: dublu-click pe start-bot.bat
echo.
echo Fereastra se va inchide in 3 secunde...
timeout /t 3 /nobreak >nul
