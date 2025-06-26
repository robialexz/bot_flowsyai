@echo off
setlocal enabledelayedexpansion
title FlowsyAI Bot Status Checker
color 0B

echo.
echo ========================================
echo     FlowsyAI Bot Status Checker
========================================
echo.

cd /d "C:\Users\flowsyai\Desktop\Folder"

set BOT_RUNNING=0
set PID_VALID=0
set ZOMBIE_PID=0
set BOT_PID=

echo [1/4] Verific fisierul bot_pid.txt...

if exist "bot_pid.txt" (
    set /p BOT_PID=<bot_pid.txt
    echo Fisier PID gasit cu valoarea: !BOT_PID!
    
    REM Verifica daca procesul cu acest PID ruleaza
    tasklist /FI "PID eq !BOT_PID!" 2>nul | find "!BOT_PID!" >nul
    if not errorlevel 1 (
        echo Procesul cu PID !BOT_PID! RULEAZA.
        set BOT_RUNNING=1
        set PID_VALID=1
    ) else (
        echo ATENTIE: Procesul cu PID !BOT_PID! NU mai ruleaza!
        set ZOMBIE_PID=1
    )
) else (
    echo Fisierul bot_pid.txt NU EXISTA.
)

echo.
echo [2/4] Caut procese Python care ruleaza bot-ul...

set PYTHON_PROCESSES=0

REM Cauta procese python.exe
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find "python.exe" >nul
if not errorlevel 1 (
    echo Gasit procese python.exe active.
    set PYTHON_PROCESSES=1
)

REM Cauta procese py.exe
tasklist /FI "IMAGENAME eq py.exe" 2>nul | find "py.exe" >nul
if not errorlevel 1 (
    echo Gasit procese py.exe active.
    set PYTHON_PROCESSES=1
)

if !PYTHON_PROCESSES! == 0 (
    echo Nu am gasit procese Python active.
) else (
    echo Total procese Python gasite: DA
)

echo.
echo [3/4] Analiza status si curatenie...

REM Curata PID zombie
if !ZOMBIE_PID! == 1 (
    echo CURATENIE: Sterg fisierul bot_pid.txt cu PID zombie...
    del "bot_pid.txt" 2>nul
    if not errorlevel 1 (
        echo Fisierul bot_pid.txt zombie a fost sters.
    ) else (
        echo ATENTIE: Nu am putut sterge fisierul bot_pid.txt
    )
)

echo.
echo [4/4] RAPORT FINAL STATUS
echo ========================================

if !BOT_RUNNING! == 1 (
    echo STATUS: BOT ACTIV si FUNCTIONAL
    echo.
    echo Detalii proces:
    for /f "tokens=1,2,5" %%a in ('tasklist /FI "PID eq !BOT_PID!" /FO TABLE 2^>nul ^| find "!BOT_PID!"') do (
        echo   Nume proces: %%a
        echo   Process ID: %%b
        echo   Memorie: %%c
    )
    echo   Locatie: %CD%
    echo   Fisier PID: bot_pid.txt ^(VALID^)
    echo.
    echo ACTIUNI DISPONIBILE:
    echo   - Pentru a opri bot-ul: ruleaza stop_bot.bat
    echo   - Pentru a restarta: ruleaza stop_bot.bat apoi start_bot.bat
) else (
    if !PYTHON_PROCESSES! == 1 (
        echo STATUS: PROCESE PYTHON DETECTATE dar FARA PID VALID
        echo.
        echo ATENTIE: Exista procese Python active dar nu sunt
        echo          asociate cu un fisier PID valid pentru bot.
        echo          Acestea ar putea fi instante ale bot-ului
        echo          pornite manual sau procese Python diferite.
        echo.
        echo ACTIUNI RECOMANDATE:
        echo   - Ruleaza stop_bot.bat pentru a opri toate procesele
        echo   - Apoi ruleaza start_bot.bat pentru a porni corect bot-ul
    ) else (
        echo STATUS: BOT OPRIT
        echo.
        echo Nu ruleaza niciun proces Python asociat cu bot-ul.
        if !ZOMBIE_PID! == 1 (
            echo Fisierul PID zombie a fost curatat automat.
        )
        echo.
        echo ACTIUNI DISPONIBILE:
        echo   - Pentru a porni bot-ul: ruleaza start_bot.bat
    )
)

echo.
echo ========================================
echo COMENZI UTILE:
echo   start_bot.bat     - Porneste bot-ul
echo   stop_bot.bat      - Opreste bot-ul  
echo   check_bot_status.bat - Verifica status (acest script)
echo ========================================
echo.

if !BOT_RUNNING! == 1 (
    echo Bot-ul FlowsyAI RULEAZA si serveste comunitatea!
) else (
    echo Bot-ul FlowsyAI este OPRIT.
)

echo.
echo Fereastra se va inchide automat in 15 secunde...
echo Sau apasa orice tasta pentru a inchide acum.
timeout /t 15 /nobreak >nul
