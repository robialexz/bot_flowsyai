@echo off
setlocal enabledelayedexpansion
title FlowsyAI Bot Stopper
color 0C

echo.
echo ========================================
echo       FlowsyAI Bot Stopper
echo ========================================
echo.

cd /d "C:\Users\flowsyai\Desktop\Folder"

echo [1/4] Opresc FlowsyAI Bot...

echo [2/4] Verific Process ID din fisier...
if exist "bot_pid.txt" (
    set /p BOT_PID=<bot_pid.txt
    echo Process ID gasit: !BOT_PID!
    
    tasklist /FI "PID eq !BOT_PID!" 2>nul | find "!BOT_PID!" >nul
    if not errorlevel 1 (
        echo Opresc procesul cu PID: !BOT_PID!
        taskkill /F /PID !BOT_PID! 2>nul
        if not errorlevel 1 (
            echo Bot-ul a fost oprit cu succes!
        ) else (
            echo ATENTIE: Nu am putut opri procesul cu PID !BOT_PID!
        )
    ) else (
        echo Procesul cu PID !BOT_PID! nu mai ruleaza.
    )
    
    echo Sterg fisierul bot_pid.txt...
    del "bot_pid.txt" 2>nul
) else (
    echo Fisierul bot_pid.txt nu a fost gasit.
)

echo.
echo [3/4] Opresc toate procesele Python...

echo Opresc toate procesele python.exe...
taskkill /F /IM python.exe 2>nul
if not errorlevel 1 (
    echo Procesele python.exe au fost oprite.
) else (
    echo Nu am gasit procese python.exe de oprit.
)

echo Opresc toate procesele py.exe...
taskkill /F /IM py.exe 2>nul
if not errorlevel 1 (
    echo Procesele py.exe au fost oprite.
) else (
    echo Nu am gasit procese py.exe de oprit.
)

echo.
echo [4/4] Verificare finala...

tasklist /FI "IMAGENAME eq python.exe" 2>nul | find "python.exe" >nul
if errorlevel 1 (
    tasklist /FI "IMAGENAME eq py.exe" 2>nul | find "py.exe" >nul
    if errorlevel 1 (
        echo SUCCES! Nu mai ruleaza procese Python.
    ) else (
        echo ATENTIE: Inca mai ruleaza procese py.exe
    )
) else (
    echo ATENTIE: Inca mai ruleaza procese python.exe
)

echo.
echo ========================================
echo   Bot-ul FlowsyAI a fost oprit!
echo ========================================
echo.
echo Status: OPRIT
echo Locatie: %CD%
echo.
echo Pentru a porni din nou bot-ul: ruleaza start_bot.bat
echo Pentru a verifica status: ruleaza check_bot_status.bat
echo.
echo Fereastra se va inchide automat in 10 secunde...
timeout /t 10 /nobreak >nul
