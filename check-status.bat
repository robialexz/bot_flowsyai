@echo off
title FlowsyAI Bot - Status Check
color 0B

echo.
echo ========================================
echo     FlowsyAI Bot - Status Check
echo ========================================
echo.

cd /d "C:\Users\flowsyai\Desktop\Folder"

echo Verific statusul FlowsyAI Bot...
echo.

REM Cauta procese Python
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find "python.exe" >nul
if not errorlevel 1 (
    echo ✅ STATUS: BOT ACTIV
    echo.
    echo 🤖 FlowsyAI Bot RULEAZA si serveste comunitatea!
    echo 💰 Promoveaza FlowsyAI Coin in conversatii private
    echo 👥 Raspunde la mentiuni in grupuri (doar in engleza)
    echo 🌍 Detecteaza limba in conversatii private
    echo.
    echo Procese Python active:
    tasklist /FI "IMAGENAME eq python.exe" /FO TABLE | find "python.exe"
) else (
    echo ❌ STATUS: BOT OPRIT
    echo.
    echo 🛑 FlowsyAI Bot nu ruleaza momentan.
    echo.
    echo Pentru a porni bot-ul: dublu-click pe start-bot.bat
)

echo.
echo ========================================
echo COMENZI RAPIDE:
echo   start-bot.bat  - Porneste bot-ul
echo   stop-bot.bat   - Opreste bot-ul
echo   check-status.bat - Verifica status
echo ========================================
echo.
echo Fereastra se va inchide in 10 secunde...
timeout /t 10 /nobreak >nul
