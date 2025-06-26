# FlowsyAI Bot Stopper Script
Write-Host "Opresc FlowsyAI Bot..." -ForegroundColor Yellow

$BotPath = "C:\Users\flowsyai\Desktop\Folder"
Set-Location $BotPath

# Citeste Process ID din fisier
if (Test-Path "bot_pid.txt") {
    $ProcessId = Get-Content "bot_pid.txt"
    Write-Host "Process ID gasit: $ProcessId" -ForegroundColor Cyan

    # Verifica daca procesul ruleaza
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $ProcessId -Force
        Write-Host "Bot-ul a fost oprit cu succes!" -ForegroundColor Green
        Remove-Item "bot_pid.txt" -ErrorAction SilentlyContinue
    } else {
        Write-Host "Procesul cu ID $ProcessId nu mai ruleaza." -ForegroundColor Yellow
        Remove-Item "bot_pid.txt" -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "Fisierul bot_pid.txt nu a fost gasit." -ForegroundColor Yellow
}

# Cauta si opreste toate procesele Python care ruleaza main.py
Write-Host "Caut alte procese Python care ruleaza bot-ul..." -ForegroundColor Cyan

$pythonProcesses = Get-WmiObject Win32_Process | Where-Object {
    $_.CommandLine -like "*python*main.py*" -or $_.CommandLine -like "*py*main.py*"
}

if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        Write-Host "Opresc procesul: $($proc.ProcessId)" -ForegroundColor Yellow
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Toate procesele bot-ului au fost oprite!" -ForegroundColor Green
} else {
    Write-Host "Nu am gasit procese Python care ruleaza bot-ul." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Bot-ul FlowsyAI a fost oprit complet!" -ForegroundColor Green
Write-Host ""
Read-Host "Apasa Enter pentru a inchide"
