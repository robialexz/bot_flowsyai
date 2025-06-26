@echo off
title FlowsyAI Bot Starter
color 0A

echo.
echo ========================================
echo        FlowsyAI Bot Starter
echo ========================================
echo.

cd /d "C:\Users\flowsyai\Desktop\Folder"

echo [1/6] Verificare fisiere necesare...
if not exist "main.py" (
    echo EROARE: main.py nu a fost gasit!
    pause
    exit /b 1
)

if not exist ".env" (
    echo EROARE: .env nu a fost gasit!
    echo Creaza fisierul .env cu token-urile necesare.
    pause
    exit /b 1
)

echo [2/6] Fisierele necesare au fost gasite.
echo.

echo [3/6] Opresc instante existente ale bot-ului...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM py.exe 2>nul
if exist "bot_pid.txt" del "bot_pid.txt"
echo Instante existente oprite.

echo.
echo [4/6] Verific mediul virtual...
if exist ".venv\Scripts\python.exe" (
    echo Mediul virtual gasit. Folosesc .venv\Scripts\python.exe
    set PYTHON_EXE=.venv\Scripts\python.exe
) else (
    echo ATENTIE: Mediul virtual nu a fost gasit. Folosesc Python global.
    set PYTHON_EXE=py
)

echo.
echo [5/6] Testez conectivitatea bot-ului...
%PYTHON_EXE% -c "import sys; print('Python version:', sys.version); import telegram; print('Telegram library OK')" 2>nul
if errorlevel 1 (
    echo EROARE: Dependentele nu sunt instalate corect!
    echo Ruleaza: %PYTHON_EXE% -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo [6/6] Pornesc bot-ul in fundal...
start /B %PYTHON_EXE% main.py

echo.
echo ========================================
echo   Bot-ul FlowsyAI ruleaza in fundal!
echo ========================================
echo.
echo Status: ACTIV si FUNCTIONAL
echo Python: %PYTHON_EXE%
echo Locatie: %CD%
echo.
echo Pentru a opri bot-ul: ruleaza stop_bot.bat
echo Pentru a verifica status: ruleaza check_bot_status.bat
echo.
echo SUCCES! Poti inchide aceasta fereastra acum.
echo Bot-ul va continua sa ruleze in fundal.
echo.
timeout /t 3 /nobreak >nul
echo Fereastra se va inchide automat in 10 secunde...
timeout /t 10 /nobreak >nul
