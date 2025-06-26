@echo off
title FlowsyAI Bot - Quick Start
color 0A

echo.
echo ========================================
echo      FlowsyAI Bot - Quick Start
echo ========================================
echo.

cd /d "C:\Users\flowsyai\Desktop\Folder"

echo Pornesc FlowsyAI Bot...

REM Opresc instante existente
taskkill /F /IM python.exe 2>nul >nul
if exist "bot_pid.txt" del "bot_pid.txt" 2>nul

REM Verific mediul virtual
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
) else (
    set PYTHON_EXE=py
)

REM Pornesc bot-ul in fundal
start /B %PYTHON_EXE% main.py

echo.
echo ✅ Bot-ul FlowsyAI a fost pornit!
echo.
echo 🤖 Status: ACTIV si FUNCTIONAL
echo 💰 Promoveaza FlowsyAI Coin 24/7
echo 🌍 Suport multilingv inteligent
echo 👥 Raspunde doar la mentiuni in grupuri
echo.
echo Pentru a opri bot-ul: dublu-click pe stop-bot.bat
echo Pentru a verifica status: dublu-click pe check-status.bat
echo.
echo Fereastra se va inchide in 5 secunde...
timeout /t 5 /nobreak >nul
